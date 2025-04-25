
# core/secrets.py

import boto3
import json
import os
from botocore.exceptions import ClientError

def load_aws_secret(secret_name, region_name="ap-northeast-2"):
    """
    AWS Secrets Manager에서 비밀을 가져와 환경 변수로 설정합니다.

    :param secret_name: 저장된 secret 이름 (예: 'chickpay/prod/credentials')
    :param region_name: AWS 리전 (기본: ap-northeast-2 = 서울)
    """
    client = boto3.client("secretsmanager", region_name=region_name)

    try:
        response = client.get_secret_value(SecretId=secret_name)
        secret = json.loads(response['SecretString'])

        # 환경 변수로 설정
        for key, value in secret.items():
            os.environ[key] = value

    except ClientError as e:
        print(f"[ERROR] Failed to load secrets: {e}")
        raise e
