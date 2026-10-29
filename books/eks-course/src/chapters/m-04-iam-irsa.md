# Модуль 04. IAM, IRSA, Pod Identity и доступ к кластеру

## Общее

- **ServiceAccount** — идентичность пода внутри кластера.
- **RBAC** (Role, RoleBinding, ClusterRole, ClusterRoleBinding) — кому что
  разрешено в Kubernetes API. Работает одинаково везде.

### Практика на kind

```bash
kubectl create serviceaccount demo-sa
kubectl create role pod-reader --verb=get,list --resource=pods
kubectl create rolebinding demo-binding --role=pod-reader --serviceaccount=default:demo-sa

# проверить права без запуска пода
kubectl auth can-i list pods   --as=system:serviceaccount:default:demo-sa   # yes
kubectl auth can-i delete pods --as=system:serviceaccount:default:demo-sa   # no
```

## В EKS: два разных вопроса про доступ

В EKS есть две независимые темы, которые легко перепутать:

1. **Как под получает доступ к сервисам AWS** (S3, DynamoDB, SQS...). Это IRSA
   или Pod Identity.
2. **Как человек или CI получает доступ к самому Kubernetes API.** Это access
   entries.

### 1. Доступ подов к AWS

**Проблема.** Приложению в поде нужно в S3. Ключи в Secret плохи: их надо
хранить и ротировать. Роль ноды (instance profile) тоже плоха: все поды на
ноде получают одни и те же права.

#### IRSA (IAM Roles for Service Accounts)

Связывает конкретный ServiceAccount с конкретной IAM-ролью через OIDC:

1. У каждого EKS-кластера есть собственный OIDC-издатель токенов. Но в IAM его
   нужно **зарегистрировать вручную, один раз на кластер**[11]:
   `eksctl utils associate-iam-oidc-provider --cluster my-cluster --approve`.
   Автоматически этого не происходит.
2. Создаётся IAM-роль, в trust policy которой указан этот OIDC-провайдер и
   условия на ServiceAccount:

```json
{
  "Effect": "Allow",
  "Principal": { "Federated": "arn:aws:iam::123456789012:oidc-provider/oidc.eks.eu-central-1.amazonaws.com/id/EXAMPLE" },
  "Action": "sts:AssumeRoleWithWebIdentity",
  "Condition": { "StringEquals": {
    "oidc.eks.eu-central-1.amazonaws.com/id/EXAMPLE:sub": "system:serviceaccount:default:demo-sa",
    "oidc.eks.eu-central-1.amazonaws.com/id/EXAMPLE:aud": "sts.amazonaws.com" } }
}
```

3. ServiceAccount аннотируется ARN роли:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: demo-sa
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789012:role/demo-role
```

4. Webhook в кластере при создании пода добавляет переменные `AWS_ROLE_ARN` и
   `AWS_WEB_IDENTITY_TOKEN_FILE` и монтирует токен. AWS SDK сам обменивает
   токен на временные ключи роли. В коде приложения ключей нет.

#### EKS Pod Identity

Более новый способ, который не заменяет IRSA, а работает рядом с ним.

- Ставится add-on `eks-pod-identity-agent`: DaemonSet, который выдаёт
  credentials подам своей ноды.
- Связь создаётся одной командой, без OIDC-провайдера и без аннотаций:

```bash
aws eks create-pod-identity-association --cluster-name my-cluster \
  --namespace default --service-account demo-sa \
  --role-arn arn:aws:iam::123456789012:role/demo-role
```

- В trust policy роли указывается сервис `pods.eks.amazonaws.com`, поэтому
  одну роль удобно использовать в нескольких кластерах.[12]
- **Ограничения:** только Linux-ноды на EC2. **На Fargate не работает**, там
  используйте IRSA.[12] Нельзя указать роль из другого аккаунта (для этого
  цепочка ролей).
- В EKS Auto Mode агент ставить не нужно.

**Что выбрать:** для новых нагрузок на EC2-нодах Pod Identity проще. IRSA
нужен для Fargate и если уже используется.

#### Как потренироваться без EKS

Полноценно IRSA в kind не воспроизвести (нужен настоящий OIDC-издатель
AWS). Можно: разобрать trust policy на бумаге, а с LocalStack попробовать
создавать роли и политики (привязки к поду не будет).

### 2. Доступ людей и CI к кластеру

В EKS вы входите в кластер **IAM-идентичностью** (пользователь или роль), а не
сертификатом. Как IAM-идентичность превращается в права Kubernetes:

- **Access entries** — современный способ. Вы создаёте запись для IAM-роли и
  выдаёте ей готовую политику доступа или привязываете к группе RBAC:

```bash
aws eks create-access-entry --cluster-name my-cluster \
  --principal-arn arn:aws:iam::123456789012:role/DevRole
aws eks associate-access-policy --cluster-name my-cluster \
  --principal-arn arn:aws:iam::123456789012:role/DevRole \
  --policy-arn arn:aws:eks::aws:cluster-access-policy/AmazonEKSViewPolicy \
  --access-scope type=namespace,namespaces=dev
```

- **ConfigMap `aws-auth`** — старый способ (запись в `kube-system`). Он
  считается устаревшим, новые кластеры лучше вести через access entries.
  Режимы аутентификации кластера: `CONFIG_MAP`, `API_AND_CONFIG_MAP`, `API`.
  Переход к режиму API односторонний.[13] Проверьте режим своего кластера в
  консоли или `aws eks describe-cluster`.
- Тот, кто **создал** кластер, получает администраторский доступ. Если эту
  роль потом удалят, вы можете остаться без доступа. Заведите отдельный
  административный access entry.

## Частые ошибки

- Забыть создать OIDC-провайдер в IAM и получить `InvalidIdentityToken` или
  `AssumeRoleWithWebIdentity` в ошибках.
- Опечататься в `sub` в trust policy (namespace и имя ServiceAccount).
  Роль не сработает.
- Ждать Pod Identity на Fargate.
- Думать, что RBAC в Kubernetes и IAM — это одно и то же. Это два разных
  уровня авторизации.

## Проверка себя

- Почему instance profile плохая замена IRSA? *(Все поды на ноде получают
  одни и те же права, изоляции по приложению нет.)*
- Что нужно сделать один раз на кластер для IRSA? *(Зарегистрировать OIDC
  в IAM.)*
- Где не работает Pod Identity? *(На Fargate и Windows-нодах.)*
- Что такое access entry? *(Запись, которая связывает IAM-роль с правами в
  Kubernetes API.)*

## Источники главы

- [11] IAM roles for service accounts — https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html
- [12] EKS Pod Identity — https://docs.aws.amazon.com/eks/latest/userguide/pod-identities.html
- [13] Grant IAM users and roles access to Kubernetes APIs — https://docs.aws.amazon.com/eks/latest/userguide/grant-k8s-access.html
