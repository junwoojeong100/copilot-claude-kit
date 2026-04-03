# Azure ↔ AWS ↔ GCP Service Mapping

서비스 카테고리별 대응 매핑 테이블입니다. "AWS의 X에 해당하는 Azure 서비스는?" 질문에 즉시 참조하세요.

---

## Compute

| Azure | AWS | GCP |
|-------|-----|-----|
| Virtual Machines | EC2 | Compute Engine |
| VM Scale Sets | Auto Scaling Groups | Managed Instance Groups |
| App Service | Elastic Beanstalk / App Runner | App Engine |
| Azure Functions | Lambda | Cloud Functions |
| Container Apps | ECS Fargate / App Runner | Cloud Run |
| AKS | EKS | GKE |
| Container Instances | Fargate (standalone) | Cloud Run Jobs |
| Azure Batch | AWS Batch | Batch on GKE |
| Azure Spring Apps | — | — |
| Static Web Apps | Amplify Hosting | Firebase Hosting |
| Dev Box | WorkSpaces | — |

## Database

| Azure | AWS | GCP |
|-------|-----|-----|
| Azure SQL Database | RDS SQL Server | Cloud SQL (SQL Server) |
| Azure SQL Managed Instance | RDS Custom | — |
| Azure Database for PostgreSQL | RDS PostgreSQL / Aurora PostgreSQL | Cloud SQL / AlloyDB |
| Azure Database for MySQL | RDS MySQL / Aurora MySQL | Cloud SQL (MySQL) |
| Cosmos DB | DynamoDB / DocumentDB | Firestore / Bigtable |
| Azure Cache for Redis | ElastiCache (Redis) | Memorystore (Redis) |
| Azure Database for MariaDB | RDS MariaDB | — |

## Storage

| Azure | AWS | GCP |
|-------|-----|-----|
| Blob Storage | S3 | Cloud Storage |
| Azure Files | EFS | Filestore |
| Queue Storage | SQS | — |
| Table Storage | DynamoDB | Bigtable |
| Azure Data Lake Storage | S3 + Lake Formation | Cloud Storage (HDFS compat) |
| Managed Disks | EBS | Persistent Disk |
| Azure NetApp Files | FSx for NetApp ONTAP | NetApp Cloud Volumes |

## Networking

| Azure | AWS | GCP |
|-------|-----|-----|
| Virtual Network (VNet) | VPC | VPC |
| Load Balancer | NLB | Network Load Balancer |
| Application Gateway | ALB | HTTP(S) Load Balancer |
| Azure Front Door | CloudFront + WAF | Cloud CDN + Cloud Armor |
| Azure DNS | Route 53 | Cloud DNS |
| VPN Gateway | VPN Gateway | Cloud VPN |
| ExpressRoute | Direct Connect | Cloud Interconnect |
| Azure Firewall | Network Firewall | Cloud NGFW |
| Private Link / Endpoint | PrivateLink | Private Service Connect |
| Traffic Manager | Route 53 (DNS routing) | Traffic Director |
| Azure DDoS Protection | Shield | Cloud Armor |
| Network Watcher | VPC Flow Logs + Reachability Analyzer | Network Intelligence Center |
| Azure Bastion | Systems Manager Session Manager | IAP TCP Forwarding |
| NAT Gateway | NAT Gateway | Cloud NAT |

## Identity & Security

| Azure | AWS | GCP |
|-------|-----|-----|
| Entra ID (Azure AD) | IAM + Cognito | Cloud Identity + IAM |
| Managed Identity | IAM Roles (for services) | Service Accounts |
| Key Vault | Secrets Manager + KMS | Secret Manager + Cloud KMS |
| Defender for Cloud | Security Hub + GuardDuty | Security Command Center |
| Microsoft Sentinel | Security Lake + OpenSearch | Chronicle |
| Azure Policy | AWS Config + SCPs | Organization Policy |
| Purview | Macie + Glue Catalog | Dataplex + DLP |
| DDoS Protection | Shield Advanced | Cloud Armor |
| Entra External ID | Cognito User Pools | Identity Platform |

## AI & Machine Learning

| Azure | AWS | GCP |
|-------|-----|-----|
| Azure OpenAI Service | Bedrock (Claude, Titan) | Vertex AI (Gemini) |
| Azure AI Foundry | Bedrock + SageMaker | Vertex AI |
| Azure Machine Learning | SageMaker | Vertex AI |
| Azure AI Search | OpenSearch + Kendra | Vertex AI Search |
| Azure AI Document Intelligence | Textract | Document AI |
| Azure AI Speech | Transcribe + Polly | Speech-to-Text/Text-to-Speech |
| Azure AI Vision | Rekognition | Vision AI |
| Azure AI Language | Comprehend | Natural Language API |
| Azure AI Translator | Translate | Translation AI |
| Azure Bot Service | Lex | Dialogflow |
| GitHub Copilot | Amazon Q Developer | Gemini Code Assist |

