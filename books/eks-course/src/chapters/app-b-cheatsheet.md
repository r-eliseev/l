# Приложение Б. Шпаргалка: vanilla Kubernetes против EKS

Для каждой темы: сначала kind/vanilla, затем EKS.

## Кластер и доступ

- **Control plane.** kind: контейнеры, в них можно зайти. EKS: скрыт,
  управляется AWS ($0.10 в час за кластер).
- **Создание.** kind: `kind create cluster`. EKS: eksctl, Terraform, консоль.
- **Вход.** kind: сертификат в kubeconfig. EKS: IAM и access entries
  (`aws eks update-kubeconfig`).
- **Ноды.** kind: контейнеры Docker. EKS: managed или self-managed node
  groups, Karpenter, Fargate, Auto Mode.

## Сеть и балансировщики

- **Сеть подов.** kind: kindnet (или Calico/Cilium). EKS: VPC CNI, IP из
  подсетей VPC.
- **Лимит подов на ноду.** kind: около 110. EKS: зависит от типа EC2
  (ENI × IP), prefix delegation увеличивает.
- **NetworkPolicy.** kind: зависит от CNI. EKS: включить
  `enableNetworkPolicy` в VPC CNI или поставить Calico/Cilium.
- **Service LoadBalancer.** kind: pending (нужен cloud-provider-kind). EKS:
  NLB с AWS Load Balancer Controller, Classic LB без него.
- **Ingress.** kind: свой контроллер. EKS: ALB через AWS Load Balancer
  Controller.

## Хранилище и доступ подов к AWS

- **Хранилище.** kind: local-path-provisioner. EKS: EBS CSI (RWO, привязан к
  AZ) и EFS CSI (RWX); драйвер ставить самим, кроме Auto Mode.
- **IAM для подов.** kind: нет. EKS: IRSA или Pod Identity (на Fargate
  только IRSA).

## Масштабирование и эксплуатация

- **Автоскейлинг нод.** kind: нет. EKS: Cluster Autoscaler, Karpenter,
  Auto Mode.
- **Add-ons.** kind: Helm/manifest. EKS: EKS Add-ons API (можно и Helm).
- **Логи control plane.** kind: audit не включён по умолчанию. EKS:
  CloudWatch, пять типов, по умолчанию выключены.
- **Обновление.** kind: пересоздать кластер. EKS: `update-cluster-version`,
  потом add-ons, потом ноды.
- **Поддержка версии.** EKS: 14 месяцев стандартной плюс 12 месяцев
  extended ($0.60 в час вместо $0.10).

## Fargate

- kind: нет. EKS: поды в микро-VM, без DaemonSet, EBS, hostNetwork и GPU.
