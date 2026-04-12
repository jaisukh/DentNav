import json
from typing import Any, Dict

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.config import settings


def _load_questionnaire_from_disk() -> Dict[str, Any]:
    local_path = settings.data_dir / "questionnaire.v1.json"
    if not local_path.is_file():
        raise ValueError(
            "No questionnaire source: configure AWS_S3_BUCKET + AWS_S3_QUESTIONNAIRE_KEY, "
            f"or add {local_path}"
        )
    return json.loads(local_path.read_bytes().decode("utf-8"))


async def load_questionnaire() -> Dict[str, Any]:
    if not settings.aws_s3_bucket or not settings.aws_s3_questionnaire_key:
        return _load_questionnaire_from_disk()

    try:
        s3 = boto3.client("s3", region_name=settings.aws_region)
        response = s3.get_object(Bucket=settings.aws_s3_bucket, Key=settings.aws_s3_questionnaire_key)
        raw = response["Body"].read()
        return json.loads(raw.decode("utf-8"))
    except (ClientError, BotoCoreError, OSError):
        return _load_questionnaire_from_disk()
