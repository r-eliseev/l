# Модуль 03. Хранилище

## Общее

Модель хранилища одинакова везде:

- **PersistentVolume (PV)** — кусок реального хранилища.
- **PersistentVolumeClaim (PVC)** — запрос приложения на хранилище.
- **StorageClass** — шаблон «как создавать PV по требованию» (dynamic
  provisioning) через CSI-драйвер.
- **Режим доступа:** `ReadWriteOnce` (RWO, одна нода пишет), `ReadWriteMany`
  (RWX, много нод пишут одновременно).

### Практика на kind

```yaml
# pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: demo-pvc
spec:
  accessModes: ["ReadWriteOnce"]
  resources:
    requests:
      storage: 1Gi
```

```bash
kubectl get storageclass          # в kind: standard (rancher.io/local-path)
kubectl apply -f pvc.yaml
kubectl get pvc                   # Pending — это нормально, см. ниже
kubectl run app --image=busybox --restart=Never --overrides='{
  "spec":{"containers":[{"name":"app","image":"busybox","command":["sleep","3600"],
  "volumeMounts":[{"name":"d","mountPath":"/data"}]}],
  "volumes":[{"name":"d","persistentVolumeClaim":{"claimName":"demo-pvc"}}]}}'
kubectl get pvc,pv                # теперь Bound
```

В kind работает **local-path-provisioner**: PV создаётся как папка на диске
ноды. У StorageClass стоит режим `WaitForFirstConsumer`: том появляется, когда
под запланирован на ноду. Поэтому PVC без пода остаётся `Pending`, и это не
ошибка.

Минус local-path: данные привязаны к одной ноде и не переживут её удаление.

## В EKS

- **EBS CSI driver нужно поставить самому.** В отличие от kind, где
  provisioner уже есть, в обычном EKS-кластере драйвер ставится как
  add-on `aws-ebs-csi-driver`. В EKS Auto Mode он встроен. В кластере
  может быть StorageClass `gp2`, но без драйвера PVC будет висеть в
  `Pending`. Проверьте `kubectl get sc` у себя.
- **Драйверу нужна IAM-роль**, потому что он создаёт тома через AWS API. Без
  неё в событиях PVC будет `UnauthorizedOperation`. Используется
  управляемая политика `AmazonEBSCSIDriverPolicyV2`, роль привязывается через
  Pod Identity или IRSA (модуль 04). Это ещё одна точка, где хранилище
  связано с IAM.
- **Свой StorageClass.** Типичный современный вариант — gp3:

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata: { name: ebs-gp3 }
provisioner: ebs.csi.aws.com      # в Auto Mode: ebs.csi.eks.amazonaws.com
parameters: { type: gp3, encrypted: "true" }
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
```

- **EBS привязан к одной зоне доступности (AZ).** Том живёт в той AZ, где
  создан, и под с ним может запуститься только на ноде в этой зоне. Поэтому
  важен `WaitForFirstConsumer`: том создаётся уже после выбора ноды, в её AZ.
  Если сделать иначе, под может «застрять» (Pending с ошибкой про volume node
  affinity), даже когда на других нодах полно свободных ресурсов.
- **EBS даёт только RWO.** Для RWX нужен **EFS CSI driver** (add-on
  `aws-efs-csi-driver`): общая файловая система, доступная из нескольких AZ.
  В kind полноценного RWX «из коробки» нет.
- **Снапшоты и шифрование** управляются через AWS: CSI snapshot controller
  (add-on `snapshot-controller`) и KMS.
- **Деньги.** Каждый PV — реальный платный EBS-том, и он может остаться после
  удаления кластера, если политика `Retain` или кластер удалили «грубо».
  Проверяйте диски после экспериментов.
- **Fargate.** EBS на Fargate подключить нельзя. EFS можно, но только со
  статическим PV, динамическое создание томов на Fargate не поддерживается
  (модуль 10).

## Частые ошибки

- PVC вечно `Pending` в EKS: не установлен драйвер или нет IAM-роли.
- Под не запускается после «переезда»: том в одной AZ, под хочет в другую.
- Ожидание, что EBS можно монтировать в несколько подов на разных нодах.

## Проверка себя

- Почему под с EBS-томом может не запуститься, хотя на других нодах есть
  ресурсы? *(Том привязан к своей AZ. Под можно запланировать только на ноду
  в той же зоне.)*
- Какой тип хранилища нужен для RWX в EKS? *(EFS.)*
- Что нужно сделать в EKS для работы EBS-томов, чего не нужно в kind?
  *(Поставить EBS CSI driver и выдать ему IAM-роль.)*
