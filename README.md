flowchart TD
    subgraph Developer_CI_CD["💻 CI/CD Pipelines (GitHub Actions)"]
        GH1["GitHub Repo: demo-cpu-spiker-app"] -->|Push to main| GHA1["GitHub Action: Docker Build & Push"]
        GH2["GitHub Repo: k8s-ai-healing-agent"] -->|Push to main| GHA2["GitHub Action: Docker Build & Push"]
    end

    subgraph AWS_Cloud["☁️ AWS Cloud (us-east-1)"]
        subgraph ECR["📦 Amazon ECR"]
            ECR1["ECR Repo: demo-cpu-spiker-app:latest"]
            ECR2["ECR Repo: k8s-ai-healing-agent:latest"]
        end

        GHA1 --> ECR1
        GHA2 --> ECR2

        subgraph EKS_Cluster["☸️ Amazon EKS Cluster (Provisioned via Terraform)"]
            
            subgraph Monitoring_NS["Namespace: monitoring"]
                PROM["Prometheus Server"]
                GRAF["Grafana Dashboard"]
                PROM --> GRAF
            end

            subgraph Default_NS["Namespace: default"]
                APP["Demo CPU Spiker App\n(FastAPI / CPU Spiker)"]
                SVC["Service: demo-cpu-spiker-app"]
                SM["ServiceMonitor CRD"]
                SECRET["Secret: llm-secrets\n(GROQ_API_KEY)"]
                
                subgraph Agent_Pod["AI Healing Agent Pod"]
                    SA["ServiceAccount: ai-healer-sa"]
                    ROLE["RBAC Role & RoleBinding\n(patch deployments/scale)"]
                    MAIN["main.py (30s Polling Loop)"]
                    METRICS["metrics_client.py"]
                    LLM["llm_client.py"]
                    EXEC["k8s_executor.py"]
                end
            end

            ECR1 -.->|Pull Image| APP
            ECR2 -.->|Pull Image| Agent_Pod

            SVC --> APP
            SM -.->|Scrape Config| SVC
            PROM -->|Scrape /metrics| APP
        end
    end

    subgraph External_API["🌐 External LLM Provider"]
        GROQ["Groq Cloud API\nModel: llama-3.1-8b-instant"]
    end

    %% Execution Event Flow
    USER["👤 User Browser"] -->|1. Click 'Spike CPU Load'| APP
    APP -->|2. CPU Rises to >80%| APP
    METRICS -->|3. Query PromQL CPU %| PROM
    MAIN --> METRICS
    MAIN --> LLM
    LLM -->|4. Send Prompt + Metrics| GROQ
    GROQ -->|5. Return JSON: SCALE_UP| LLM
    MAIN --> EXEC
    EXEC -->|6. Patch Deployment Replicas| APP
