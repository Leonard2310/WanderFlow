# workers.py
from conductor.client.worker.worker_task import worker_task

def generate_user_profile(task_input: dict, *args, **kwargs) -> dict:
    preferences = task_input.get("preferences", [])
    profile = f"Viaggiatore interessato a: {', '.join(preferences)}"
    return {"profile": profile}

