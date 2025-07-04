"""
WanderFlow - AI-Powered Travel Planning Application

This is the main application file for WanderFlow, an intelligent travel planning system
that uses Orkes Conductor workflows to generate personalized travel itineraries.

The application provides:
- Interactive travel preference collection
- AI-powered itinerary generation
- Country selection with interactive maps
- PDF export functionality
- Support for both short trips (≤3 days) and long trips (≥5 days)
"""

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

# Import custom modules
from components.ui_components import UIComponents
from components.map_components import MapComponents
from components.workflow_manager import WorkflowManager
from utils.session_state import SessionState
from utils.pdf_generator import PDFGenerator
from config.app_config import AppConfig

# ================= STREAMLIT CONFIGURATION =================
st.set_page_config(
    page_title="WanderFlow - Plan Your Adventure",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply custom CSS styling
UIComponents.apply_custom_css()

# ================= ORKES CONDUCTOR CONFIGURATION =================
@st.cache_resource
def create_conductor_clients():
    """
    Create and configure Orkes Conductor clients with authentication.
    
    This function initializes the workflow executor and task client needed
    to interact with the Orkes Conductor service. The clients are cached
    to avoid recreation on every app reload.
    
    Returns:
        tuple: A tuple containing (WorkflowExecutor, OrkesTaskClient) instances,
               or (None, None) if configuration fails
    """
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

# Initialize WorkflowManager instance
workflow_manager = WorkflowManager(executor, task_client)

# ================= SESSION STATE INITIALIZATION =================
SessionState.initialize()

# ================= MAIN APPLICATION INTERFACE =================
def main():
    """
    Main application function that handles the primary workflow routing.
    
    This function manages the overall application flow, displaying different
    screens based on the current workflow state. It handles:
    - Welcome screen for new users
    - Preferences form for trip configuration
    - Itinerary results display
    - Completion screen
    """
    # Render header
    UIComponents.render_header()
    
    # Display progress indicator
    UIComponents.create_step_indicator(SessionState.get_current_step())
    
    # Show welcome screen if workflow hasn't started
    if not SessionState.is_workflow_started():
        show_welcome_screen()
        return
    
    # Route based on workflow state
    if SessionState.get("workflow_completed"):
        show_completion_screen()
    elif not has_travel_content():
        show_preferences_form()
    else:
        show_itinerary_results()

def has_travel_content() -> bool:
    """
    Check if travel content (itinerary or travel options) is available.
    
    This function determines whether the user has received travel content
    that can be displayed, supporting both long trips (itineraries) and
    short trips (travel options).
    
    Returns:
        bool: True if travel content is available, False otherwise
    """
    # For long trips: check if itinerary exists
    if SessionState.has_itinerary():
        return True
    
    # For short trips: check if travel options exist
    if SessionState.get("travel_options"):
        return True
    
    return False

def show_welcome_screen():
    """
    Display the welcome screen and handle workflow initialization.
    
    This function shows the initial landing page where users can start
    their trip planning journey. When the user clicks the start button,
    it initializes a new workflow instance.
    """
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
        
        # Use container to avoid duplications
        with st.container():
            if st.button("🚀 Start Planning Your Trip", key="start_btn", use_container_width=True):
                with st.spinner("Starting your trip planning workflow..."):
                    try:
                        # Use WorkflowManager's start_workflow method
                        wf_id = workflow_manager.start_workflow()
                        if wf_id:
                            SessionState.reset()
                            SessionState.set("workflow_id", wf_id)
                            SessionState.set_step(1)
                            st.rerun()
                        else:
                            st.error("Error starting workflow")
                    except Exception as e:
                        st.error(f"General error starting workflow: {e}")

def show_preferences_form():
    """
    Display the travel preferences form for user input.
    
    This function renders the main preferences collection interface where
    users can specify their travel duration, destinations, country preferences,
    and vacation styles. It handles form validation and workflow task completion.
    """
    SessionState.set_step(1)

    workflow_manager.cache_task("UserPreferences", "pref_task_id")

    if not SessionState.get("pref_task_id"):
        st.warning("⏳ Waiting for preferences task from workflow...")
        
        # Check if workflow is stuck
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
    
    # Warning for 4-day duration
    if duration == 4:
        st.warning("⚠️ **Note:** The current workflow supports trips of 3 days or fewer (city tours) or 5+ days (regional exploration). 4-day trips are not currently supported.")
    
    selected_destinations = UIComponents.render_destination_types()

    # Get country selection without side effects
    selected_country = UIComponents.render_country_selection()

    # Render interactive map only if a country is selected
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

        # Check for 4-day duration
        if duration == 4:
            st.warning("⚠️ The current workflow doesn't support exactly 4-day trips. Please choose 3 days or fewer (for city tours) or 5+ days (for regional exploration).")
            return

        # Use the selected country directly here, without depending on SessionState
        preferences = [period.strftime("%d/%m/%Y")]
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
                
                # Save duration to determine flow
                SessionState.set("trip_duration", duration)
                SessionState.set("is_short_trip", duration <= 3)

                # Determine which task to wait for based on duration
                if duration <= 3:
                    # Short trip: wait for ChoiceTravelCity
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
                    # Long trip: wait for ShowItinerary (existing logic)
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
    """
    Display itinerary results and subsequent options.
    
    This function routes between short trip options (≤3 days) and long trip
    itineraries (≥5 days), displaying the appropriate interface based on
    the trip duration.
    """
    SessionState.set_step(2)
    
    st.markdown('<div class="custom-form-container">', unsafe_allow_html=True)
    
    # Check if it's a short or long trip
    is_short_trip = SessionState.get("is_short_trip", False)
    
    if is_short_trip:
        show_travel_options_selection()
    else:
        show_single_itinerary_results()
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_travel_options_selection():
    """
    Display the 3 travel options for short trips (≤3 days).
    
    This function handles the display and selection of travel options for
    short trips, allowing users to choose from 3 different city tour options
    generated by the workflow.
    """
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
        
        # If user has already selected an option AND the task is completed, show the itinerary
        if selected_option and choice_task_completed:
            show_selected_itinerary()
            return
        
        # If user hasn't selected an option yet, show the choices
        if not selected_option:
            st.info("Please select one of the three travel options below:")
            
            # Display the 3 options in columns
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
            # User has selected but task is not yet completed
            st.info("Processing your selection...")
            time.sleep(0.5)
            st.rerun()
    
    except Exception as e:
        st.error(f"❌ Error displaying travel options: {e}")
        if st.button("🔄 Restart Application", key="restart_travel_options", use_container_width=True):
            SessionState.reset()
            st.rerun()

def select_travel_option(option_number: int, itinerary_text: str):
    """
    Select one of the travel options and complete the workflow task.
    
    Args:
        option_number (int): The selected option number (1, 2, or 3)
        itinerary_text (str): The itinerary text for the selected option
    """
    choice_task_id = SessionState.get("choice_travel_city_task_id")
    
    if choice_task_id:
        # Complete the ChoiceTravelCity task with the selected option
        success = workflow_manager.complete_task(choice_task_id, "COMPLETED", {
            "user_choice": f"option{option_number}",
            "selected_option": option_number,
            "selected_itinerary": itinerary_text
        })
        
        if success:
            # Update session state
            SessionState.set("selected_travel_option", option_number)
            SessionState.set("itinerary", itinerary_text)
            SessionState.set("choice_task_completed", True)
            st.success(f"🎉 Option {option_number} selected!")
            time.sleep(1)
            st.rerun()
        else:
            st.error("❌ Error selecting travel option. Please try again.")
    else:
        st.error("⚠️ Choice task ID not found. Please restart the workflow.")

def show_selected_itinerary():
    """
    Display the selected itinerary and subsequent options for short trips.
    
    This function shows the user's selected travel option and provides
    actions like downloading PDF and requesting additional information.
    """
    selected_option = SessionState.get("selected_travel_option")
    itinerary_data = SessionState.get("itinerary")
    
    st.markdown(f"### 🌟 Your Selected Travel Option ({selected_option})")
    
    if not itinerary_data:
        st.warning("No itinerary found.")
        return
    
    # Display the selected itinerary
    itinerary_text = UIComponents.process_itinerary_data(itinerary_data)
    UIComponents.render_itinerary_display(itinerary_text)
    
    # PDF download button
    extra_info = SessionState.get("extra_info")
    pdf_buffer = PDFGenerator.create_enhanced_pdf(itinerary_text, extra_info=extra_info)
    if pdf_buffer:
        st.download_button(
            label="📄 Download PDF Itinerary",
            data=pdf_buffer,
            file_name=f"WanderFlow_itinerary_{uuid.uuid4().hex[:8]}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    
    # For short trips, use the same logic as ShowItinerary but without the task
    show_itinerary_actions(itinerary_text, use_show_task=False)

def show_single_itinerary_results():
    """
    Display itinerary results for long trips (≥5 days).
    
    This function handles the display of single itineraries for longer trips,
    showing the generated itinerary and providing download and action options.
    """
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
        
        # Handle and display itinerary
        itinerary_text = UIComponents.process_itinerary_data(itinerary_data)
        UIComponents.render_itinerary_display(itinerary_text)
        
        # PDF download button
        extra_info = SessionState.get("extra_info")
        pdf_buffer = PDFGenerator.create_enhanced_pdf(itinerary_text, extra_info=extra_info)
        if pdf_buffer:
            st.download_button(
                label="📄 Download PDF Itinerary",
                data=pdf_buffer,
                file_name=f"WanderFlow_itinerary_{uuid.uuid4().hex[:8]}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        
        # Show itinerary actions
        show_itinerary_actions(itinerary_text, use_show_task=True)
    
    except Exception as e:
        st.error(f"❌ Error displaying itinerary: {e}")
        if st.button("🔄 Restart Application", use_container_width=True):
            SessionState.reset()
            st.rerun()

def show_itinerary_actions(itinerary_text: str, use_show_task: bool = True):
    """
    Display common actions for both types of itineraries.
    
    This function provides the interface for accepting itineraries and
    requesting additional information, supporting both short and long trips.
    
    Args:
        itinerary_text (str): The itinerary text to work with
        use_show_task (bool): Whether to use ShowItinerary task (True for long trips,
                             False for short trips)
    """
    st.markdown("### 🎯 What would you like to do next?")
    
    # Action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        # Itinerary acceptance button
        itinerary_confirmed = SessionState.get("itinerary_confirmed")
        
        if itinerary_confirmed:
            # Show confirmed state instead of button
            st.success("✅ Itinerary Accepted!")
            st.info("You can now request additional information if needed.")
        elif st.button("✅ Accept This Itinerary", key="accept_itinerary", use_container_width=True):
            if use_show_task:
                # For long trips: use ShowItinerary task
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
                # For short trips: no ShowItinerary task, just mark as confirmed
                SessionState.set("itinerary_confirmed", True)
                st.success("🎉 Itinerary accepted! You can now request additional info or plan a new trip.")
                st.rerun()
    
    with col2:
        # Handle additional information request
        show_additional_info_options()
    
    # Handle additional info
    handle_additional_info()
    
    # Final buttons
    show_final_buttons()

def show_additional_info_options():
    """
    Display options for requesting additional information.
    
    This function shows the interface for users to request additional travel
    information after accepting their itinerary. It manages the Yes/No choice
    workflow task.
    """
    itinerary_confirmed = SessionState.get("itinerary_confirmed")
    
    if not itinerary_confirmed:
        st.info("⏳ Additional info option will be available after accepting the itinerary")
    else:
        workflow_manager.cache_task("AskforAddInfo_ref", "request_confirmation_task_id")
        request_task_id = SessionState.get("request_confirmation_task_id")
        confirmation_response = SessionState.get("confirmation_response")
        
        # If task is active and user hasn't responded yet
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
        
        # If user has already responded, show the choice
        elif confirmation_response:
            st.info(f"Your choice: **{confirmation_response}**")
        else:
            st.info("⏳ Waiting for additional info task to become available...")

def handle_additional_info():
    """
    Handle additional information processing and display.
    
    This function manages the workflow for additional information:
    - For users who chose "No": proceeds directly to completion
    - For users who chose "Yes": waits for and displays additional info
    - Handles the acceptance of additional information
    """
    # If user chose "No", go directly to completion screen
    if SessionState.get("confirmation_response") == "No":
        if not SessionState.get("workflow_completed"):
            st.success("🎉 Trip planning completed successfully!")
            SessionState.set_step(3)
            SessionState.set("workflow_completed", True)
            time.sleep(1)
            st.rerun()
        return
    
    # Handle additional info - only for users who chose "Yes"
    if SessionState.get("confirmation_response") == "Yes" and not SessionState.get("extra_info"):
        # Additional info comes from ShowMoreInformation task
        extra_info_data = workflow_manager.wait_for_additional_info_task(
            SessionState.get("workflow_id")
        )
        if extra_info_data:
            SessionState.set("extra_info", extra_info_data)
            st.rerun()
    
    # Display additional info if available (only for users who chose "Yes")
    if SessionState.get("extra_info"):
        st.subheader("ℹ️ Additional Information")
        st.markdown(SessionState.get("extra_info"))
        
        # Cache ShowMoreInformation task to allow acceptance
        workflow_manager.cache_task("ShowMoreInformation", "show_more_info_task_id")
        show_more_info_task_id = SessionState.get("show_more_info_task_id")
        
        # Button to accept additional info
        if show_more_info_task_id and st.button("✅ Accept Additional Information", key="accept_additional_info", use_container_width=True):
            # Use additional info from session state
            current_extra_info = SessionState.get("extra_info")
            if workflow_manager.complete_task(show_more_info_task_id, "COMPLETED", {
                "accepted": True,
                "additional_info": current_extra_info
            }):
                st.success("🎉 Additional information accepted!")
                # Go directly to completion screen
                SessionState.set_step(3)
                SessionState.set("workflow_completed", True)
                st.rerun()
            else:
                st.error("❌ Error confirming additional information.")

def show_final_buttons():
    """
    Display final action buttons.
    
    This function renders the final buttons that allow users to start
    a new trip planning session.
    """
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("🔄 Start New Trip Planning", key="restart_final", use_container_width=True):
            SessionState.reset()
            st.rerun()

def show_completion_screen():
    """
    Display the completion and thank you screen.
    
    This function shows the final screen after successful trip planning,
    including:
    - Thank you message
    - Trip summary
    - Final PDF download option
    - Application features showcase
    - Option to plan another trip
    """
    SessionState.set_step(3)
    
    st.markdown('<div class="custom-form-container">', unsafe_allow_html=True)
    
    # Completion header
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
    
    # Thank you message
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
    
    # Trip summary
    itinerary_data = SessionState.get("itinerary")
    if itinerary_data:
        # Show itinerary excerpt
        itinerary_text = UIComponents.process_itinerary_data(itinerary_data)
        
        # Final PDF download button
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
    
    # Application features showcase
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
    
    # Plan another trip button
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🚀 Plan Another Trip", use_container_width=True, type="primary"):
            SessionState.reset()
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ================= SIDEBAR AND FOOTER =================
def show_sidebar_info():
    """
    Display information in the sidebar.
    
    This function renders sidebar content using the UIComponents
    render_sidebar method to show additional application information.
    """
    UIComponents.render_sidebar()

def show_footer():
    """
    Display the application footer.
    
    This function renders the footer content using the UIComponents
    render_footer method to show footer information and links.
    """
    UIComponents.render_footer()

# ================= MAIN EXECUTION =================
if __name__ == "__main__":
    try:
        # Display sidebar
        show_sidebar_info()
        
        # Run main application
        main()
        
        # Display footer
        show_footer()
        
    except Exception as e:
        st.error(f"🚨 An unhandled application error occurred: {e}")
        if hasattr(UIComponents, 'handle_workflow_error'):
            UIComponents.handle_workflow_error()
        st.exception(e)