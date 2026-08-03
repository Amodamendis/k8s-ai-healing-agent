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
        # We use the modernized Bedrock Converse API format
        system_prompts = [{"text": self.system_prompt}]
        
        message_text = f"Metrics - CPU: {current_cpu}%, Replicas: {current_replicas}. What is your decision?"
        messages = [{
            "role": "user",
            "content": [{"text": message_text}]
        }]

        # Standardized parameters for the Converse API
        inference_config = {
            "maxTokens": 128,
            "temperature": 0.1,
            "topP": 0.9
        }

        try:
            response = self.client.converse(
                modelId=self.model_id,
                messages=messages,
                system=system_prompts,
                inferenceConfig=inference_config
            )
            
            # The Converse API standardizes the response path across all models
            decision = response['output']['message']['content'][0]['text'].strip()
            return decision
            
        except Exception as e:
            logger.error(f"Bedrock invocation failed: {e}")
            return '{"action": "DO_NOTHING"}'