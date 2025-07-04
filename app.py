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
    page_title="WanderFlow - Plan Your Adventure",
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
    elif not has_travel_content():
        show_preferences_form()
    else:
        show_itinerary_results()

def has_travel_content() -> bool:
    """Verifica se ci sono contenuti di viaggio disponibili (itinerario o opzioni)"""
    # Per viaggi lunghi: controlla se c'è un itinerario
    if SessionState.has_itinerary():
        return True
    
    # Per viaggi brevi: controlla se ci sono opzioni di viaggio
    if SessionState.get("travel_options"):
        return True
    
    return False

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
                
                # Salva la durata per determinare il flusso
                SessionState.set("trip_duration", duration)
                SessionState.set("is_short_trip", duration <= 3)

                # Determina quale task aspettare in base alla durata
                if duration <= 3:
                    # Viaggio breve: aspetta ChoiceTravelCity
                    travel_options = workflow_manager.wait_for_choice_travel_city_task(
                        SessionState.get("workflow_id")
                    )
                    if travel_options:
                        SessionState.set("travel_options", travel_options)
                        SessionState.set("choice_travel_city_task_id", travel_options["task_id"])
                        SessionState.set_step(2)
                        st.success("✅ Your travel options are ready!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Error generating travel options or timeout reached.")
                else:
                    # Viaggio lungo: aspetta ShowItinerary (logica esistente)
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
    
    # Controlla se è un viaggio breve o lungo
    is_short_trip = SessionState.get("is_short_trip", False)
    
    if is_short_trip:
        show_travel_options_selection()
    else:
        show_single_itinerary_results()
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_travel_options_selection():
    """Mostra le 3 opzioni di viaggio per viaggi brevi"""
    st.markdown("### 🏙️ Choose Your Perfect City Trip")
    
    try:
        travel_options = SessionState.get("travel_options")
        selected_option = SessionState.get("selected_travel_option")
        choice_task_completed = SessionState.get("choice_task_completed", False)
        
        if not travel_options:
            st.warning("No travel options found. Please go back to preferences.")
            if st.button("Back to Preferences", key="back_to_prefs_no_options"):
                SessionState.set_step(1)
                st.rerun()
            return
        
        # Se l'utente ha già selezionato un'opzione E il task è completato, mostra l'itinerario
        if selected_option and choice_task_completed:
            show_selected_itinerary()
            return
        
        # Se l'utente non ha ancora selezionato un'opzione, mostra le scelte
        if not selected_option:
            st.info("Please select one of the three travel options below:")
            
            # Mostra le 3 opzioni in colonne
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.subheader("🌟 Option 1")
                st.markdown(travel_options["itinerary1"])
                if st.button("Choose Option 1", key="option1", use_container_width=True):
                    select_travel_option(1, travel_options["itinerary1"])
            
            with col2:
                st.subheader("🌟 Option 2")
                st.markdown(travel_options["itinerary2"])
                if st.button("Choose Option 2", key="option2", use_container_width=True):
                    select_travel_option(2, travel_options["itinerary2"])
            
            with col3:
                st.subheader("🌟 Option 3")
                st.markdown(travel_options["itinerary3"])
                if st.button("Choose Option 3", key="option3", use_container_width=True):
                    select_travel_option(3, travel_options["itinerary3"])
        else:
            # L'utente ha selezionato ma il task non è ancora completato
            st.info("Processing your selection...")
            time.sleep(0.5)
            st.rerun()
    
    except Exception as e:
        st.error(f"❌ Error displaying travel options: {e}")
        if st.button("🔄 Restart Application", key="restart_travel_options", use_container_width=True):
            SessionState.reset()
            st.rerun()

