import os
import time
import uuid
import json
from typing import Optional, Dict, Any

import streamlit as st
import folium
from streamlit_folium import st_folium

from dotenv import load_dotenv
from conductor.client.configuration.configuration import (
    Configuration, AuthenticationSettings
)
from conductor.client.workflow.executor.workflow_executor import WorkflowExecutor
from conductor.client.orkes.orkes_task_client import OrkesTaskClient

# Import dei moduli personalizzati
from components.ui_components import UIComponents
from components.map_components import MapComponents
from components.workflow_manager import WorkflowManager
from utils.session_state import SessionState
from utils.pdf_generator import PDFGenerator
from config.app_config import AppConfig

# ================= CONFIGURAZIONE STREAMLIT =================
st.set_page_config(
    page_title="TripMatch - Plan Your Adventure",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Applica CSS personalizzato
UIComponents.apply_custom_css()

# ================= CONFIGURAZIONE ORKES =================
@st.cache_resource
def create_conductor_clients():
    """Crea e configura i client Orkes, memorizzandoli nella cache."""
    load_dotenv("credentials.env")

    key_id = os.getenv("CONDUCTOR_AUTH_KEY")
    key_secret = os.getenv("CONDUCTOR_AUTH_SECRET")
    server_url = os.getenv("CONDUCTOR_SERVER_URL")

    if not all([key_id, key_secret, server_url]):
        st.error("Missing Conductor API credentials in 'credentials.env'. Please check your .env file.")
        return None, None

    auth = AuthenticationSettings(
        key_id=key_id,
        key_secret=key_secret
    )

    cfg = Configuration(
        server_api_url=server_url,
        authentication_settings=auth
    )

    return WorkflowExecutor(configuration=cfg), OrkesTaskClient(configuration=cfg)

executor, task_client = create_conductor_clients()

if executor is None or task_client is None:
    st.stop()

# Inizializza l'istanza di WorkflowManager
workflow_manager = WorkflowManager(executor, task_client)

# ================= INIZIALIZZAZIONE DELLO STATO DELLA SESSIONE =================
SessionState.initialize()

# ================= INTERFACCIA PRINCIPALE =================
def main():
    """Funzione principale dell'applicazione"""
    
    # Header
    UIComponents.render_header()
    
    # Indicatore di progresso
    UIComponents.create_step_indicator(SessionState.get_current_step())
    
    # Mostra la schermata di benvenuto se il workflow non è iniziato
    if not SessionState.is_workflow_started():
        show_welcome_screen()
        return
    
    # Routing basato sullo stato del workflow
    if not SessionState.has_itinerary():
        show_preferences_form()
    else:
        show_itinerary_results()

def show_welcome_screen():
    """Mostra la schermata di benvenuto e avvia il workflow"""
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 3rem 0;">
            <h2>✈️ Ready for your next adventure?</h2>
            <p style="font-size: 1.2rem; color: #6c757d; margin-bottom: 2rem;">
                Discover personalized travel itineraries tailored just for you!
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Uso di un container per evitare duplicazioni
        with st.container():
            if st.button("🚀 Start Planning Your Trip", key="start_btn", use_container_width=True):
                with st.spinner("Starting your trip planning workflow..."):
                    try:
                        # Usa il metodo start_workflow di WorkflowManager
                        wf_id = workflow_manager.start_workflow()
                        if wf_id:
                            SessionState.reset()
                            SessionState.set("workflow_id", wf_id)
                            SessionState.set_step(1)
                            # Ricarica la pagina senza delay o messaggi aggiuntivi
                            st.rerun()
                        else:
                            st.error("Errore nell'avvio del workflow")
                    except Exception as e:
                        st.error(f"Errore generale nell'avvio del workflow: {e}")

def show_preferences_form():
    SessionState.set_step(1)

    workflow_manager.cache_task("UserPreferences", "pref_task_id")

    if not SessionState.get("pref_task_id"):
        st.warning("⏳ In attesa del task delle preferenze dal workflow...")
        
        # NUOVO: Controlla se il workflow è bloccato
        if SessionState.get("workflow_id"):
            stuck_analysis = workflow_manager.is_workflow_stuck(SessionState.get("workflow_id"))
            if stuck_analysis.get("is_stuck"):
                st.error(f"🚫 **Workflow Blocked:** {stuck_analysis.get('reason')}")
                if stuck_analysis.get("has_unhandled_duration"):
                    st.info("💡 **Solution:** Please start a new trip with a duration of 3 days or fewer, or 5 days or more.")
                    if st.button("🔄 Start New Trip", key="stuck_restart"):
                        SessionState.reset()
                        st.rerun()
        return

    st.markdown('<div class="custom-form-container">', unsafe_allow_html=True)
    st.markdown("### 🎯 Tell us about your dream trip")

    duration, period = UIComponents.render_duration_section()
    
    # NUOVO: Avviso per durata di 4 giorni
    if duration == 4:
        st.warning("⚠️ **Note:** The current workflow supports trips of 3 days or fewer (city tours) or 5+ days (regional exploration). 4-day trips are not currently supported.")
    
    selected_destinations = UIComponents.render_destination_types()

    # Qui prendi la selezione senza effetto collaterale
    selected_country = UIComponents.render_country_selection()

    # Renderizza la mappa interattiva solo se è selezionato un paese
    # Se selected_country è None o vuoto, la mappa scompare completamente
    if selected_country:
        MapComponents.render_interactive_map(selected_country)

    selected_styles = UIComponents.render_vacation_styles()

    with st.form("preferences_form", clear_on_submit=False):
        submitted = st.form_submit_button("✨ Find My Perfect Trip!", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    if submitted:
        if not period:
            st.error("⚠️ Please select a travel period for your trip.")
            return

        if not selected_destinations and not selected_styles:
            st.error("⚠️ Please select at least one destination type or vacation style.")
            return

        # NUOVO: Controllo per durata di 4 giorni
        if duration == 4:
            st.warning("⚠️ The current workflow doesn't support exactly 4-day trips. Please choose 3 days or fewer (for city tours) or 5+ days (for regional exploration).")
            return

        # Ora il paese selezionato lo usi direttamente qui, senza dipendere da SessionState
        preferences = [period.isoformat()]
        preferences.extend(selected_destinations)
        if selected_country:
            preferences.append(selected_country)
        preferences.extend(selected_styles)

        pref_task_id = SessionState.get("pref_task_id")
        if pref_task_id:
            if workflow_manager.complete_task(pref_task_id, "COMPLETED", {
                "durata": duration,
                "preferences": preferences
            }):
                st.success("🎉 Preferences submitted successfully!")

                itinerary_data = workflow_manager.wait_for_output_key(
                    SessionState.get("workflow_id"),
                    "itinerary",
                    "🤖 Creating your personalized itinerary..."
                )

                if itinerary_data:
                    SessionState.set("itinerary", itinerary_data)
                    SessionState.set_step(2)
                    st.success("✅ Your itinerary is ready!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Error generating itinerary or timeout reached.")
            else:
                st.error("❌ Error submitting preferences to workflow.")
        else:
            st.error("⚠️ Preference task ID not found.")

def show_itinerary_results():
    """Mostra i risultati dell'itinerario e le opzioni successive"""
    SessionState.set_step(2)
    
    st.markdown('<div class="custom-form-container">', unsafe_allow_html=True)
    st.markdown("### 🌟 Your Personalized Travel Itinerary")
    
    try:
        itinerary_data = SessionState.get("itinerary")
        if not itinerary_data:
            st.warning("No itinerary found. Please go back to preferences.")
            if st.button("Back to Preferences"):
                SessionState.set_step(1)
                SessionState.set("itinerary", None)
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            return
        
        # Gestione e visualizzazione itinerario
        itinerary_text = UIComponents.process_itinerary_data(itinerary_data)
        UIComponents.render_itinerary_display(itinerary_text)
        
        # Pulsante per scaricare PDF
        pdf_buffer = PDFGenerator.create_enhanced_pdf(itinerary_text)
        if pdf_buffer:
            st.download_button(
                label="📄 Download PDF Itinerary",
                data=pdf_buffer,
                file_name=f"itinerary_{uuid.uuid4().hex[:8]}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        
        # Cache task per le azioni successive - STESSO PATTERN DEL DASHBOARD FUNZIONANTE
        # ShowItinerary viene cachato quando l'itinerario è disponibile
        workflow_manager.cache_task("ShowItinerary", "show_task_id")
        
        # GetUserChoice viene sempre cachato (come nel dashboard.py)
        workflow_manager.cache_task("GetUserChoice", "choice_task_id")
        
        st.markdown("### 🎯 What would you like to do next?")
        
        # Mostra stato corrente per debug
        show_task_id = SessionState.get("show_task_id")
        choice_task_id = SessionState.get("choice_task_id")
        
        status_info = f"""
        **Current Status:** 
        - ShowItinerary Task: {'✅ Found' if show_task_id else '❌ Not found'}
        - GetUserChoice Task: {'✅ Found' if choice_task_id else '❌ Not found'}
        """
        
        # Se ShowItinerary è trovato ma GetUserChoice no, mostra pulsante di ricerca
        if show_task_id and not choice_task_id:
            status_info += "\n\n⚠️ **Note:** You need to accept the itinerary first to unlock additional options."
        
        st.markdown(status_info)
        
        # Pulsanti di azione
        col1, col2 = st.columns(2)
        
        with col1:
            show_task_id = SessionState.get("show_task_id")
            if st.button("✅ Accept This Itinerary", use_container_width=True):
                if show_task_id:
                    # STESSO APPROCCIO DEL DASHBOARD FUNZIONANTE
                    if workflow_manager.complete_task(show_task_id, "COMPLETED", {
                        "selected_itinerary_index": 0,
                        "selected_itinerary": itinerary_text
                    }):
                        st.success("🎉 Itinerary confirmed! Have an amazing trip!")
                        # Mantieni l'itinerario per uso futuro (come nel dashboard)
                        SessionState.set("itinerary", itinerary_text)
                        SessionState.set_step(3)
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Error confirming itinerary.")
                else:
                    st.error("⚠️ ShowItinerary task ID not found.")
        
        with col2:
            # STESSO PATTERN DEL DASHBOARD FUNZIONANTE
            choice_task_id = SessionState.get("choice_task_id")
            btn_disabled = (choice_task_id is None or SessionState.get("extra_requested", False))
            
            if st.button("ℹ️ Request Additional Info", 
                        disabled=btn_disabled, 
                        use_container_width=True):
                if choice_task_id:
                    correlation_id = str(uuid.uuid4())
                    if workflow_manager.complete_task(choice_task_id, "COMPLETED", {
                        "extra_request_id": correlation_id
                    }):
                        SessionState.set("extra_requested", True)
                        st.rerun()
                    else:
                        st.error("❌ Error requesting additional info.")
                else:
                    st.error("⚠️ GetUserChoice task ID not found.")
        
        # Gestione info aggiuntive (seguendo il pattern dashboard.py)
        if SessionState.get("extra_requested", False) and not SessionState.get("extra_info"):
            extra_info_data = workflow_manager.wait_for_output_key(
                SessionState.get("workflow_id"),
                "extra_info",
                "📚 Gathering additional travel information..."
            )
            if extra_info_data:
                SessionState.set("extra_info", extra_info_data)
                st.rerun()
        
        # Mostra info aggiuntive
        if SessionState.get("extra_info"):
            st.markdown("### 📚 Additional Travel Information")
            st.info(SessionState.get("extra_info"))
        
        # Pulsante per ricominciare
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("🔄 Start New Trip Planning", use_container_width=True):
                SessionState.reset()
                st.rerun()
        
        with col3:
            if st.button("🔍 Debug Workflow", use_container_width=True):
                debug_info = workflow_manager.get_workflow_debug_info(SessionState.get("workflow_id"))
                st.json(debug_info)
                
                # Debug specifico per il problema della durata
                st.markdown("### 🔧 Switch Logic Debug")
                switch_debug = workflow_manager.debug_workflow_switch_logic(SessionState.get("workflow_id"))
                st.json(switch_debug)
    
    except Exception as e:
        st.error(f"❌ Error displaying itinerary: {e}")

        if st.button("🔄 Restart Application", use_container_width=True):
            SessionState.reset()
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ================= SIDEBAR E FOOTER =================
def show_sidebar_info():
    """Mostra informazioni nella sidebar"""
    UIComponents.render_sidebar()

def show_footer():
    """Mostra il footer dell'applicazione"""
    UIComponents.render_footer()

# ================= ESECUZIONE PRINCIPALE =================
if __name__ == "__main__":
    try:
        # Mostra sidebar
        show_sidebar_info()
        
        # Esegui l'applicazione principale
        main()
        
        # Mostra footer
        show_footer()
        
    except Exception as e:
        st.error(f"🚨 An unhandled application error occurred: {e}")
        if hasattr(UIComponents, 'handle_workflow_error'):
            UIComponents.handle_workflow_error()
        st.exception(e)