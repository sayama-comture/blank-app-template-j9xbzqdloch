import boto3
import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client('bedrock-runtime', region_name='us-east-1')

def main(prompt, max_token=2048):
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_token,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}]
            }
        ],
    })
    response = client.invoke_model(
        body=body,
        modelId="us.anthropic.claude-sonnet-4-20250514-v1:0"
    )
    response_body = json.loads(response.get('body').read())
    generated_text = response_body['content'][0]['text']
    print(generated_text)
    
if __name__ == "__main__":
    prompt = input()
    main(prompt)