def select_travel_option(option_number: int, itinerary_text: str):
    """Seleziona una delle opzioni di viaggio e completa il task"""
    choice_task_id = SessionState.get("choice_travel_city_task_id")
    
    if choice_task_id:
        # Completa il task ChoiceTravelCity con l'opzione selezionata
        success = workflow_manager.complete_task(choice_task_id, "COMPLETED", {
            "user_choice": f"option{option_number}",
            "selected_option": option_number,
            "selected_itinerary": itinerary_text
        })
        
        if success:
            # Aggiorna lo stato della sessione
            SessionState.set("selected_travel_option", option_number)
            SessionState.set("itinerary", itinerary_text)
            SessionState.set("choice_task_completed", True)
            st.success(f"🎉 Option {option_number} selected!")
            time.sleep(1)  # Breve pausa per mostrare il messaggio
            st.rerun()
        else:
            st.error("❌ Error selecting travel option. Please try again.")
    else:
        st.error("⚠️ Choice task ID not found. Please restart the workflow.")

def show_selected_itinerary():
    """Mostra l'itinerario selezionato e le opzioni successive"""
    selected_option = SessionState.get("selected_travel_option")
    itinerary_data = SessionState.get("itinerary")
    
    st.markdown(f"### 🌟 Your Selected Travel Option ({selected_option})")
    
    if not itinerary_data:
        st.warning("No itinerary found.")
        return
    
    # Mostra l'itinerario selezionato
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
    
    # Per viaggi brevi, usa la stessa logica di ShowItinerary ma senza il task
    show_itinerary_actions(itinerary_text, use_show_task=False)

def show_single_itinerary_results():
    """Mostra i risultati dell'itinerario per viaggi lunghi (logica originale)"""
    st.markdown("### 🌟 Your Personalized Travel Itinerary")
    
    try:
        itinerary_data = SessionState.get("itinerary")
        if not itinerary_data:
            st.warning("No itinerary found. Please go back to preferences.")
            if st.button("Back to Preferences"):
                SessionState.set_step(1)
                SessionState.set("itinerary", None)
                st.rerun()
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
        
        # Mostra azioni dell'itinerario
        show_itinerary_actions(itinerary_text, use_show_task=True)
    
    except Exception as e:
        st.error(f"❌ Error displaying itinerary: {e}")
        if st.button("🔄 Restart Application", use_container_width=True):
            SessionState.reset()
            st.rerun()

def show_itinerary_actions(itinerary_text: str, use_show_task: bool = True):
    """Mostra le azioni comuni per entrambi i tipi di itinerario"""
    st.markdown("### 🎯 What would you like to do next?")
    
    # Pulsanti di azione
    col1, col2 = st.columns(2)
    
    with col1:
        # Pulsante di accettazione dell'itinerario
        itinerary_confirmed = SessionState.get("itinerary_confirmed")
        
        if itinerary_confirmed:
            # Mostra stato confermato invece del pulsante
            st.success("✅ Itinerary Accepted!")
            st.info("You can now request additional information if needed.")
        elif st.button("✅ Accept This Itinerary", key="accept_itinerary", use_container_width=True):
            if use_show_task:
                # Per viaggi lunghi: usa ShowItinerary task
                workflow_manager.cache_task("ShowItinerary", "show_task_id")
                show_task_id = SessionState.get("show_task_id")
                if show_task_id:
                    if workflow_manager.complete_task(show_task_id, "COMPLETED", {
                        "selected_itinerary_index": 0,
                        "selected_itinerary": itinerary_text
                    }):
                        st.success("🎉 Itinerary accepted! You can now request additional info or plan a new trip.")
                        SessionState.set("itinerary_confirmed", True)
                        st.rerun()
                    else:
                        st.error("❌ Error confirming itinerary.")
                else:
                    st.error("⚠️ ShowItinerary task ID not found.")
            else:
                # Per viaggi brevi: non c'è ShowItinerary task, marca solo come confermato
                SessionState.set("itinerary_confirmed", True)
                st.success("🎉 Itinerary accepted! You can now request additional info or plan a new trip.")
                st.rerun()
    
    with col2:
        # Gestione richiesta informazioni aggiuntive
        show_additional_info_options()
    
    # Gestione info aggiuntive
    handle_additional_info()
    
    # Pulsanti finali
    show_final_buttons()

