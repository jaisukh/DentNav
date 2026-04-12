import json
from typing import Any, Dict

import boto3

from app.config import settings


async def load_questionnaire() -> Dict[str, Any]:
    if not settings.aws_s3_bucket or not settings.aws_s3_questionnaire_key:
        raise ValueError("Missing AWS_S3_BUCKET or AWS_S3_QUESTIONNAIRE_KEY")

    s3 = boto3.client("s3", region_name=settings.aws_region)
    response = s3.get_object(Bucket=settings.aws_s3_bucket, Key=settings.aws_s3_questionnaire_key)
    raw = response["Body"].read()
    return json.loads(raw.decode("utf-8"))