## Messaging & Events

| Azure | AWS | GCP |
|-------|-----|-----|
| Service Bus | SQS + SNS | Pub/Sub |
| Event Hubs | Kinesis Data Streams | Pub/Sub |
| Event Grid | EventBridge | Eventarc |
| Queue Storage | SQS | Cloud Tasks |
| Notification Hubs | SNS (Mobile Push) | Firebase Cloud Messaging |

## Analytics & Big Data

| Azure | AWS | GCP |
|-------|-----|-----|
| Synapse Analytics | Redshift + Athena + Glue | BigQuery |
| Data Factory | Glue | Dataflow |
| Stream Analytics | Kinesis Data Analytics | Dataflow (streaming) |
| Azure Databricks | EMR + Databricks on AWS | Dataproc + Databricks on GCP |
| Data Explorer (Kusto) | Timestream + OpenSearch | — |
| Power BI | QuickSight | Looker |
| HDInsight | EMR | Dataproc |

## DevOps & Management

| Azure | AWS | GCP |
|-------|-----|-----|
| Azure DevOps | CodePipeline + CodeBuild | Cloud Build |
| GitHub Actions | CodePipeline + CodeBuild | Cloud Build |
| Azure Monitor | CloudWatch | Cloud Monitoring |
| Application Insights | X-Ray + CloudWatch RUM | Cloud Trace + Cloud Profiler |
| Log Analytics | CloudWatch Logs Insights | Cloud Logging |
| Azure Resource Manager | CloudFormation | Deployment Manager / Config Connector |
| Bicep | CloudFormation / CDK | — |
| Azure Advisor | Trusted Advisor | Recommender |
| Cost Management | Cost Explorer | Cost Management |
| Azure Arc | — (AWS 전용) | Anthos |

## IoT

| Azure | AWS | GCP |
|-------|-----|-----|
| IoT Hub | IoT Core | IoT Core (deprecated → Pub/Sub) |
| IoT Central | IoT SiteWise | — |
| IoT Edge | Greengrass | — |
| Digital Twins | IoT TwinMaker | Supply Chain Twin |
| Azure Sphere | — | — |

## Integration

| Azure | AWS | GCP |
|-------|-----|-----|
| Logic Apps | Step Functions | Workflows |
| API Management | API Gateway | Apigee |
| Service Bus | MQ + SQS | — |
| Azure SignalR | AppSync (WebSocket) | — |

## Containers & Registry

| Azure | AWS | GCP |
|-------|-----|-----|
| Azure Container Registry | ECR | Artifact Registry |
| Container Apps | ECS Fargate / App Runner | Cloud Run |
| AKS | EKS | GKE |
| Container Instances | Fargate (standalone task) | Cloud Run Jobs |

---

## GitHub ↔ GitLab ↔ Bitbucket Mapping

| GitHub | GitLab | Bitbucket |
|--------|--------|-----------|
| Repositories | Projects/Repos | Repositories |
| Pull Requests | Merge Requests | Pull Requests |
| GitHub Actions | GitLab CI/CD | Bitbucket Pipelines |
| Issues | Issues | Jira Issues |
| Projects (v2) | Issue Boards | Jira Boards |
| GitHub Pages | GitLab Pages | — |
| GitHub Packages | GitLab Packages | — |
| GHCR (Container Registry) | GitLab Container Registry | — |
| GitHub Discussions | — | — |
| GitHub Copilot | GitLab Duo | — |
| GitHub Advanced Security | GitLab Ultimate Security | Snyk 연동 |
| Dependabot | Dependency Scanning | — |
| CodeQL (SAST) | GitLab SAST | — |
| Secret Scanning | Secret Detection | — |
| GitHub Codespaces | Web IDE / Remote Dev | — |
| GitHub Wiki | GitLab Wiki | Bitbucket Wiki |
| GitHub Sponsors | — | — |

---

## 참고 링크

- [Microsoft: Azure ↔ AWS 서비스 비교 공식 문서](https://learn.microsoft.com/azure/architecture/aws-professional/services)
- [Microsoft: Azure ↔ GCP 서비스 비교 공식 문서](https://learn.microsoft.com/azure/architecture/gcp-professional/services)
