"""
Prompt3CitiesNear Worker for WanderFlow Application

This module implements a Conductor worker that processes tasks for generating
prompts related to 3-city near travel recommendations. The worker polls for
tasks, processes travel preferences, and returns formatted prompts.
"""

import os
import time
import logging
import requests
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load credentials from environment file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'credentials.env'))

# Conductor configuration
BASE = os.getenv("CONDUCTOR_SERVER_URL").rstrip("/")
API_KEY = os.getenv("CONDUCTOR_AUTH_KEY")
API_SECRET = os.getenv("CONDUCTOR_AUTH_SECRET")
WORKER_ID = "python-prompt3citiesnear-worker"
TASK_TYPE = "Prompt3CitiesNear"

# HTTP headers for API authentication
HEADERS = {
    "X-Authorization": f"{API_KEY}:{API_SECRET}",
    "Content-Type": "application/json"
}

def poll_task():
    """
    Poll for available tasks from the Conductor server.
    
    This function continuously checks for tasks of type "Prompt3CitiesNear"
    assigned to this worker. When a task is available, it returns the task data.
    
    Returns:
        dict or None: Task data if available, None if no tasks are pending
    """
    url = f"{BASE}/tasks/poll/{TASK_TYPE}/{WORKER_ID}"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code == 200 and resp.json():
        return resp.json()
    return None

def complete_task(task_id, output):
    """
    Mark a task as completed and submit the results.
    
    Args:
        task_id (str): The unique identifier of the task to complete
        output (dict): The task output data containing the generated prompt
        
    Returns:
        bool: True if task completion was successful, False otherwise
    """
    url = f"{BASE}/tasks"
    payload = {
        "taskId": task_id,
        "status": "COMPLETED",
        "outputData": output
    }
    resp = requests.post(url, json=payload, headers=HEADERS)
    return resp.ok

def main():
    """
    Main worker execution loop.
    
    This function runs continuously, polling for tasks every 2 seconds.
    When a task is received, it processes the travel preferences and
    generates an appropriate prompt for the itinerary creation.
    """
    logger.info("🔄 Python Worker started, polling every 2s...")
    while True:
        task = poll_task()
        if task and task.get("taskId"):
            task_id = task["taskId"]
            input_data = task.get("inputData", {})
            days = input_data.get("giorni", 3)
            preferences = input_data.get("preferenze", [])
            logger.info(f"✔️  Task {task_id} received, input={input_data}")

            # Generate prompt based on input parameters
            prompt = (
                f"Create a prompt to generate an itinerary for "
                f"{days} days based on preferences: "
                f"{', '.join(preferences)}"
            )
            output = {"prompt": prompt}

            # Complete the task with generated output
            if complete_task(task_id, output):
                logger.info(f"✅ Task {task_id} completed.")
            else:
                logger.error(f"❌ Error completing task {task_id}.")
        else:
            # No tasks available, wait before next poll
            time.sleep(2)

if __name__ == "__main__":
    main()