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

config = create_config()
task_client = OrkesTaskClient(configuration=config)
executor = WorkflowExecutor(configuration=config)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start_workflow", methods=["GET", "POST"])
def start_workflow():
    if request.method == "GET":
        return "❌ Questo endpoint supporta solo richieste POST.", 405

    run = executor.execute(
        name="checkout_workflow",
        version=1,
        workflow_input={}
    )
    return redirect(url_for("workflow_started", workflow_id=run.workflow_id))

@app.route("/workflow_started/<workflow_id>")
def workflow_started(workflow_id):
    return render_template("workflow_started.html", workflow_id=workflow_id, ui_host=config.ui_host)

@app.route("/check_workflow_status/<workflow_id>")
def check_workflow_status(workflow_id):
    try:
        wf = executor.get_workflow(workflow_id=workflow_id, include_tasks=False)
        return jsonify({"status": wf.status})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/form/<task_id>")
def form(task_id):
    return render_template("form.html", task_id=task_id)

@app.route("/complete_task", methods=["POST"])
def complete_task():
    task_id = request.form["taskId"]
    durata = request.form.get("durata", type=int)
    prefs = request.form.getlist("preferences")

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
    worker_id = "web_form_worker"
    task = task_client.poll(task_type="WaitUserRequest", worker_id=worker_id, timeout=10000)
    if task and task.get("taskId"):
        return redirect(url_for("form", task_id=task["taskId"]))
    else:
        return "<p>Nessun task disponibile al momento. Ricarica questa pagina fra qualche secondo.</p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)