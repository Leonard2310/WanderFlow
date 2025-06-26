from flask import Flask, request, render_template, redirect, url_for
from conductor.client.configuration.configuration import Configuration, AuthenticationSettings
from conductor.client.workflow.executor.workflow_executor import WorkflowExecutor
from conductor.client.orkes.orkes_task_client import OrkesTaskClient
from dotenv import load_dotenv
import threading
import time
import os

app = Flask(__name__)

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

config = create_config()
task_client = OrkesTaskClient(configuration=config)
executor = WorkflowExecutor(configuration=config)

@app.route("/")
def index():
    # Mostra pagina per avviare workflow
    return render_template("index.html")

@app.route("/start_workflow", methods=["POST"])
def start_workflow():
    # Avvia workflow senza input (o con input minimo)
    run = executor.execute(
        name="checkout_workflow",
        version=1,
        workflow_input={}  # oppure puoi mettere input minimo
    )
    # Reindirizza a pagina che indica l'ID del workflow
    return render_template("workflow_started.html", workflow_id=run.workflow_id, ui_host=config.ui_host)

@app.route("/form/<task_id>")
def form(task_id):
    # Mostra form per completare il task WaitUserRequest
    return render_template("form.html", task_id=task_id)

@app.route("/complete_task", methods=["POST"])
def complete_task():
    task_id = request.form["taskId"]
    durata = request.form.get("durata", type=int)
    prefs = request.form.getlist("preferences")

    # Completa il task WAIT_FOR_WEBHOOK con output dati utente
    task_client.update_task({
        "taskId": task_id,
        "status": "COMPLETED",
        "outputData": {
            "durata": durata,
            "preferences": prefs
        }
    })
    return "✅ Preferenze inviate a Conductor!"

@app.route("/wait_task")
def wait_task():
    # Prova a fare polling per un task WaitUserRequest (timeout 10s)
    worker_id = "web_form_worker"  # ID del worker, personalizzabile

    task = task_client.poll(task_type="WaitUserRequest", worker_id=worker_id, timeout=10000)
    if task and task.get("taskId"):
        task_id = task["taskId"]
        # Redirect a form con task_id
        return redirect(url_for("form", task_id=task_id))
    else:
        return "<p>Nessun task disponibile al momento. Ricarica questa pagina fra qualche secondo.</p>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
