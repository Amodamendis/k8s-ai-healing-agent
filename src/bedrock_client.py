import boto3
import json
import logging

logger = logging.getLogger(__name__)

class BedrockClient:
    def __init__(self, region: str, model_id: str):
        self.client = boto3.client(service_name='bedrock-runtime', region_name=region)
        self.model_id = model_id
        
        with open("prompts/bedrock_system_prompt.txt", "r") as f:
            self.system_prompt = f.read()

    def get_scaling_decision(self, current_cpu: float, current_replicas: int) -> str:
        prompt = (
            f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n"
            f"{self.system_prompt}\n"
            f"<|eot_id|><|start_header_id|>user<|end_header_id|>\n"
            f"Metrics - CPU: {current_cpu}%, Replicas: {current_replicas}. What is your decision?<|eot_id|>\n"
            f"<|start_header_id|>assistant<|end_header_id|>\n"
        )

        # Llama 3 requires a specific payload format on Bedrock
        payload = {
            "prompt": prompt,
            "max_gen_len": 128,
            "temperature": 0.1,
            "top_p": 0.9
        }

        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(payload),
                accept="application/json",
                contentType="application/json"
            )
            
            response_body = json.loads(response.get('body').read())
            # Llama 3 returns the text in the "generation" field
            decision = response_body.get('generation', '').strip()
            return decision
            
        except Exception as e:
            logger.error(f"Bedrock invocation failed: {e}")
            return '{"action": "DO_NOTHING"}'