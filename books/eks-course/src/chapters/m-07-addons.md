# Модуль 07. Аддоны

## Общее

Базовые компоненты кластера одни и те же:

- **CoreDNS** — DNS внутри кластера.
- **kube-proxy** — реализация Service на нодах (iptables или IPVS).
- **metrics-server** — метрики для HPA и `kubectl top`.

```bash
kubectl get pods -n kube-system
kubectl get configmap coredns -n kube-system -o yaml
```

В kind CoreDNS и kube-proxy ставит сам kubeadm при создании кластера. Их не
устанавливают чартом. Остальное (например, metrics-server) вы добавляете
сами, версию и настройки контролируете целиком:

```bash
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
helm install metrics-server metrics-server/metrics-server -n kube-system
```

## В EKS

- **EKS Add-ons** — AWS-способ управлять компонентами. Это те же самые
  CoreDNS, kube-proxy и так далее, но версией, совместимостью с версией
  кластера и обновлениями управляет AWS через свой API.

```bash
aws eks describe-addon-versions --addon-name coredns --kubernetes-version 1.36
aws eks create-addon --cluster-name my-cluster --addon-name coredns
aws eks update-addon --cluster-name my-cluster --addon-name coredns \
  --addon-version <версия> --resolve-conflicts PRESERVE
aws eks describe-addon --cluster-name my-cluster --addon-name coredns
```

- **Что стоит в новом кластере сразу:** `vpc-cni`, `coredns` и `kube-proxy`
  появляются при создании кластера. Если вы их не «усыновили» как managed
  add-ons, их обновляете вы сами.
- **Параметр `--resolve-conflicts`** решает, что делать, если вы ранее
  вручную меняли настройки компонента: `OVERWRITE` затрёт ваши изменения,
  `PRESERVE` сохранит.
- **Каталог add-ons шире, чем три базовых.** Среди них: драйверы хранилища
  `aws-ebs-csi-driver`, `aws-efs-csi-driver`, `snapshot-controller`;
  `eks-pod-identity-agent` (модуль 04); `amazon-cloudwatch-observability` и
  `adot` (модуль 08); агент GuardDuty; Secrets Store CSI provider. Актуальный
  список смотрите командой `aws eks describe-addon-versions`.
- **metrics-server** нужно ставить отдельно (Helm или манифест), если вы не
  нашли его в каталоге своей версии. Проверьте актуальный каталог.
- **Некоторым add-ons нужна IAM-роль** (например, EBS CSI). Её передают в
  `--service-account-role-arn` или привязывают через Pod Identity.
- **Это необязательный слой.** Можно по-прежнему ставить всё через Helm или
  kubectl (self-managed). Add-ons — удобство, а не новый компонент.
- **В EKS Auto Mode** vpc-cni, coredns, kube-proxy, EBS CSI, Pod Identity
  agent и LBC ставить не нужно: они встроены (модуль 11).

## Частые ошибки

- Обновить control plane и забыть обновить add-ons. Версии должны
  соответствовать кластеру.
- Затереть свои настройки CoreDNS, выбрав `OVERWRITE`.
- Ставить в kind `helm install` без `helm repo add`: репозиторий нужно
  добавить заранее.

## Проверка себя

- EKS Add-on для CoreDNS — это другой DNS-сервер? *(Нет, тот же CoreDNS.
  Версия и жизненный цикл управляются через AWS API.)*
- Какие add-ons есть в новом кластере без вашего участия? *(vpc-cni,
  coredns, kube-proxy.)*
