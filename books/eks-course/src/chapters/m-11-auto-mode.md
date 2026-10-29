# Модуль 11. EKS Auto Mode

## Общее

В обычном Kubernetes кластер — это ваша ответственность: control plane,
ноды, CNI, DNS, драйверы хранилища, балансировщики. Auto Mode — это вариант
EKS, где AWS берёт на себя ещё и «рабочую» часть.

## В EKS: что делает Auto Mode

- **Ноды.** Внутри работает Karpenter, которым управляет AWS. Он добавляет
  ноды под Pending-поды и убирает ненужные.[30] Группы нод создавать не нужно.
- **Базовые компоненты встроены:** сеть подов, DNS, драйвер EBS, управление
  балансировщиками.[30] Ставить `vpc-cni`, `coredns`, `kube-proxy`, EBS CSI,
  Pod Identity agent и AWS Load Balancer Controller **не нужно**.
- **Ноды неизменяемые.** Они работают на Bottlerocket с защищёнными
  настройками, **без SSH и SSM**[30]. Максимальное время жизни ноды — 21 день,
  после чего её заменяют (с учётом PDB).[30] Это обновление «из коробки».
- **Свои настройки.** Встроенные NodePool и NodeClass не редактируют. Нужен
  особый тип инстансов, Spot или GPU — создаёте свои NodePool и NodeClass.
- **Что меняется в именах.** StorageClass должен использовать provisioner
  `ebs.csi.eks.amazonaws.com` (вместо `ebs.csi.aws.com`)[9], а Ingress и Service
  обрабатываются встроенным контроллером. Перенос существующих EBS-томов
  требует снапшотов.
- **Деньги.** Кроме EC2 вы платите отдельную плату Auto Mode за каждый
  запущенный инстанс (посекундно, минимум одна минута).[1] Цены смотрите на
  странице EKS pricing.
- **Включение:** при создании кластера (консоль, eksctl, Terraform) или на
  существующем кластере. В свежих версиях eksctl это флаг
  `--enable-auto-mode` или секция `autoModeConfig` в конфиге.

## Как выбирать

- **Минимум администрирования, стандартные нагрузки:** Auto Mode.
- **Полный контроль над нодами и AMI, привилегированные DaemonSet:** managed
  node groups или Karpenter.
- **Поды без нод, редкие короткие задачи:** Fargate.
- **Свои серверы вне AWS:** Hybrid Nodes.

## Практика

На kind такого не воспроизвести. Упражнение на бумаге: возьмите кластер из
модулей 02–09 и выпишите, какие компоненты и операции (add-ons, обновления
нод, LBC, драйвер EBS) Auto Mode делает за вас, а за какие вы всё равно
отвечаете (манифесты, PDB, requests, IAM для приложений, стоимость).

## Частые ошибки

- Ждать SSH на ноды для отладки. Используйте `kubectl debug`, логи и
  метрики.
- Менять встроенные NodePool вместо создания своих.
- Использовать старый provisioner EBS в StorageClass.

## Проверка себя

- Что вы больше не ставите сами в Auto Mode? *(CNI, DNS, kube-proxy, драйвер
  EBS, LBC, Pod Identity agent.)*
- Почему в Auto Mode нельзя «зайти на ноду»? *(Ноды неизменяемые, SSH и SSM
  отключены.)*
- Через сколько заменяется нода? *(Максимум 21 день.)*

## Источники главы

- [1] Amazon EKS Pricing — https://aws.amazon.com/eks/pricing/
- [9] Set up the Amazon EBS CSI driver — https://docs.aws.amazon.com/eks/latest/userguide/ebs-csi.html
- [30] Automate cluster infrastructure with EKS Auto Mode — https://docs.aws.amazon.com/eks/latest/userguide/automode.html
