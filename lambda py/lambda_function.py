import boto3
import json
import logging
import os

API_KEY = os.environ.get("API_KEY", "changeme")

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(f"Event received: {json.dumps(event)}")

    # 🔐 verifica API key
    headers = event.get("headers", {})
    client_key = headers.get("x-api-key")
    if client_key != API_KEY:
        logger.warning("Unauthorized request – invalid or missing API key")
        return {
            "statusCode": 401,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Unauthorized"})
        }

    # ✅ Legge e decodifica il body
    try:
        body = json.loads(event.get("body", "{}"))
        question = body.get("question", "Hello")
    except Exception as e:
        logger.error(f"Error parsing body: {str(e)}")
        question = "Hello"

    logger.info(f"Question received: {question}")

    bedrock = boto3.client("bedrock-agent-runtime")

    response = bedrock.retrieve_and_generate(
        input={"text": question},
        retrieveAndGenerateConfiguration={
            "knowledgeBaseConfiguration": {
                "knowledgeBaseId": "NFKFCBWDXB",
                "modelArn": "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0"
            },
            "type": "KNOWLEDGE_BASE"
        }
    )

    answer = response["output"]["text"]

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "question": question,
            "answer": answer
        })
    }