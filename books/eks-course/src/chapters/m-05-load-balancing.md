# Модуль 05. Балансировщики и Ingress

## Общее

API-объекты одинаковы везде:

- **Service type=LoadBalancer** — запрос на внешний балансировщик.
- **Ingress** (и более новый **Gateway API**) — маршрутизация по host/path к
  нескольким Service. Сам по себе объект ничего не делает: нужен контроллер,
  который его исполняет.

### Практика на kind

В kind нет облака, поэтому `type=LoadBalancer` сам по себе не получит адрес:

```bash
kubectl create deployment nginx --image=nginx
kubectl expose deployment nginx --port=80 --type=LoadBalancer
kubectl get svc nginx        # EXTERNAL-IP: <pending>
```

Три способа это обойти:

1. **port-forward** для быстрой проверки: `kubectl port-forward svc/nginx 8080:80`.
2. **NodePort плюс проброс порта из контейнера ноды.** Порт нужно описать в
   конфиге кластера и использовать его в Service:

```yaml
# kind-config.yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
    extraPortMappings:
      - containerPort: 30080
        hostPort: 8080
  - role: worker
```

```yaml
# svc-nodeport.yaml
apiVersion: v1
kind: Service
metadata: { name: nginx-np }
spec:
  type: NodePort
  selector: { app: nginx }
  ports:
    - port: 80
      targetPort: 80
      nodePort: 30080
```

```bash
kubectl apply -f svc-nodeport.yaml
curl localhost:8080
```

3. **cloud-provider-kind** — отдельная утилита проекта kubernetes-sigs. Она
   выдаёт `LoadBalancer`-сервисам в kind реальные адреса. Это самый близкий
   к облаку вариант (инструкция в репозитории проекта).

Для Ingress в kind берите контроллер, который сейчас поддерживается. Проект
ingress-nginx объявлен выводимым из поддержки (с марта 2026), поэтому для
новых лабораторных лучше реализации Gateway API (например, Envoy Gateway) или
Traefik. Проверьте актуальное состояние проектов.

## В EKS

**Главное: за балансировщики отвечает отдельный компонент, и от него зависит,
что именно создастся.**

- **Если AWS Load Balancer Controller (LBC) не установлен**, Kubernetes
  использует встроенный устаревший провайдер и для `type=LoadBalancer`
  создаёт **Classic Load Balancer**. Это не то, что обычно нужно.
- **Если LBC установлен** (версии 2.5 и новее), он по умолчанию делает для
  `type=LoadBalancer` **Network Load Balancer (NLB)**, а для **Ingress**
  создаёт **Application Load Balancer (ALB)**. Версии 2.14 и новее умеют
  Gateway API. Контроллер ставится отдельно, обычно Helm-чартом, и ему нужна
  IAM-роль (IRSA или Pod Identity, модуль 04).
- **Подсети должны быть размечены тегами**: `kubernetes.io/role/elb=1` для
  публичных и `kubernetes.io/role/internal-elb=1` для приватных. Без тегов
  балансировщик не найдёт, где ему создаваться.
- Поведение задаётся аннотациями, и они AWS-специфичные:

```yaml
# Service -> NLB
metadata:
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-scheme: internet-facing
    service.beta.kubernetes.io/aws-load-balancer-nlb-target-type: ip
```

```yaml
# Ingress -> ALB
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web
  annotations:
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
spec:
  ingressClassName: alb
  rules:
    - http:
        paths:
          - path: /
            pathType: Prefix
            backend: { service: { name: web, port: { number: 80 } } }
```

- **`target-type: ip`.** Балансировщик шлёт трафик прямо на IP пода, минуя
  NodePort и kube-proxy. Это работает благодаря VPC CNI (модуль 02): у пода
  настоящий адрес VPC. Вариант `instance` идёт через NodePort ноды.
- **Fargate** поддерживает только режим `ip`.
- **В EKS Auto Mode** управление балансировщиками встроено, отдельный LBC
  ставить не нужно (модуль 11).
- **Деньги и время.** Каждый ALB и NLB — отдельный платный ресурс, создаётся
  не мгновенно. Удаление Service или Ingress удаляет и балансировщик. Если же
  удалить кластер «грубо», балансировщики могут остаться и продолжать
  списывать деньги.

## Частые ошибки

- В EKS получили Classic Load Balancer, потому что не поставили LBC.
- Ingress создан, но адреса нет: не хватает тегов подсетей или прав у LBC.
- Забыли `ingressClassName`, и ни один контроллер не взял Ingress.

## Проверка себя

- Почему `target-type: ip` работает именно благодаря VPC CNI? *(У пода
  реальный адрес VPC, поэтому ALB может слать трафик прямо в под.)*
- Что создастся в EKS для `type=LoadBalancer` без LBC? *(Classic Load
  Balancer.)*
- Чем Ingress отличается от Service type=LoadBalancer по результату в AWS?
  *(Ingress через LBC даёт ALB, уровень 7 по host/path; Service даёт NLB,
  уровень 4.)*
