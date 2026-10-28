# Приложение А. Короткая практика на реальном EKS

Цель: за 1–2 часа проверить главное из курса на настоящем кластере и
**гарантированно всё удалить**.

## Что понадобится

- аккаунт AWS и настроенный `aws configure` (лучше отдельный пользователь
  или роль для экспериментов);
- `eksctl` (инструкция на eksctl.io);
- kubectl и Helm из модуля 00.

## Стоимость

Платите за control plane ($0.10 в час), EC2-ноды, NAT gateway, балансировщики и
EBS-тома. Двухчасовой эксперимент обычно стоит несколько долларов, но
забытый кластер стоит дорого. Поставьте напоминание удалить.

## Создание кластера

```yaml
# eks-lab.yaml
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig
metadata:
  name: eks-lab
  region: eu-central-1
  version: "1.36"          # выберите из: aws eks describe-cluster-versions
iam:
  withOIDC: true           # IRSA (модуль 04)
managedNodeGroups:
  - name: workers
    instanceType: t3.medium
    desiredCapacity: 2
    minSize: 2
    maxSize: 3
```

```bash
eksctl create cluster -f eks-lab.yaml     # 15-20 минут
kubectl get nodes
```

## Что стоит проверить (по модулям)

1. **01/02:** `kubectl get pods -A -o wide` — IP подов из диапазона вашей VPC.
   `kubectl -n kube-system get ds aws-node`.
2. **03:** поставьте add-on `aws-ebs-csi-driver`, создайте PVC и под, найдите
   созданный том в EC2 → Volumes.
3. **04:** создайте ServiceAccount с ролью через IRSA и запустите под с
   `aws s3 ls`.
4. **05:** поставьте AWS Load Balancer Controller, создайте Ingress и
   посмотрите ALB в консоли.
5. **07/08:** `aws eks list-addons`; включите логи `authenticator` и найдите
   их в CloudWatch.
6. **09:** создайте PDB и обновите node group, посмотрите на drain.

## Удаление (обязательно)

Порядок важен: сначала удалите то, что создало внешние ресурсы.

```bash
kubectl delete ingress,svc --all -A      # осторожно: удалит ваши Service и Ingress; в учебном кластере это нормально
kubectl delete pvc --all -A
eksctl delete cluster -f eks-lab.yaml
```

Затем проверьте в консоли AWS, что не осталось:

- балансировщиков (EC2 → Load Balancers);
- томов EBS (EC2 → Volumes);
- NAT gateway и Elastic IP;
- групп логов CloudWatch (`/aws/eks/eks-lab/cluster`);
- IAM-ролей, созданных для IRSA.
