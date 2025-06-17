import os
import multiprocessing
from dotenv import load_dotenv

from conductor.client.configuration.configuration import Configuration, AuthenticationSettings
from conductor.client.metadata_client import MetadataClient
from conductor.client.automator.task_handler import TaskHandler
from conductor.client.worker.worker import Worker
from conductor.client.workflow.executor.workflow_executor import WorkflowExecutor
from conductor.client.http.models import WorkflowDef, WorkflowTask

from workers import generate_user_profile

from conductor.client.workflow.conductor_workflow import ConductorWorkflow
from conductor.client.workflow.task.simple_task import SimpleTask
from conductor.client.workflow.task.start_workflow_task import StartWorkflowTask
from conductor.client.worker.worker_task import worker_task
from conductor.client.http.models.start_workflow_request import StartWorkflowRequest
import time


def create_config():
    load_dotenv("credentials.env")
    auth = AuthenticationSettings(
        key_id=os.getenv("CONDUCTOR_AUTH_KEY"),
        key_secret=os.getenv("CONDUCTOR_AUTH_SECRET")
    )
    return Configuration(
        server_api_url=os.getenv("CONDUCTOR_SERVER_URL"),
        authentication_settings=auth
    )

def register_workflow(executor: WorkflowExecutor) -> ConductorWorkflow:

    #Generazione del profilo dell'utente -> prende in input le preferenze dell'utente e cosa fa?
    generate_profile_task = WorkflowTask(
        name="generate_user_profile",
        task_reference_name="t1",
        input_parameters={"preferences": "${workflow.input.preferences}"},
        type="SIMPLE"
    )

    #Prende il profilo dell'utente e 

    workflow = ConductorWorkflow(
        name="checkout_workflow",
        executor=executor
    )
    workflow.version = 1
    workflow.add(generate_profile_task)
    workflow.register(overwrite=True)
    return workflow

def main():
    config = create_config()
    executor = WorkflowExecutor(configuration=config)

    # 1) registra workflow via MetadataClient
    register_workflow(executor)

    # 2) avvia worker
    worker = Worker(task_definition_name="generate_user_profile", executor=generate_user_profile)
    #handler = TaskHandler(configuration=config, workers=[worker])
    handler = TaskHandler(
        workers=[worker],
        configuration=config,
        scan_for_annotated_workers=True
    )
    handler.start_processes()

    # 3) avvia il workflow
    #run = executor.start_workflow(name="tripmatch_workflow", version=1, workflow_input={"preferences": ["natura", "relax"]})
    #print("Workflow avviato:", run)

    handler.join_processes()
    # Trigger the checkout workflow
    input_data = {"preferences": ["natura", "relax"]}

    print("🚀 Starting checkout workflow...")
    run = executor.execute(
        name="checkout_workflow",
        version=1,
        workflow_input=input_data
    )

    print(f"✅ Workflow started: {run.workflow_id}")
    print(f"🔗 UI Link: {config.ui_host}/execution/{run.workflow_id}")

    # need to keep workers running for async workflow
    try:
        print("🧠 Workers running... Press Ctrl+C to exit.")
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("🛑 Stopping workers...")
        handler.stop_processes()

if __name__ == "__main__":
    multiprocessing.set_start_method("spawn", force=True)
    main()
