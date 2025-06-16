from dotenv import load_dotenv
import os

from conductor.client.configuration.configuration import Configuration
from conductor.client.worker.worker import Worker
from conductor.client.automator.task_handler import start_workers
from conductor.client.http.models import TaskDef, WorkflowDef, WorkflowTask
from conductor.client.automator.task_runner import task_handler

# Carica variabili d'ambiente
load_dotenv("credentials.env")

# Recupera i valori dal file .env
API_KEY_ID = os.getenv("CONDUCTOR_AUTH_KEY")
API_KEY_SECRET = os.getenv("CONDUCTOR_AUTH_SECRET")
SERVER_URL = os.getenv("CONDUCTOR_SERVER_URL")

# Configurazione di Conductor
config = Configuration(
    server_api_url=SERVER_URL,
    api_key_id=API_KEY_ID,
    api_key_secret=API_KEY_SECRET
)

@task_handler(name="generate_user_profile")
def generate_user_profile(task_input, *args, **kwargs):
    preferences = task_input.get("preferences", [])
    profile = f"Viaggiatore interessato a: {', '.join(preferences)}"
    return {"profile": profile}

def register_task_definitions():
    task_def = TaskDef(
        name="generate_user_profile",
        description="Crea un profilo sintetico dalle preferenze dell'utente",
        retry_count=1,
        timeout_seconds=60
    )
    config.get_task_resource().register_task_definitions([task_def])

def register_workflow():
    workflow = WorkflowDef(
        name="tripmatch_workflow",
        description="Generatore itinerario viaggio personalizzato",
        version=1,
        tasks=[
            WorkflowTask(
                name="generate_user_profile",
                task_reference_name="t1",
                type="SIMPLE"
            )
        ],
        schema_version=2
    )
    config.get_workflow_resource().register_workflow(workflow)

def start_all_workers():
    start_workers(config, [Worker(config=config, task_definition_name="generate_user_profile", executor=generate_user_profile)])

if __name__ == "__main__":
    register_task_definitions()
    register_workflow()
    start_all_workers()
    print("Conductor workers started successfully.")