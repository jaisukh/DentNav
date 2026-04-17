import asyncio
import json
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.config import REPO_ROOT, settings
from app.schemas.questionnaire import QuestionnaireDocument


async def load_questionnaire_document() -> QuestionnaireDocument:
    raw: dict[str, Any]
    if settings.aws_s3_bucket and settings.aws_s3_questionnaire_key:

        def _read_s3() -> dict[str, Any]:
            s3 = boto3.client("s3", region_name=settings.aws_region)
            response = s3.get_object(
                Bucket=settings.aws_s3_bucket, Key=settings.aws_s3_questionnaire_key
            )
            return json.loads(response["Body"].read().decode("utf-8"))

        try:
            raw = await asyncio.to_thread(_read_s3)
        except (ClientError, BotoCoreError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ValueError(f"S3 questionnaire load failed: {exc}") from exc
    else:
        path = settings.questionnaire_local_path
        if not path.exists():
            path = REPO_ROOT / "data" / "questionnaire.v1.json"
        if not path.exists():
            raise ValueError(
                "No questionnaire source: set AWS_S3_BUCKET + AWS_S3_QUESTIONNAIRE_KEY "
                f"or place questionnaire JSON at {path}"
            )
        raw = json.loads(path.read_text(encoding="utf-8"))

    return QuestionnaireDocument.model_validate(raw)
