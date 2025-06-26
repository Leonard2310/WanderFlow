from flask import Flask, request, render_template, redirect, url_for, jsonify
from conductor.client.configuration.configuration import Configuration, AuthenticationSettings
from conductor.client.workflow.executor.workflow_executor import WorkflowExecutor
from conductor.client.orkes.orkes_task_client import OrkesTaskClient
from dotenv import load_dotenv
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

config      = create_config()
executor    = WorkflowExecutor(configuration=config)
task_client = OrkesTaskClient(configuration=config)
UI_HOST     = os.getenv("CONDUCTOR_UI_HOST", "").rstrip("/")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start_workflow", methods=["POST"])
def start_workflow():
    run = executor.execute(
        name="TripMatch_BPA",
        version=2,
        workflow_input={}
    )
    return redirect(url_for("workflow_started", workflow_id=run.workflow_id))

@app.route("/workflow_started/<workflow_id>")
def workflow_started(workflow_id):
    return render_template(
        "workflow_started.html",
        workflow_id=workflow_id,
        ui_host=UI_HOST
    )

@app.route("/wait_task/<workflow_id>")
def wait_task(workflow_id):
    wf = executor.get_workflow(workflow_id=workflow_id, include_tasks=True)
    details = []

    for t in wf.tasks:
        # Usa gli attributi corretti esposti dal modello Task
        ref_name = getattr(t, "reference_task_name", None)
        status   = getattr(t, "status", None)
        tid      = getattr(t, "task_id", None)

        # Log per debug
        app.logger.debug(f"Task found: ref_name={ref_name}, status={status}, task_id={tid}")

        # Se è il nostro WaitUserRequest in corso, reindirizza al form
        if ref_name == "WaitUserRequest" and status == "IN_PROGRESS" and tid:
            return redirect(url_for("form", task_id=tid))

        details.append(f"{ref_name} ➞ {status} (id={tid})")

    # Se non lo trova, mostra messaggio + elenco per debug
    return (
        "<p>Nessun task disponibile al momento. Ricarica questa pagina fra qualche secondo.</p>"
        "<h3>Debug tasks:</h3><pre>"
        + "\n".join(details) +
        "</pre>"
    )

@app.route("/form/<task_id>")
def form(task_id):
    return render_template("form.html", task_id=task_id)

@app.route("/webhook", methods=["POST"])
def webhook():
    task_id = request.form.get("taskId")
    if not task_id:
        return "❌ taskId mancante", 400

    try:
        durata = int(request.form.get("durata", 0))
    except ValueError:
        return "❌ durata non valida", 400

    prefs = request.form.getlist("preferences")

    task_client.update_task({
        "taskId": task_id,
        "status": "COMPLETED",
        "outputData": {
            "durata": durata,
            "preferences": prefs
        }
    })
    return render_template("webhook_ack.html")

@app.route("/check_workflow_status/<workflow_id>")
def check_workflow_status(workflow_id):
    wf = executor.get_workflow(workflow_id=workflow_id, include_tasks=False)
    return jsonify({"status": wf.status})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)