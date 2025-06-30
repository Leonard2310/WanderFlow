# dashboard_streamlit.py
import os, time, uuid
import streamlit as st
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import json

from dotenv import load_dotenv

from conductor.client.configuration.configuration import (
    Configuration, AuthenticationSettings
)
from conductor.client.workflow.executor.workflow_executor import WorkflowExecutor
from conductor.client.orkes.orkes_task_client import OrkesTaskClient

# ---------------- CONFIG ORKES ----------------
@st.cache_resource
def create_clients():
    load_dotenv("credentials.env")
    auth = AuthenticationSettings(
        key_id=os.getenv("CONDUCTOR_AUTH_KEY"),
        key_secret=os.getenv("CONDUCTOR_AUTH_SECRET")
    )
    cfg = Configuration(
        server_api_url=os.getenv("CONDUCTOR_SERVER_URL"),
        authentication_settings=auth
    )
    return WorkflowExecutor(configuration=cfg), OrkesTaskClient(configuration=cfg)

executor, task_client = create_clients()

# ---------------- SESSION STATE ---------------
defaults = {
    "workflow_id": None,
    "pref_task_id": None,
    "show_task_id": None,
    "choice_task_id": None,
    "itinerary": None,
    "extra_requested": False,
    "extra_info": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------------- HELPER ----------------------
def fetch_task_by_ref(wf_id: str, ref_name: str):
    """Restituisce il primo task con reference `ref_name` in stato SCHEDULED/IN_PROGRESS."""
    wf = executor.get_workflow(workflow_id=wf_id, include_tasks=True)
    for t in wf.tasks:
        if t.reference_task_name == ref_name and t.status in ("SCHEDULED", "IN_PROGRESS"):
            return t
    return None

def wait_for_output_key(wf_id: str, key: str, msg: str):
    with st.spinner(msg):
        while True:
            wf = executor.get_workflow(workflow_id=wf_id, include_tasks=False)
            if wf.output and wf.output.get(key):
                return wf.output[key]
            time.sleep(2)

def complete_task(task_id: str, status="COMPLETED", output=None):
    """
    Chiude (o aggiorna) un task SIMPLE con asyncComplete=true.
    Deve prima fare il poll per poterlo aggiornare.
    """
    task = task_client.get_task(task_id)
    task_type = task.task_type  # ✅ usa l’attributo, non la chiave

    # Fai il poll per acquisire il task
    task_client.poll_task(task_type=task_type, worker_id="streamlit_ui")

    # Completa il task
    task_client.update_task({
        "taskId": task_id,
        "workflowInstanceId": st.session_state.workflow_id,
        "workerId": "streamlit_ui",
        "status": status,
        "outputData": output or {}
    })

def cache_task(ref_name, state_key):
    if st.session_state[state_key] is None and st.session_state.workflow_id:
        t = fetch_task_by_ref(st.session_state.workflow_id, ref_name)
        if t:
            st.session_state[state_key] = t.task_id

def wait_for_itinerary_task(wf_id):
    with st.spinner("Elaboro itinerario…"):
        while True:
            t = fetch_task_by_ref(wf_id, "ShowItinerary")
            if t:
                # nelle versioni più recenti è t.input_data, in quelle vecchie t.inputData
                return t.input_data["itinerary"]
            time.sleep(2)

def build_itinerary_pdf(itinerary_text: str) -> BytesIO:
    """
    Crea un PDF in memoria con ReportLab e restituisce il buffer BytesIO.
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Titolo
    c.setFont("Helvetica-Bold", 18)
    c.drawString(40, height - 60, "Itinerario di viaggio")

    # Corpo (split per evitare testo fuori pagina)
    c.setFont("Helvetica", 11)
    y = height - 100
    for line in itinerary_text.split("\n"):
        c.drawString(40, y, line)
        y -= 15
        if y < 40:          # vai a pagina nuova se serve
            c.showPage()
            y = height - 60
    c.save()

    buffer.seek(0)
    return buffer

# ---------------- SIDEBAR ---------------------
st.sidebar.title("TripMatch 🧳")

if st.sidebar.button("Avvia nuovo workflow"):
    run = executor.execute(name="TripMatch_BPA", version=8, workflow_input={})
    for k in defaults:
        st.session_state[k] = defaults[k]                  # reset stato
    st.session_state.workflow_id = run.workflow_id
    st.sidebar.success(f"Workflow {run.workflow_id} avviato ✅")
    st.rerun()

# ---------------- MAIN ------------------------
st.title("TripMatch – Pianifica la tua avventura 🌍")

if not st.session_state.workflow_id:
    st.info("Premi *Avvia nuovo workflow* nel menu laterale per iniziare.")
    st.stop()

# 1️⃣  --- UserPreferences ---
cache_task("UserPreferences", "pref_task_id")
if st.session_state.pref_task_id and st.session_state.itinerary is None:
    with st.form("pref_form"):
        durata  = st.number_input("Durata (giorni)", min_value=1, value=7)
        periodo = st.date_input("Periodo")

        st.markdown("### Tipologia di meta:")
        metas = [m for m in ["natura","città","mare","montagna"]
                 if st.checkbox(m.capitalize(), key=f"meta_{m}")]

        st.markdown("### Nazione preferita:")
        # (lista paesi abbreviata per brevità ⇣)
        countries = {
            "Europa": ["Italia","Francia","Spagna","Germania","Grecia","Portogallo",
                       "Regno Unito","Malta","Paesi Bassi","Svizzera","Austria","Norvegia",
                       "Svezia","Finlandia","Irlanda","Polonia","Croazia",
                       "Repubblica Ceca","Ungheria"],
            "Asia": ["Giappone","Cina","Thailandia","India","Indonesia","Vietnam",
                     "Corea del Sud","Filippine","Singapore","Maldive","Nepal","Sri Lanka"],
            "Africa": ["Egitto","Marocco","Sudafrica","Kenya","Tanzania",
                       "Mauritius","Madagascar","Tunisia","Namibia"],
            "America del Nord": ["Stati Uniti","Canada","Messico","Cuba","Repubblica Dominicana"],
            "America Centrale & Sud": ["Colombia","Perù","Cile","Argentina","Brasile","Uruguay",
                                       "Ecuador","Costa Rica","Panama"],
            "Oceania": ["Australia","Nuova Zelanda","Figi","Samoa","Polinesia Francese"],
            "Medio Oriente": ["Emirati Arabi Uniti","Israele","Giordania","Turchia","Qatar"]
        }
        sel = st.selectbox(
            "Seleziona una nazione",
            [""] + [f"{reg} – {c}" for reg, cl in countries.items() for c in cl]
        )
        nazione = sel.split(" – ")[-1] if " – " in sel else None

        st.markdown("### Tipo di vacanza:")
        tipi = [t for t in ["relax","villeggiatura","avventura","cultura","gastronomia"]
                if st.checkbox(t.capitalize(), key=f"tipo_{t}")]

        inviato = st.form_submit_button("Invia preferenze")

    if inviato:
        prefs = [periodo.isoformat()] + metas + ([nazione] if nazione else []) + tipi
        complete_task(st.session_state.pref_task_id, "COMPLETED",
                      {"durata": durata, "preferences": prefs})
        st.success("Preferenze inviate ✅")

        st.session_state.itinerary = wait_for_output_key(
            st.session_state.workflow_id, "itinerary",
            "Elaboro itinerario…"
        )
        st.rerun()

# 2️⃣  --- Itinerary display & choice ---

if st.session_state.itinerary:
    st.subheader("🌟 Itinerario proposto")
    st.markdown(st.session_state.itinerary)

    pdf_buffer = build_itinerary_pdf(st.session_state.itinerary)
    st.download_button(
        label="📄 Scarica PDF",
        data=pdf_buffer,
        file_name="itinerario.pdf",
        mime="application/pdf",
    )

    cache_task("ShowItinerary", "show_task_id")

    # Il planner a volte restituisce JSON con più itinerari.
    try:
        itineraries = json.loads(st.session_state.itinerary)
    except json.JSONDecodeError:
        itineraries = None

    if isinstance(itineraries, list) and len(itineraries) > 1:
        st.subheader("🌟 Scegli il tuo itinerario preferito")
        selected = st.radio(
            "Seleziona un itinerario:",
            [f"Itinerario {i + 1}" for i in range(len(itineraries))],
            index=0,
        )
        selected_idx = int(selected.split(" ")[1]) - 1
        selected_itinerary = itineraries[selected_idx]

        st.markdown("### ✨ Itinerario selezionato")
        st.markdown(selected_itinerary)

        pdf_buffer = build_itinerary_pdf(selected_itinerary)
        st.download_button(
            label="📄 Scarica PDF",
            data=pdf_buffer,
            file_name=f"itinerario_{selected_idx + 1}.pdf",
            mime="application/pdf",
        )

        if st.button("Conferma scelta"):
            complete_task(
                st.session_state.show_task_id,
                "COMPLETED",
                {
                    "selected_itinerary_index": selected_idx,
                    "selected_itinerary": selected_itinerary,
                },
            )
            st.success("Itinerario confermato ✅")
            st.session_state.itinerary = selected_itinerary  # keep for later
            st.rerun()
    else:
        itinerary_text = (
            itineraries if isinstance(itineraries, str) else itineraries[0] if itineraries else st.session_state.itinerary
        )
        st.markdown("### ✨ Itinerario proposto")
        st.markdown(itinerary_text)

        pdf_buffer = build_itinerary_pdf(itinerary_text)
        st.download_button(
            label="📄 Scarica PDF",
            data=pdf_buffer,
            file_name="itinerario.pdf",
            mime="application/pdf",
        )

        if st.button("Accetta itinerario"):
            complete_task(
                st.session_state.show_task_id,
                "COMPLETED",
                {
                    "selected_itinerary_index": 0,
                    "selected_itinerary": itinerary_text,
                },
            )
            st.success("Itinerario confermato ✅")
            st.session_state.itinerary = itinerary_text
            st.rerun()

# 3️⃣  --- Extra info button (only if GetUserChoice exists) ---

cache_task("GetUserChoice", "choice_task_id")
btn_disabled = st.session_state.choice_task_id is None or st.session_state.extra_requested

if st.sidebar.button("Richiedi info aggiuntive", disabled=btn_disabled):
    correlation_id = str(uuid.uuid4())
    complete_task(
        st.session_state.choice_task_id,
        "COMPLETED",
        {"extra_request_id": correlation_id},
    )
    st.session_state.extra_requested = True
    st.rerun()

# 4️⃣  --- Wait for extra_info ---

if st.session_state.extra_requested and not st.session_state.extra_info:
    st.session_state.extra_info = wait_for_output_key(
        st.session_state.workflow_id,
        "extra_info",
        "Recupero informazioni aggiuntive…",
    )
    st.rerun()

if st.session_state.extra_info:
    st.subheader("ℹ️ Informazioni aggiuntive")
    st.markdown(st.session_state.extra_info)
