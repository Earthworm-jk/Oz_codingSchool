import asyncio
import json
import uuid
from pathlib import Path
from typing import Any

from fastapi import HTTPException

from app.core.redis_client import get_redis_client


PNEUMONIA_TASK_QUEUE = "pneumonia:tasks"
PNEUMONIA_RESULT_CHANNEL_PREFIX = "pneumonia:results"


async def request_pneumonia_prediction(
    image_path: Path,
    record_id: int | None = None,
    create_heatmap: bool = True,
    timeout_seconds: int = 60,
) -> dict[str, Any]:
    task_id = uuid.uuid4().hex
    result_channel = f"{PNEUMONIA_RESULT_CHANNEL_PREFIX}:{task_id}"
    redis = get_redis_client()
    pubsub = redis.pubsub()

    task = {
        "task_id": task_id,
        "record_id": record_id,
        "image_path": str(image_path),
        "create_heatmap": create_heatmap,
        "result_channel": result_channel,
    }

    try:
        await pubsub.subscribe(result_channel)
        await redis.rpush(PNEUMONIA_TASK_QUEUE, json.dumps(task, ensure_ascii=False))
        result = await _wait_for_worker_result(pubsub, timeout_seconds)
    finally:
        await pubsub.unsubscribe(result_channel)
        await pubsub.close()
        await redis.aclose()

    if result.get("status") == "error":
        raise HTTPException(
            status_code=500,
            detail=f"AI worker 처리 중 오류가 발생했습니다: {result.get('error', 'unknown error')}",
        )

    if result.get("status") != "success":
        raise HTTPException(status_code=500, detail="AI worker가 알 수 없는 응답을 반환했습니다.")

    return result["data"]


async def _wait_for_worker_result(pubsub, timeout_seconds: int) -> dict[str, Any]:
    deadline = asyncio.get_running_loop().time() + timeout_seconds

    while True:
        remaining = deadline - asyncio.get_running_loop().time()
        if remaining <= 0:
            raise HTTPException(status_code=504, detail="AI worker 응답 시간이 초과되었습니다.")

        message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=min(1.0, remaining))
        if message is None:
            await asyncio.sleep(0.05)
            continue

        return json.loads(message["data"])
