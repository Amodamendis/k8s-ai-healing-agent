import os
import json
import logging
import requests

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        self.api_key = os.environ.get("GROQ_API_KEY")
        self.model_id = "llama3-8b-8192"
        self.endpoint = "https://api.groq.com/openai/v1/chat/completions"
        
        with open("prompts/bedrock_system_prompt.txt", "r") as f:
            self.system_prompt = f.read()

    def get_scaling_decision(self, current_cpu: float, current_replicas: int) -> str:
        if not self.api_key:
            logger.error("GROQ_API_KEY is not set.")
            return '{"action": "DO_NOTHING"}'

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model_id,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Metrics - CPU: {current_cpu}%, Replicas: {current_replicas}. What is your decision?"}
            ]
        }

        try:
            response = requests.post(self.endpoint, headers=headers, json=payload, timeout=10)
            
            # Print the actual error text if it fails again so we can debug it easily
            if response.status_code != 200:
                 logger.error(f"LLM Error Response: {response.text}")
            
            response.raise_for_status()
            
            response_data = response.json()
            decision = response_data['choices'][0]['message']['content'].strip()
            return decision
            
        except Exception as e:
            logger.error(f"LLM invocation failed: {e}")
            return '{"action": "DO_NOTHING"}'