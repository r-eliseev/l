# Модуль 08. Наблюдаемость

## Общее

Стек мониторинга и его идеи одинаковы:

- **Prometheus** собирает метрики с подов и нод.
- **Grafana** показывает графики.
- `kubectl logs` и `kubectl top` — базовая диагностика. Для `kubectl top`
  нужен metrics-server (модули 06 и 07).

### Практика на kind

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install monitoring prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace
kubectl -n monitoring port-forward svc/monitoring-grafana 3000:80
kubectl logs deployment/nginx
kubectl top pods
```

Стек `kube-prometheus-stack` тяжёлый. Если kind работает на небольшой машине,
дайте ей хотя бы несколько гигабайт памяти или используйте облегчённые
варианты.

**Логи control plane в kind.** Компоненты — обычные поды, их логи читаются
так: `kubectl -n kube-system logs kube-apiserver-eks-lab-control-plane`.
Команда `docker logs eks-lab-control-plane` покажет логи самого контейнера
ноды (systemd, containerd), а не API server. **Audit-лог в kind по умолчанию
не включён**: его настраивают через политику аудита и параметры API server в
конфиге кластера (смотрите раздел про аудит в документации kind).

## В EKS

Разница в том, что происходит с логами **control plane**, который вы не
видите как машины.

- **Control plane logging в CloudWatch.** Включается отдельно по типам,
  **по умолчанию выключено**. Типов пять: `api`, `audit`, `authenticator`,
  `controllerManager`, `scheduler`. Логи попадают в группу
  `/aws/eks/<кластер>/cluster`.

```bash
aws eks update-cluster-config --name my-cluster --logging \
  '{"clusterLogging":[{"types":["api","audit","authenticator","controllerManager","scheduler"],"enabled":true}]}'
```

  Особо полезен `authenticator`: он показывает, какая IAM-идентичность
  пришла в кластер (модуль 04). Включённые логи оплачиваются как обычные
  данные CloudWatch Logs.
- **CloudWatch Container Insights** (add-on `amazon-cloudwatch-observability`)
  собирает метрики и логи подов в CloudWatch. Это управляемая альтернатива
  Prometheus или дополнение к нему.
- **Managed-сервисы.** Amazon Managed Service for Prometheus и Amazon
  Managed Grafana дают Prometheus и Grafana без администрирования. Сбор
  метрик можно делать через add-on ADOT (OpenTelemetry).
- **Логи подов на Fargate** собирает встроенный log router: его настраивают
  ConfigMap в специальном namespace `aws-observability`. DaemonSet для
  сбора логов на Fargate запустить нельзя (модуль 10).
- **VPC Flow Logs** показывают сетевой трафик на уровне интерфейсов VPC.
  Это работает, потому что у подов реальные адреса VPC (модуль 02).
- **Деньги.** Хранение и приём логов в CloudWatch платные. В kind метрики и
  логи бесплатны (и пропадают вместе с кластером).

## Частые ошибки

- Сначала разбираться с проблемой доступа, а потом вспомнить, что логи
  `authenticator` не включены.
- Включить все типы логов на тестовом кластере и забыть. Копится счёт.
- В kind искать audit-лог, которого нет.

## Проверка себя

- Почему audit-логи control plane в EKS нужно включать явно? *(Control
  plane скрыт от вас, доступ к его логам возможен только через настроенную
  выгрузку в CloudWatch.)*
- Какой тип лога поможет понять, кто пришёл в кластер по IAM?
  *(`authenticator`.)*
- Как собирать логи подов на Fargate? *(Встроенный log router через
  ConfigMap в `aws-observability`, либо sidecar.)*
