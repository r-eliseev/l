# Модуль 00. Подготовка

## Общее

Ставим три инструмента, которые нужны во всех модулях:

- **kind** запускает настоящий upstream Kubernetes в Docker-контейнерах.
  Каждая «нода» — это контейнер. API и поведение объектов те же, что в EKS
  (EKS основан на upstream-версии; AWS публикует его как EKS Distro).
- **kubectl** — тот же CLI и тот же API, что для EKS.
- **Helm** ставит чарты и одинаково работает против любого кластера.

### Установка (Amazon Linux 2023, x86_64)

```bash
# Docker
sudo dnf install -y docker
sudo systemctl enable --now docker
sudo usermod -aG docker $USER   # затем перелогиньтесь (или: newgrp docker)

# kubectl (последняя стабильная версия)
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl && sudo mv kubectl /usr/local/bin/

# kind (на момент написания — v0.33.0, проверьте последнюю на странице релизов)
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.33.0/kind-linux-amd64
chmod +x ./kind && sudo mv ./kind /usr/local/bin/kind

# Helm: инструкция на https://helm.sh/docs/intro/install/
# (чарты из курса работают и в Helm 3, и в Helm 4)
```

Если у вас ARM-машина (Graviton, Apple Silicon), в именах файлов вместо
`amd64` будет `arm64`. Проверить архитектуру можно командой `uname -m`.

### Многонодовый кластер

```yaml
# kind-config.yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
  - role: worker
  - role: worker
```

```bash
kind create cluster --name eks-lab --config kind-config.yaml
kubectl cluster-info --context kind-eks-lab
kubectl get nodes
docker ps          # три контейнера: это и есть ваши «ноды»
```

Вы увидите control-plane и два worker-узла. Концептуально это то же, что
control plane EKS плюс node group, только всё в контейнерах на одной машине.

Удалить кластер: `kind delete cluster --name eks-lab`.

## В EKS

- **Control plane управляется AWS.** Вы не видите и не администрируете машины
  с API server и etcd. В kind `docker ps` показывает контейнер control-plane,
  и в него можно зайти.
- **Кластер создаётся через AWS**, а не конфиг-файлом для локального
  инструмента: `eksctl`, Terraform/CloudFormation, консоль. Под капотом
  реальные ресурсы: VPC, подсети, IAM-роли, security groups, EC2.
- **Доступ к кластеру идёт через AWS CLI.** Команда
  `aws eks update-kubeconfig --name <кластер>` прописывает в kubeconfig
  вызов `aws eks get-token`. Вы заходите по IAM-идентичности (подробнее в
  модуле 04), а не по сертификату, как в kind.
- **Кластер платный сам по себе.** Control plane стоит $0.10 в час за
  кластер (стандартная поддержка), в extended support — $0.60 в час. Цена
  не зависит от того, что в кластере крутится. Ноды, балансировщики, диски и
  NAT gateway оплачиваются отдельно.

## Частые ошибки

- `permission denied` при `docker ps` значит, что вы не перелогинились после
  `usermod`.
- kind и 3 ноды на слабой машине могут не хватать памяти. Начните с одного
  worker.
- Если kubectl «ходит» не в тот кластер, посмотрите `kubectl config
  current-context`. Привыкайте проверять контекст, когда у вас рядом kind и
  реальный EKS.

## Проверка себя

- Чем kind-кластер отличается от обычного kubeadm-кластера на VM?
  *(Концептуально ничем: kind запускает ноды в Docker вместо VM, API
  тот же.)*
- Почему нельзя «зайти на master-ноду» в EKS?
  *(Control plane скрыт и управляется AWS. Вы работаете только через API
  Kubernetes и AWS API.)*
