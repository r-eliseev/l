# Приложение Г. Источники

*Все утверждения о версиях, ценах и поведении сервисов AWS в курсе снабжены
номером в квадратных скобках. Ниже — перечень источников с адресами и
дословными цитатами, на которые опирается текст.*

*Цитаты приведены в том виде, в каком они звучат в оригинале, — чтобы можно
было проверить формулировку, не доверяя пересказу.*


## Как читать ссылки

Номер в квадратных скобках после утверждения означает: это утверждение
опирается на источник под этим номером в перечне ниже.

## Документация AWS по EKS

### [1] Amazon EKS Pricing

https://aws.amazon.com/eks/pricing/

Ключевые формулировки:

> «Standard Kubernetes version support $0.10 per cluster per hour»

> «You pay $0.10 per hour during the first 14 months when the version is in standard support. After 14 months, the Kubernetes version transitions to extended support. You now pay $0.60 per hour for the remaining 12 months.»

> «Like EC2 instance charges, EKS Auto Mode charges are billed per-second, with a one-minute minimum.»


### [2] What is Amazon EKS?

https://docs.aws.amazon.com/eks/latest/userguide/what-is-eks.html

Ключевые формулировки:

> «**EKS standard**: AWS manages the Kubernetes control plane when you create a cluster with EKS. Components that manage nodes, schedule workloads, integrate with the AWS cloud, and store and scale control plane information to keep your clusters up and running, are handled for you automatically.»

> «**EKS Auto Mode**: Using the EKS Auto Mode feature, EKS extends its control to manage Nodes (Kubernetes data plane) as well. It simplifies Kubernetes management by automatically provisioning infrastructure, selecting optimal compute instances, dynamically scaling resources, continuously optimizing costs, patching operating systems, and integrating with AWS security services.»


### [3] Amazon EKS architecture

https://docs.aws.amazon.com/eks/latest/userguide/eks-architecture.html

Ключевые формулировки:

> «Amazon EKS ensures every cluster has its own unique Kubernetes control plane.»

> «The control plane positions at least two API server instances and three etcd instances across three AWS Availability Zones within an AWS Region.»

> «With Amazon EKS Hybrid Nodes, you can use your on-premises and edge infrastructure as nodes in Amazon EKS clusters. Amazon EKS Hybrid Nodes unifies Kubernetes management across environments and offloads Kubernetes control plane management to AWS for your on-premises and edge applications.»


### [4] Cluster API server endpoint

https://docs.aws.amazon.com/eks/latest/userguide/cluster-endpoint.html

Ключевые формулировки:

> «By default, this API server endpoint is public to the internet, and access to the API server is secured using a combination of AWS Identity and Access Management (IAM) and native Kubernetes Role Based Access Control (RBAC). This endpoint is known as the cluster public endpoint.»

> «You can enable private access to the Kubernetes API server so that all communication between your nodes and the API server stays within your VPC.»


### [5] Amazon VPC CNI (Best Practices)

https://docs.aws.amazon.com/eks/latest/best-practices/vpc-cni.html

Ключевые формулировки:

> «(Number of network interfaces for the instance type * (the number of IP addresses per network interface - 1)) + 2»

> «The VPC CNI checks the limits file to find out how many ENIs and IP addresses are allowed for each type of instance.»


### [6] Custom Networking (Best Practices)

https://docs.aws.amazon.com/eks/latest/best-practices/custom-networking.html

Ключевые формулировки:

> «The maximum number of Pods you can run without prefix assignment is 29»

> «With prefix assignment, each secondary IP is replaced with a /28 prefix on secondary ENIs.»


### [7] Prefix Mode for Linux (Best Practices)

https://docs.aws.amazon.com/eks/latest/best-practices/prefix-mode-linux.html

Ключевые формулировки:

> «you can now configure Amazon VPC CNI to assign /28 (16 IP addresses) IPv4 address prefixes, instead of assigning individual IPv4 addresses to the slots on network interfaces»

> «When `ENABLE_PREFIX_DELEGATION` is set to true VPC CNI allocates an IP address to a Pod from the prefix assigned to an ENI.»


### [8] Configure network policy for the Amazon VPC CNI

https://docs.aws.amazon.com/eks/latest/userguide/cni-network-policy-configure.html

Ключевые формулировки:

> «Your nodes must have Linux kernel version `5.10` or later.»


### [9] Set up the Amazon EBS CSI driver

https://docs.aws.amazon.com/eks/latest/userguide/ebs-csi.html

Ключевые формулировки:

> «You do not need to install the Amazon EBS CSI controller on EKS Auto Mode clusters.»

> «attempting to install the add-on and running `kubectl describe pvc` will show `failed to provision volume with StorageClass` along with a `could not create volume in EC2: UnauthorizedOperation` error»

> «EKS Auto Mode requires storage classes to use `ebs.csi.eks.amazonaws.com` as the provisioner. The standard Amazon EBS CSI Driver (`ebs.csi.aws.com`) manages its own volumes separately.»


### [10] Set up the Amazon EFS CSI driver

https://docs.aws.amazon.com/eks/latest/userguide/efs-csi.html

Ключевые формулировки:

> «The Amazon EFS CSI driver requires IAM permissions to interact with your file system.»


### [11] IAM roles for service accounts

https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html

Ключевые формулировки:

> «Create an IAM OIDC provider for your cluster – You only complete this procedure once for each cluster.»


### [12] EKS Pod Identity

https://docs.aws.amazon.com/eks/latest/userguide/pod-identities.html

Ключевые формулировки:

