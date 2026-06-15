import json
import os
import uuid
from pathlib import Path
from typing import Any

from worker.model import generate_heatmap, predict_pneumonia
from worker.redis_client import get_redis_client


PNEUMONIA_TASK_QUEUE = os.getenv("PNEUMONIA_TASK_QUEUE", "pneumonia:tasks")
BASE_DIR = Path(__file__).resolve().parent.parent


def run_worker() -> None:
    redis = get_redis_client()
    print(f"AI worker started. Waiting for tasks on {PNEUMONIA_TASK_QUEUE}...")

    while True:
        queued_item = redis.blpop(PNEUMONIA_TASK_QUEUE, timeout=5)
        if queued_item is None:
            continue

        _, raw_task = queued_item
        task = json.loads(raw_task)
        result_channel = task["result_channel"]

        try:
            result = handle_prediction_task(task)
            redis.publish(
                result_channel,
                json.dumps({"status": "success", "data": result}, ensure_ascii=False),
            )
        except Exception as exc:
            redis.publish(
                result_channel,
                json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False),
            )


def handle_prediction_task(task: dict[str, Any]) -> dict[str, Any]:
    image_path = Path(task["image_path"])
    record_id = task.get("record_id")
    create_heatmap = task.get("create_heatmap", True)

    prediction_result = predict_pneumonia(str(image_path))
    response = {
        "prediction": prediction_result["prediction"],
        "probability_normal": prediction_result["probability_normal"],
        "probability_pneumonia": prediction_result["probability_pneumonia"],
        "confidence": prediction_result["confidence"],
        "heatmap_url": None,
    }

    if create_heatmap:
        heatmap_dir = BASE_DIR / "media" / "heatmap"
        heatmap_dir.mkdir(parents=True, exist_ok=True)
        filename_prefix = f"record_{record_id}" if record_id is not None else "upload"
        heatmap_filename = f"{filename_prefix}_{uuid.uuid4().hex[:8]}.png"
        heatmap_path = heatmap_dir / heatmap_filename
        generate_heatmap(str(image_path), str(heatmap_path))
        response["heatmap_url"] = f"/media/heatmap/{heatmap_filename}"

    return response


if __name__ == "__main__":
    run_worker()
