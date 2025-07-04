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
    if SessionState.get("workflow_completed"):
        show_completion_screen()
    elif not SessionState.has_itinerary():
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

                # USA LA STESSA LOGICA DEL DASHBOARD FUNZIONANTE
                itinerary_data = workflow_manager.wait_for_itinerary_task(
                    SessionState.get("workflow_id")
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
        extra_info = SessionState.get("extra_info")
        pdf_buffer = PDFGenerator.create_enhanced_pdf(itinerary_text, extra_info=extra_info)
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
        # Cache task per le azioni successive - STESSO PATTERN DEL DASHBOARD FUNZIONANTE
        # ShowItinerary viene cachato quando l'itinerario è disponibile
        workflow_manager.cache_task("ShowItinerary", "show_task_id")
        
        st.markdown("### 🎯 What would you like to do next?")
        
        # Pulsanti di azione
        col1, col2 = st.columns(2)
        
        with col1:
            # Pulsante di accettazione dell'itinerario
            show_task_id = SessionState.get("show_task_id")
            itinerary_confirmed = SessionState.get("itinerary_confirmed")
            
            if itinerary_confirmed:
                # Mostra stato confermato invece del pulsante
                st.success("✅ Itinerary Accepted!")
                st.info("You can now request additional information if needed.")
            elif st.button("✅ Accept This Itinerary", use_container_width=True):
                if show_task_id:
                    # COMPLETIAMO SOLO ShowItinerary, non l'intero workflow
                    if workflow_manager.complete_task(show_task_id, "COMPLETED", {
                        "selected_itinerary_index": 0,
                        "selected_itinerary": itinerary_text
                    }):
                        st.success("🎉 Itinerary accepted! You can now request additional info or plan a new trip.")
                        # Marca l'itinerario come confermato
                        SessionState.set("itinerary_confirmed", True)
                        st.rerun()
                    else:
                        st.error("❌ Error confirming itinerary.")
                else:
                    st.error("⚠️ ShowItinerary task ID not found.")
        
        with col2:
            # STESSO PATTERN DEL DASHBOARD FUNZIONANTE - AskforAddInfo_ref
            # Le opzioni per info aggiuntive sono disponibili solo dopo aver accettato l'itinerario
            itinerary_confirmed = SessionState.get("itinerary_confirmed")
            
            if not itinerary_confirmed:
                st.info("⏳ Additional info option will be available after accepting the itinerary")
            else:
                workflow_manager.cache_task("AskforAddInfo_ref", "request_confirmation_task_id")
                request_task_id = SessionState.get("request_confirmation_task_id")
                confirmation_response = SessionState.get("confirmation_response")
                
                # Se il task è attivo e l'utente non ha ancora risposto
                if request_task_id and confirmation_response is None:
                    st.subheader("❓ Request additional information?")
                    col_yes, col_no = st.columns(2)
                    with col_yes:
                        if st.button("Yes", key="confirm_yes", use_container_width=True):
                            if workflow_manager.complete_task(request_task_id, "COMPLETED", {"user_choice": "yes"}):
                                SessionState.set("confirmation_response", "Sì")
                                st.rerun()
                            else:
                                st.error("❌ Error requesting additional info.")
                    with col_no:
                        if st.button("No", key="confirm_no", use_container_width=True):
                            if workflow_manager.complete_task(request_task_id, "COMPLETED", {"user_choice": "no"}):
                                SessionState.set("confirmation_response", "No")
                                st.rerun()
                            else:
                                st.error("❌ Error declining additional info.")
                
                # Se l'utente ha già risposto, mostra la scelta
                elif confirmation_response:
                    st.info(f"Your choice: **{confirmation_response}**")
                else:
                    st.info("⏳ Waiting for additional info task to become available...")
        
        # GESTIONE INFO AGGIUNTIVE - NUOVO PATTERN CON ShowMoreInformation
        if SessionState.get("confirmation_response") == "Sì" and not SessionState.get("extra_info"):
            # Le info aggiuntive vengono dal task ShowMoreInformation (come ShowItinerary)
            extra_info_data = workflow_manager.wait_for_additional_info_task(
                SessionState.get("workflow_id")
            )
            if extra_info_data:
                SessionState.set("extra_info", extra_info_data)
                st.rerun()
        
        # Mostra info aggiuntive se disponibili
        if SessionState.get("extra_info"):
            st.subheader("ℹ️ Informazioni aggiuntive")
            st.markdown(SessionState.get("extra_info"))
            
            # Cache del task ShowMoreInformation per permettere l'accettazione
            workflow_manager.cache_task("ShowMoreInformation", "show_more_info_task_id")
            show_more_info_task_id = SessionState.get("show_more_info_task_id")
            
            # Pulsante per accettare le info aggiuntive
            if show_more_info_task_id and st.button("✅ Accept Additional Information", use_container_width=True):
                # Usa le info aggiuntive dallo stato della sessione
                current_extra_info = SessionState.get("extra_info")
                if workflow_manager.complete_task(show_more_info_task_id, "COMPLETED", {
                    "accepted": True,
                    "additional_info": current_extra_info
                }):
                    st.success("🎉 Additional information accepted!")
                    # Vai direttamente alla schermata di completamento
                    SessionState.set_step(3)
                    SessionState.set("workflow_completed", True)
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Error confirming additional information.")
        
        # Pulsanti finali
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            if st.button("🔄 Start New Trip Planning", use_container_width=True):
                SessionState.reset()
                st.rerun()
    
    except Exception as e:
        st.error(f"❌ Error displaying itinerary: {e}")

        if st.button("🔄 Restart Application", use_container_width=True):
            SessionState.reset()
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

def show_completion_screen():
    """Mostra la schermata di completamento e ringraziamento"""
    SessionState.set_step(3)
    
    st.markdown('<div class="custom-form-container">', unsafe_allow_html=True)
    
    # Header di completamento
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="color: #28a745; font-size: 2.5rem; margin-bottom: 1rem;">
            🎉 Trip Planning Complete!
        </h1>
        <h2 style="color: #667eea; font-size: 1.8rem; margin-bottom: 2rem;">
            Thank you for using TripMatch!
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Messaggio di ringraziamento
    st.markdown("""
    <div style="text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 15px; color: white; margin: 2rem 0;">
        <h3 style="margin-bottom: 1rem;">✈️ Your adventure awaits!</h3>
        <p style="font-size: 1.1rem; line-height: 1.6; margin-bottom: 1.5rem;">
            We've successfully created your personalized travel itinerary. 
            Your journey is now planned and ready to unfold!
        </p>
        <p style="font-size: 1rem; margin-bottom: 0;">
            Safe travels and have an amazing experience! 🌍
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Riepilogo del viaggio
    itinerary_data = SessionState.get("itinerary")
    if itinerary_data:
        # Mostra un estratto dell'itinerario
        itinerary_text = UIComponents.process_itinerary_data(itinerary_data)
        
        # Pulsante per scaricare PDF finale
        st.markdown("### 📄 Take Your Itinerary With You")
        extra_info = SessionState.get("extra_info")
        pdf_buffer = PDFGenerator.create_enhanced_pdf(itinerary_text, extra_info=extra_info)
        if pdf_buffer:
            st.download_button(
                label="📱 Download Your Complete Itinerary (PDF)",
                data=pdf_buffer,
                file_name=f"TripMatch_Itinerary_{uuid.uuid4().hex[:8]}.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary"
            )
    
    # Statistiche e ringraziamenti
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h4 style="color: #667eea;">🤖 AI-Powered</h4>
            <p>Personalized recommendations</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h4 style="color: #667eea;">⚡ Fast Planning</h4>
            <p>Instant itinerary generation</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h4 style="color: #667eea;">🎯 Tailored</h4>
            <p>Based on your preferences</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Pulsante per pianificare un nuovo viaggio
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🚀 Plan Another Trip", use_container_width=True, type="primary"):
            SessionState.reset()
            st.rerun()
        
        st.markdown("""
        <div style="text-align: center; margin-top: 2rem; color: #6c757d;">
            <p>Made with ❤️ by <strong>TripMatch</strong></p>
            <p style="font-size: 0.9rem;">Your AI Travel Planning Assistant</p>
        </div>
        """, unsafe_allow_html=True)
    
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