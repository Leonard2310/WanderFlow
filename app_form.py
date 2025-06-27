from flask import Flask, request, render_template, redirect, url_for, jsonify
from conductor.client.configuration.configuration import Configuration, AuthenticationSettings
from conductor.client.workflow.executor.workflow_executor import WorkflowExecutor
from conductor.client.orkes.orkes_task_client import OrkesTaskClient
from dotenv import load_dotenv
import os
import time
import json
import uuid
import logging

logging.basicConfig(level=logging.INFO)  # Configurazione logging

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
    app.logger.info("Accesso alla pagina index")
    return render_template("index.html")

@app.route("/start_workflow", methods=["POST"])
def start_workflow():
    app.logger.info("Avvio workflow")
    run = executor.execute(
        name="TripMatch_BPA",
        version=2,
        workflow_input={}
    )

    app.logger.info(f"Workflow avviato: {run}")
    workflow_id = getattr(run, "workflow_id", None)
    app.logger.info(f"Workflow ID ottenuto: {workflow_id}")

    if not run or not workflow_id:
        app.logger.error("Errore nell'avvio workflow: workflow_id mancante")
        return "Errore nell'avvio workflow", 500

    return redirect(url_for("workflow_started", workflow_id=workflow_id))

@app.route("/workflow_started/<workflow_id>")
def workflow_started(workflow_id):
    app.logger.info(f"Workflow started page per workflow_id={workflow_id}")
    return render_template(
        "workflow_started.html",
        workflow_id=workflow_id,
        ui_host=UI_HOST
    )

@app.route("/wait_task/<workflow_id>")
def wait_task(workflow_id):
    app.logger.info(f"In attesa di task per workflow_id={workflow_id}")
    
    max_retries = 5
    retry_delay = 2  # secondi

    for attempt in range(max_retries):
        app.logger.debug(f"Attempt {attempt+1} per ottenere workflow con task, workflow_id={workflow_id}")
        wf = executor.get_workflow(workflow_id=workflow_id, include_tasks=True)
        details = []

        for t in wf.tasks:
            ref_name = getattr(t, "reference_task_name", None)
            status   = getattr(t, "status", None)
            tid      = getattr(t, "task_id", None)
            app.logger.debug(f"Task trovato: ref_name={ref_name}, status={status}, task_id={tid}")

            if ref_name == "WaitUserRequest" and status == "IN_PROGRESS" and tid:
                app.logger.info(f"Redirect al form per task_id={tid} e workflow_id={workflow_id}")
                return redirect(url_for("form", task_id=tid, workflow_id=workflow_id))

            details.append(f"{ref_name} ➞ {status} (id={tid})")

        time.sleep(retry_delay)  # aspetta prima di ritentare

    app.logger.warning(f"Nessun task disponibile dopo {max_retries} tentativi, workflow_id={workflow_id}")
    return (
        "<p>Nessun task disponibile al momento. Ricarica questa pagina fra qualche secondo.</p>"
        "<h3>Debug tasks:</h3><pre>"
        + "\n".join(details) +
        "</pre>"
    )

@app.route("/form/<task_id>")
def form(task_id):
    workflow_id = request.args.get("workflow_id")
    app.logger.info(f"Rendering form con task_id={task_id} e workflow_id={workflow_id}")
    return render_template("form.html", task_id=task_id, workflow_id=workflow_id)

@app.route("/webhook", methods=["POST"])
def webhook():
    task_id = request.form.get("taskId")
    workflow_id = request.form.get("workflowId")
    app.logger.info(f"Ricevuta chiamata webhook con taskId={task_id}, workflowId={workflow_id}")

    if not task_id or not workflow_id:
        app.logger.error("taskId o workflowId mancanti nel webhook")
        return "❌ taskId o workflowId mancante", 400

    try:
        durata = int(request.form.get("durata", 0))
        app.logger.info(f"Durata ricevuta: {durata}")
    except ValueError:
        app.logger.error("Valore durata non valido nel webhook")
        return "❌ durata non valida", 400

    prefs = request.form.getlist("preferences")
    app.logger.info(f"Preferenze ricevute: {prefs}")

    update_payload = {
        "taskId": task_id,
        "workflowInstanceId": workflow_id,
        "status": "COMPLETED",
        "outputData": {
            "durata": durata,
            "preferences": prefs
        }
    }
    app.logger.debug(f"Payload update_task: {update_payload}")

    try:
        task_client.update_task(update_payload)
        app.logger.info("Task aggiornato con successo")
    except Exception as e:
        app.logger.error(f"Errore durante update_task: {e}")
        return f"Errore aggiornando task: {e}", 500

    return render_template("webhook_ack.html")

@app.route("/check_workflow_status/<workflow_id>")
def check_workflow_status(workflow_id):
    app.logger.info(f"Check status workflow_id={workflow_id}")
    wf = executor.get_workflow(workflow_id=workflow_id, include_tasks=False)
    return jsonify({"status": wf.status})


# input web service
user_profiles = {}

@app.route("/input_webservice_endpoint", methods=["POST"])
def input_webservice_endpoint():
    data = request.get_json()

    durata = data.get("durata")
    preferences = data.get("preferences")

    # Genera un user ID unico ogni volta
    user_id = str(uuid.uuid4())

    # Salva il profilo in memoria
    user_profiles[user_id] = {
        "durata": durata,
        "preferences": preferences
    }

    app.logger.info(f"Nuovo profilo utente creato con ID {user_id}: durata={durata}, preferences={preferences}")

    return jsonify({
        "status": "success",
        "message": "Profilo utente salvato correttamente",
        "user_id": user_id,
        "user_profile": user_profiles[user_id]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)