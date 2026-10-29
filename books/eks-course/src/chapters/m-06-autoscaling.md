# Модуль 06. Автоскейлинг

## Общее

- **HPA (Horizontal Pod Autoscaler)** меняет число реплик по метрикам (CPU,
  память, кастомные). Ему нужен **metrics-server**, и у подов должны быть
  заданы `resources.requests`. Без requests процент загрузки посчитать не от
  чего, и HPA покажет `<unknown>`.
- **VPA (Vertical Pod Autoscaler)** подбирает requests и limits. Это
  отдельный компонент, он не встроен в Kubernetes.

### Практика на kind

```bash
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
helm install metrics-server metrics-server/metrics-server -n kube-system
# в kind kubelet использует самоподписанные сертификаты, поэтому:
kubectl -n kube-system patch deployment metrics-server --type=json \
  -p '[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'

kubectl create deployment nginx --image=nginx
kubectl set resources deployment nginx --requests=cpu=50m --limits=cpu=200m
kubectl autoscale deployment nginx --cpu-percent=50 --min=1 --max=5
kubectl top pods && kubectl get hpa
```

Дайте нагрузку (`kubectl run load --rm -it --image=busybox -- sh -c "while true; do wget -q -O- http://nginx; done"`)
и посмотрите, как растёт число реплик: `kubectl get hpa -w`.

В kind HPA двигает поды между **существующими** нодами. Добавить ноду kind
сам не может: облака, которое выдаст машину, нет.

## В EKS

Разница в том, что можно масштабировать и **ноды**.

- **Cluster Autoscaler (CA).** Следит за подами в `Pending` из-за нехватки
  места и увеличивает размер Auto Scaling Group.[16] Недогруженные ноды
  убирает. Работает в рамках уже созданных node groups с заданными типами
  инстансов. Группы нужно пометить тегами
  `k8s.io/cluster-autoscaler/enabled` и `k8s.io/cluster-autoscaler/<кластер>`.[18]
- **Karpenter.** Не использует заранее заданные группы. Видит Pending-поды,
  сам подбирает подходящий тип и размер EC2 и запускает его напрямую через
  EC2 API.[16] Обычно работает быстрее и экономнее CA, умеет уплотнять и
  заменять ноды. Настраивается двумя объектами: `NodePool` (какие ноды
  допустимы)[17] и `EC2NodeClass` (как их создавать: AMI, подсети, роль).

```yaml
apiVersion: karpenter.sh/v1
kind: NodePool
metadata: { name: default }
spec:
  template:
    spec:
      nodeClassRef: { group: karpenter.k8s.aws, kind: EC2NodeClass, name: default }
      requirements:
        - { key: karpenter.sh/capacity-type, operator: In, values: ["on-demand"] }
        - { key: kubernetes.io/arch, operator: In, values: ["amd64"] }
  limits: { cpu: "100" }
  disruption: { consolidationPolicy: WhenEmptyOrUnderutilized, consolidateAfter: 1m }
---
apiVersion: karpenter.k8s.aws/v1
kind: EC2NodeClass
metadata: { name: default }
spec:
  role: KarpenterNodeRole-my-cluster
  amiSelectorTerms: [{ alias: "al2023@latest" }]
  subnetSelectorTerms: [{ tags: { karpenter.sh/discovery: my-cluster } }]
  securityGroupSelectorTerms: [{ tags: { karpenter.sh/discovery: my-cluster } }]
```

  Сам Karpenter работает как под, поэтому ему нужно место, где он живёт
  (небольшая managed node group или Fargate), и IAM-права на создание EC2.
- **EKS Auto Mode** содержит управляемую версию такой логики: AWS сама
  добавляет и убирает ноды (модуль 11), настраивать Karpenter не нужно.
- **Fargate:** поды получают свои микро-VM по требованию, и ни CA, ни
  Karpenter для них не нужны. HPA при этом работает как обычно.
- **Ограничения:** в EKS число подов на ноду зависит от типа инстанса
  (модуль 02), поэтому выбор типов влияет на то, сколько нод понадобится.
- **Для практики без AWS** у Karpenter есть KWOK-провайдер, который
  имитирует ноды. Проверьте актуальность в документации проекта.

## Частые ошибки

- HPA показывает `<unknown>`: не установлен metrics-server или у пода нет
  requests.
- В kind metrics-server не стартует из-за TLS: нужен флаг
  `--kubelet-insecure-tls` (только для учёбы).
- Ждать от Cluster Autoscaler, что он выберет тип инстанса. Он этого не
  делает, тип задан в группе.

## Проверка себя

- В чём принципиальная разница между CA и Karpenter? *(CA меняет размер
  существующих ASG с фиксированными типами; Karpenter сам подбирает тип и
  размер EC2 под Pending-поды.)*
- Почему HPA и добавление нод — разные уровни? *(HPA меняет число подов;
  ноды добавляет CA, Karpenter или Auto Mode.)*

## Источники главы

- [16] Scale cluster compute with Karpenter and Cluster Autoscaler — https://docs.aws.amazon.com/eks/latest/userguide/autoscaling.html
- [17] Karpenter (Best Practices) — https://docs.aws.amazon.com/eks/latest/best-practices/karpenter.html
- [18] Auto Scaling (eksctl) — https://docs.aws.amazon.com/eks/latest/eksctl/autoscaling.html
