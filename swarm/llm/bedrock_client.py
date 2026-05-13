import json
import os
import logging
from typing import Any, Dict

import boto3
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger(__name__)


class BedrockLLMClient:
    """
    Minimal AWS Bedrock LLM client.

    Responsibilities:
    - Build and send a prompt to Bedrock
    - Return raw text output to callers
    - NEVER perform parsing or schema validation
    - Fail closed on any error

    Observability:
    - Optional debug logging of prompt and raw output
    - Controlled via LLM_DEBUG_LOGS=true
    """

    def __init__(self) -> None:
        # Required configuration (fail fast)
        self.model_id = os.environ["LLM_MODEL"]
        self.region = os.environ.get("LLM_AWS_REGION", "eu-south-2")

        self.max_tokens = int(os.environ.get("LLM_MAX_TOKENS", "1024"))
        self.temperature = float(os.environ.get("LLM_TEMPERATURE", "0.2"))

        # Debug flag (safe default: False)
        self.debug_logs = (
            os.environ.get("LLM_DEBUG_LOGS", "false").lower() == "true"
        )

        self.client = boto3.client(
            "bedrock-runtime",
            region_name=self.region,
        )

        if self.debug_logs:
            logger.info(
                "BedrockLLMClient initialized with debug logging enabled"
            )

    def invoke(self, prompt: str) -> str:
        """
        Send a prompt to Anthropic Claude on AWS Bedrock
        and return the raw text response.
        """

        if self.debug_logs:
            logger.info("========== LLM PROMPT (FINAL) ==========")
            logger.info(prompt)
            logger.info("=======================================")

        try:
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ],
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
            }

            response = self.client.invoke_model(
                modelId=self.model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(body),
            )

            response_body = json.loads(response["body"].read())

            # Claude responses come back like:
            # { "content": [ { "type": "text", "text": "..." } ] }

            output_text = ""
            for block in response_body.get("content", []):
                if block.get("type") == "text":
                    output_text += block.get("text", "")

            output_text = output_text.strip()

            if self.debug_logs:
                logger.info("========== LLM RAW OUTPUT ==============")
                logger.info(output_text)
                logger.info("=======================================")

            return output_text

        except Exception as exc:
            if self.debug_logs:
                logger.warning("LLM invocation failed; returning empty output")
                logger.warning(str(exc))

            return ""