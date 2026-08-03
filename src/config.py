import os

# Prometheus Configuration
PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://ai-monitor-kube-prometheus-prometheus.monitoring:9090")
TARGET_DEPLOYMENT = os.getenv("TARGET_DEPLOYMENT", "demo-cpu-spiker-app")
TARGET_NAMESPACE = os.getenv("TARGET_NAMESPACE", "default")

# AWS Bedrock Configuration
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
# Meta Llama 3 8B Instruct model ID in Amazon Bedrock
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "meta.llama3-8b-instruct-v1:0")

# Agent Configuration
CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", 30))
COOLDOWN_SECONDS = int(os.getenv("COOLDOWN_SECONDS", 300)) # 5 minutes