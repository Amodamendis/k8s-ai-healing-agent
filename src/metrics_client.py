import requests
import logging

logger = logging.getLogger(__name__)

class PrometheusClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def get_cpu_utilization(self, deployment_name: str) -> float:
        # A simple PromQL query to get the container's CPU usage percentage
        query = (
            f'sum(rate(container_cpu_usage_seconds_total{{pod=~"{deployment_name}-.*"}}[1m])) '
            f'/ sum(kube_pod_container_resource_limits{{resource="cpu", pod=~"{deployment_name}-.*"}}) * 100'
        )
        
        try:
            response = requests.get(f"{self.base_url}/api/v1/query", params={"query": query}, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            result = data.get("data", {}).get("result", [])
            if not result:
                return 0.0
                
            # The value is a string inside a list: [timestamp, "value"]
            cpu_percent = float(result[0]["value"][1])
            return round(cpu_percent, 2)
        except Exception as e:
            logger.error(f"Error querying Prometheus: {e}")
            return 0.0