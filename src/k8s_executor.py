import logging
from kubernetes import client, config

logger = logging.getLogger(__name__)

class K8sExecutor:
    def __init__(self): 
        try:
            # When running inside the pod, it uses the attached ServiceAccount
            config.load_incluster_config()
            logger.info("Loaded in-cluster Kubernetes config.")
        except config.ConfigException:
            # Fallback for local testing (though we are running this in EKS)
            config.load_kube_config()
            logger.info("Loaded local kubeconfig.")
            
        self.apps_v1 = client.AppsV1Api()

    def get_replica_count(self, deployment_name: str, namespace: str) -> int:
        try:
            deployment = self.apps_v1.read_namespaced_deployment(deployment_name, namespace)
            return deployment.spec.replicas
        except Exception as e:
            logger.error(f"Error fetching deployment {deployment_name}: {e}")
            return -1

    def scale_deployment(self, deployment_name: str, namespace: str, target_replicas: int):
        try:
            body = {"spec": {"replicas": target_replicas}}
            self.apps_v1.patch_namespaced_deployment_scale(
                name=deployment_name, 
                namespace=namespace, 
                body=body
            )
            logger.info(f"Scaled {deployment_name} to {target_replicas} replicas.")
        except Exception as e:
            logger.error(f"Failed to scale deployment {deployment_name}: {e}")