def show_additional_info_options():
    """Mostra le opzioni per richiedere informazioni aggiuntive"""
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
                if st.button("Yes", key="confirm_yes_main", use_container_width=True):
                    if workflow_manager.complete_task(request_task_id, "COMPLETED", {"user_choice": "yes"}):
                        SessionState.set("confirmation_response", "Yes")
                        st.rerun()
                    else:
                        st.error("❌ Error requesting additional info.")
            with col_no:
                if st.button("No", key="confirm_no_main", use_container_width=True):
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

def handle_additional_info():
    """Gestisce le informazioni aggiuntive"""
    
    # Se l'utente ha scelto "No", vai direttamente alla schermata di completamento
    if SessionState.get("confirmation_response") == "No":
        # Vai direttamente alla schermata di completamento senza aspettare info aggiuntive
        if not SessionState.get("workflow_completed"):
            st.success("🎉 Trip planning completed successfully!")
            SessionState.set_step(3)
            SessionState.set("workflow_completed", True)
            time.sleep(1)
            st.rerun()
        return
    
    # GESTIONE INFO AGGIUNTIVE - SOLO PER CHI HA SCELTO "YES"
    if SessionState.get("confirmation_response") == "Yes" and not SessionState.get("extra_info"):
        # Le info aggiuntive vengono dal task ShowMoreInformation
        extra_info_data = workflow_manager.wait_for_additional_info_task(
            SessionState.get("workflow_id")
        )
        if extra_info_data:
            SessionState.set("extra_info", extra_info_data)
            st.rerun()
    
    # Mostra info aggiuntive se disponibili (solo per chi ha scelto "Yes")
    if SessionState.get("extra_info"):
        st.subheader("ℹ️ Informazioni aggiuntive")
        st.markdown(SessionState.get("extra_info"))
        
        # Cache del task ShowMoreInformation per permettere l'accettazione
        workflow_manager.cache_task("ShowMoreInformation", "show_more_info_task_id")
        show_more_info_task_id = SessionState.get("show_more_info_task_id")
        
        # Pulsante per accettare le info aggiuntive
        if show_more_info_task_id and st.button("✅ Accept Additional Information", key="accept_additional_info", use_container_width=True):
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
                st.rerun()
            else:
                st.error("❌ Error confirming additional information.")

def show_final_buttons():
    """Mostra i pulsanti finali"""
    # Pulsanti finali
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("🔄 Start New Trip Planning", key="restart_final", use_container_width=True):
            SessionState.reset()
            st.rerun()

def show_completion_screen():
    """Mostra la schermata di completamento e ringraziamento"""
    SessionState.set_step(3)
    
    # Mostra la celebrazione statica
    UIComponents.show_travel_celebration()
    
    st.markdown('<div class="custom-form-container">', unsafe_allow_html=True)
    
    # Header di completamento
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="color: #28a745; font-size: 2.5rem; margin-bottom: 1rem;">
            🎉 Trip Planning Complete!
        </h1>
        <h2 style="color: #667eea; font-size: 1.8rem; margin-bottom: 2rem;">
            Thank you for using WanderFlow!
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Messaggio di ringraziamento
    st.markdown("""
    <div class="completion-banner" style="text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 15px; margin: 2rem 0;">
        <h3 class="completion-title" style="margin-bottom: 1rem; color: #FFFFFF !important; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">✈️ Your adventure awaits!</h3>
        <p class="completion-text" style="font-size: 1.1rem; line-height: 1.6; margin-bottom: 1.5rem; color: #FFFFFF !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">
            We've successfully created your personalized travel itinerary. 
            Your journey is now planned and ready to unfold!
        </p>
        <p class="completion-text" style="font-size: 1rem; margin-bottom: 0; color: #FFFFFF !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">
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
                file_name=f"WanderFlow_Itinerary_{uuid.uuid4().hex[:8]}.pdf",
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