# Модуль 01. Архитектура кластера

## Общее

Где бы ни работал кластер, компоненты одни и те же:

- **Control plane:** kube-apiserver, etcd, kube-controller-manager,
  kube-scheduler (и в облаках ещё cloud-controller-manager).
- **Worker-нода:** kubelet, kube-proxy, container runtime (containerd).
- Объекты API (Pod, Deployment, Service и так далее) и их поведение
  одинаковы.

### Практика на kind

```bash
kubectl get pods -n kube-system -o wide        # компоненты control plane — это поды
kubectl describe node eks-lab-worker           # версия kubelet, capacity, allocatable
docker exec eks-lab-control-plane ls /etc/kubernetes/manifests   # static pod'ы control plane
docker exec eks-lab-control-plane crictl ps                       # контейнеры внутри «ноды»
```

Старая команда `kubectl get componentstatuses` объявлена устаревшей и может
не показывать ничего полезного. Смотрите поды в `kube-system`.

Задеплойте приложение и посмотрите, как scheduler раскидал поды:

```bash
kubectl create deployment nginx --image=nginx --replicas=3
kubectl get pods -o wide
```

## В EKS

- **Control plane управляется AWS.** API server и etcd работают у AWS в
  отдельном аккаунте, в нескольких зонах доступности (AZ).[3] Вы за них не
  отвечаете, но и не видите их как EC2. В вашей VPC для связи появляются
  сетевые интерфейсы (ENI), через которые ноды ходят к API.
- **Доступ к API server** настраивается: публичный endpoint, приватный или
  оба.[4] Это AWS-настройка кластера, в kind такого понятия нет.
- **Варианты worker-нод.** В vanilla Kubernetes ноды вы создаёте сами. В EKS
  есть несколько способов получить вычислительные мощности:
  - *Managed node group*: EC2 в Auto Scaling Group, жизненным циклом
    (обновление AMI, drain при замене) управляет AWS.
  - *Self-managed nodes*: вы сами создаёте ASG и AMI. Это ближе всего к
    kubeadm.
  - *Karpenter*: ноды создаются под конкретные поды без заранее заданных
    групп (модуль 06).
  - *Fargate*: нод для вас нет, у каждого пода своя микро-VM (модуль 10).
  - *EKS Auto Mode*: AWS сама ведёт и ноды, и базовые компоненты
    (модуль 11).
  - *Hybrid Nodes*: ваши собственные серверы вне AWS подключаются к
    EKS control plane.[3]
- **Версии и обновления.** Control plane и ноды обновляются раздельно через
  AWS API, а не через `kubeadm upgrade` (модуль 09).
- **SSH на control plane нет в принципе.** На ноды в Auto Mode SSH тоже
  отключён.

## Частые ошибки

- Ждать, что `kubectl get nodes` покажет control plane EKS. Не покажет: он
  не входит в список нод.
- Считать, что ноды обновляются вместе с control plane автоматически.
  В managed node group это отдельная операция.

## Проверка себя

- Какие компоненты control plane вы не увидите как EC2-инстансы в EKS?
  *(Все: kube-apiserver, etcd, controller-manager и scheduler полностью
  на стороне AWS.)*
- Назовите три способа получить worker-ноды в EKS. *(Managed node group,
  self-managed, Fargate; плюс Karpenter и Auto Mode.)*

## Источники главы

- [3] Amazon EKS architecture — https://docs.aws.amazon.com/eks/latest/userguide/eks-architecture.html
- [4] Cluster API server endpoint — https://docs.aws.amazon.com/eks/latest/userguide/cluster-endpoint.html