> «"Principal": { "Service": "pods.eks.amazonaws.com"»

> «You can’t use EKS Pod Identities with: + Pods that run anywhere except Linux Amazon EC2 instances. Linux and Windows pods that run on AWS Fargate (Fargate) aren’t supported.»


## Kubernetes и kind

### [13] Grant IAM users and roles access to Kubernetes APIs

https://docs.aws.amazon.com/eks/latest/userguide/grant-k8s-access.html

Ключевые формулировки:

> «Once the access entry method is enabled, it cannot be disabled.»

> «| `ConfigMap` only (`CONFIG_MAP`) | `aws-auth` `ConfigMap` | | EKS API and `ConfigMap` (`API_AND_CONFIG_MAP`) | access entries in the EKS API, AWS Command Line Interface, AWS SDKs, AWS CloudFormation, and AWS Management Console and `aws-auth` `ConfigMap` | | EKS API only (`API`) | access entries in the EKS API, AWS Command Line Interface, AWS SDKs, AWS CloudFormation, and AWS Management Console |»


### [14] Route internet traffic with AWS Load Balancer Controller

https://docs.aws.amazon.com/eks/latest/userguide/aws-load-balancer-controller.html

Ключевые формулировки:

> «The LBC creates an AWS Application Load Balancer (ALB) when you create a Kubernetes `Ingress`.»

> «The LBC creates an AWS Network Load Balancer (NLB) when you create a Kubernetes service of type `LoadBalancer`.»

> «In versions 2.5 and newer, the AWS Load Balancer Controller becomes the default controller for Kubernetes *service* resources with the `type: LoadBalancer` and makes an AWS Network Load Balancer (NLB) for each service.»

> «With the AWS Load Balancer Controller version `2.14.0` or later, the LBC creates an AWS Application Load Balancer (ALB) when you create a Kubernetes `Gateway`.»

> «The legacy cloud provider creates Classic Load Balancers. If you do not install the AWS Load Balancer Controller, Kubernetes will default to using the legacy cloud provider.»


### [15] Route TCP and UDP traffic with Network Load Balancers

https://docs.aws.amazon.com/eks/latest/userguide/network-load-balancing.html

Ключевые формулировки:

> «When you create a Kubernetes `Service` of type `LoadBalancer`, the AWS cloud provider load balancer controller creates AWS Classic Load Balancers by default, but can also create AWS»

> «**Key** – `kubernetes.io/role/internal-elb` + **Value** – `1`»

> «**Key** – `kubernetes.io/role/elb` + **Value** – `1`»


## Прочие материалы

- **[16]** Scale cluster compute with Karpenter and Cluster Autoscaler — https://docs.aws.amazon.com/eks/latest/userguide/autoscaling.html
- **[17]** Karpenter (Best Practices) — https://docs.aws.amazon.com/eks/latest/best-practices/karpenter.html
- **[18]** Auto Scaling (eksctl) — https://docs.aws.amazon.com/eks/latest/eksctl/autoscaling.html
- **[19]** Amazon EKS add-ons — https://docs.aws.amazon.com/eks/latest/userguide/eks-add-ons.html
- **[20]** Amazon EKS add-ons available for Amazon EKS clusters — https://docs.aws.amazon.com/eks/latest/userguide/workloads-add-ons-available-eks.html
- **[21]** aws eks update-addon (AWS CLI) — https://docs.aws.amazon.com/cli/latest/reference/eks/update-addon.html
- **[22]** Send control plane logs to CloudWatch Logs — https://docs.aws.amazon.com/eks/latest/userguide/control-plane-logs.html
- **[23]** Start AWS Fargate logging for your cluster — https://docs.aws.amazon.com/eks/latest/userguide/fargate-logging.html
- **[24]** Understand the Kubernetes version lifecycle on EKS — https://docs.aws.amazon.com/eks/latest/userguide/kubernetes-versions.html
- **[25]** Update the Kubernetes version for your Amazon EKS cluster — https://docs.aws.amazon.com/eks/latest/userguide/update-cluster.html
- **[26]** Update managed node group behavior — https://docs.aws.amazon.com/eks/latest/userguide/managed-node-update-behavior.html
- **[27]** Kubernetes Version and Version Skew Support Policy — https://kubernetes.io/releases/version-skew-policy/
- **[28]** Simplify compute management with AWS Fargate — https://docs.aws.amazon.com/eks/latest/userguide/fargate.html
- **[29]** Configure your Amazon EKS cluster for AWS Fargate — https://docs.aws.amazon.com/eks/latest/userguide/fargate-pod-configuration.html
- **[30]** Automate cluster infrastructure with EKS Auto Mode — https://docs.aws.amazon.com/eks/latest/userguide/automode.html
- **[31]** Quick Start (kind) — https://kind.sigs.k8s.io/docs/user/quick-start/
- **[32]** Configuring Your kind Cluster (kind) — https://kind.sigs.k8s.io/docs/user/configuration/
- **[33]** Operating Large Clusters (Kubernetes) — https://kubernetes.io/docs/setup/best-practices/cluster-large/
- **[34]** Create an Amazon EKS cluster — https://docs.aws.amazon.com/eks/latest/userguide/create-cluster.html
- **[35]** Ingress NGINX Retirement (Kubernetes Blog) — https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/
- **[36]** Maximum number of Pods for your Amazon EKS nodes — https://docs.aws.amazon.com/eks/latest/userguide/choosing-instance-type.html

## Источники, не процитированные в тексте

Эти материалы были изучены при подготовке книги, но прямой ссылки на них в главах нет: [32], [36]
