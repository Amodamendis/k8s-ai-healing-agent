import time
import json
import logging
from src.config import *
from src.metrics_client import PrometheusClient
from src.llm_client import LLMClient
from src.k8s_executor import K8sExecutor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting AI Healing Agent...")
    
    prom_client = PrometheusClient(PROMETHEUS_URL)
    llm_client = LLMClient()
    k8s = K8sExecutor()
    
    last_action_time = 0

    while True:
        try:
            cpu = prom_client.get_cpu_utilization(TARGET_DEPLOYMENT)
            replicas = k8s.get_replica_count(TARGET_DEPLOYMENT, TARGET_NAMESPACE)
            
            logger.info(f"Status - CPU: {cpu}% | Replicas: {replicas}")

            # Check Cooldown
            if time.time() - last_action_time < COOLDOWN_SECONDS:
                logger.info("In cooldown period. Skipping AI analysis.")
                time.sleep(CHECK_INTERVAL_SECONDS)
                continue

            if cpu > 80.0 or cpu < 50.0:
                logger.info("Threshold crossed. Consulting Amazon Bedrock...")
                
                decision_str = llm_client.get_scaling_decision(cpu, replicas)
                logger.info(f"Bedrock Decision: {decision_str}")
                
                try:
                    decision_json = json.loads(decision_str)
                    action = decision_json.get("action")
                    
                    if action == "SCALE_UP" and replicas < 5:
                        k8s.scale_deployment(TARGET_DEPLOYMENT, TARGET_NAMESPACE, replicas + 1)
                        last_action_time = time.time()
                    elif action == "SCALE_DOWN" and replicas > 1:
                        k8s.scale_deployment(TARGET_DEPLOYMENT, TARGET_NAMESPACE, replicas - 1)
                        last_action_time = time.time()
                except json.JSONDecodeError:
                    logger.error("Failed to parse JSON from Bedrock.")

        except Exception as e:
            logger.error(f"Agent Loop Error: {e}")
            
        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()