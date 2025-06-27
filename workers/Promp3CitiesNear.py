import os
import time
import requests
from dotenv import load_dotenv

# Carica le credenziali
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'credentials.env'))

BASE = os.getenv("CONDUCTOR_SERVER_URL").rstrip("/")
API_KEY = os.getenv("CONDUCTOR_AUTH_KEY")
API_SECRET = os.getenv("CONDUCTOR_AUTH_SECRET")
WORKER_ID = "python-prompt3citiesnear-worker"
TASK_TYPE = "Prompt3CitiesNear"

HEADERS = {
    "X-Authorization": f"{API_KEY}:{API_SECRET}",
    "Content-Type": "application/json"
}

def poll_task():
    url = f"{BASE}/tasks/poll/{TASK_TYPE}/{WORKER_ID}"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code == 200 and resp.json():
        return resp.json()
    return None

def complete_task(task_id, output):
    url = f"{BASE}/tasks"
    payload = {
        "taskId": task_id,
        "status": "COMPLETED",
        "outputData": output
    }
    resp = requests.post(url, json=payload, headers=HEADERS)
    return resp.ok

def main():
    print("🔄 Worker Python avviato, polling ogni 2s…")
    while True:
        task = poll_task()
        if task and task.get("taskId"):
            tid = task["taskId"]
            inp = task.get("inputData", {})
            giorni = inp.get("giorni", 3)
            prefs = inp.get("preferenze", [])
            print(f"✔️  Task {tid} ricevuto, input={inp}")

            prompt = (
                f"Crea un prompt per generare un itinerario di "
                f"{giorni} giorni basato sulle preferenze: "
                f"{', '.join(prefs)}"
            )
            output = {"prompt": prompt}

            if complete_task(tid, output):
                print(f"✅ Task {tid} completato.")
            else:
                print(f"❌ Errore completando task {tid}.")
        else:
            # nessun task disponibile
            time.sleep(2)

if __name__ == "__main__":
    main()