from flask import Flask, request, render_template
from conductor.client.configuration.configuration import Configuration
from conductor.client.automator.task_executor import WorkflowExecutor

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("form.html")

@app.route("/start_workflow", methods=["POST"])
def start_workflow():
    preferences = request.form.getlist("preferences")
    durata = int(request.form.get("durata"))

    input_data = {
        "preferences": preferences,
        "durata": durata
    }

    executor = WorkflowExecutor(config)
    executor.start_workflow(name="tripmatch_workflow", input=input_data)

    return "Workflow avviato con successo!"