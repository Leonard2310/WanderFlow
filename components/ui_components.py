"""
UI Components for TripMatch application - Updated with improved spacing and styling
"""

import streamlit as st
import json
from typing import List, Tuple, Optional, Any
from datetime import date

# Assuming these are defined elsewhere in your project
from config.app_config import AppConfig
from utils.session_state import SessionState

class UIComponents:
    """Collection of reusable UI components"""

    @staticmethod
    def apply_custom_css():
        """Apply custom CSS styling to the app"""
        st.markdown("""
        <style>
            /* General app styling */
            .stApp {
                background: linear-gradient(135deg, #A1C4FD 0%, #C2E9FB 100%);
                background-attachment: fixed;
                color: #333333;
            }

            /* Remove default Streamlit padding and margins */
            .main > div {
                padding-top: 0rem;
                padding-bottom: 0rem;
            }

            .main .block-container {
                padding-top: 1rem;
                padding-bottom: 1rem;
                max-width: 1200px;
            }

            /* Remove white bars/spacing at top and bottom */
            .stApp > header, .stApp > div:first-child > div:first-child {
                background-color: transparent !important;
                height: 0px !important;
                padding: 0px !important;
                margin: 0px !important;
            }

            .stApp > div {
                background-color: transparent;
            }

            /* Main header */
            .main-header {
                text-align: center;
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                font-size: 2.5rem;
                font-weight: bold;
                margin-top: 0.5rem;
                margin-bottom: 0.5rem;
            }

            /* Remove white container backgrounds - make transparent */
            .section-container {
                background: transparent !important;
                border-radius: 0px;
                padding: 0.25rem 0;
                margin: 0.25rem 0;
                box-shadow: none;
                border-left: none;
            }

            /* All text should be readable on gradient background */
            .section-container,
            .section-container * {
                color: #333333 !important;
            }

            /* Section headers - make them stand out on gradient */
            .section-container h3 {
                color: #2c3e50 !important;
                margin-bottom: 0.5rem !important;
                margin-top: 0.5rem !important;
                font-size: 1.2rem !important;
                font-weight: bold !important;
                text-shadow: 0px 1px 2px rgba(255,255,255,0.8);
            }

            /* Buttons */
            .stButton > button {
                width: 100%;
                border-radius: 20px;
                height: 3rem;
                font-weight: bold;
                transition: all 0.3s ease;
                border: none;
                background: linear-gradient(45deg, #667eea, #764ba2);
                color: white !important;
            }

            .stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                background: linear-gradient(45deg, #764ba2, #667eea);
            }

            /* Step indicator */
            .step-indicator {
                display: flex;
                justify-content: center;
                margin: 1rem 0;
                background: transparent;
            }

            .step {
                width: 35px;
                height: 35px;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.9);
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 0.5rem;
                font-weight: bold;
                color: #6c757d;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }

            .step.active {
                background: #667eea;
                color: white;
            }

            .step.completed {
                background: #28a745;
                color: white;
            }

            /* Text below steps */
            .step-text {
                color: #2c3e50 !important;
                text-align: center;
                margin-top: 0.5rem;
                font-weight: 500;
                text-shadow: 0px 1px 2px rgba(255,255,255,0.8);
            }

            /* Input styling - labels with better contrast */
            .stSelectbox label,
            .stNumberInput label,
            .stDateInput label,
            .stTextInput label,
            .stCheckbox label,
            .stRadio label {
                color: #2c3e50 !important;
                font-weight: 600 !important;
                text-shadow: 0px 1px 2px rgba(255,255,255,0.8);
            }

            /* Input fields - keep white for readability */
            .stSelectbox > div > div,
            .stNumberInput > div > div,
            .stDateInput > div > div,
            .stTextInput > div > div {
                background-color: rgba(255, 255, 255, 0.95) !important;
                border-radius: 8px !important;
                border: 1px solid rgba(255, 255, 255, 0.3) !important;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }

            /* SPECIFIC FIX FOR DATE INPUT WHITE BACKGROUND */
            .stDateInput > div > div > div {
                background-color: rgba(255, 255, 255, 0.95) !important;
                border-radius: 8px !important;
                border: 1px solid rgba(255, 255, 255, 0.3) !important;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }

            /* Date input field itself */
            .stDateInput input[type="date"] {
                background-color: rgba(255, 255, 255, 0.95) !important;
                color: #000000 !important;
                border: none !important;
                border-radius: 8px !important;
            }

            /* Input text - force black text */
            .stSelectbox input,
            .stNumberInput input,
            .stDateInput input,
            .stTextInput input {
                color: #000000 !important;
            }

            /* Selectbox selected text */
            .stSelectbox > div > div > div {
                color: #000000 !important;
            }

            /* Number input text */
            .stNumberInput input[type="number"] {
                color: #000000 !important;
            }

            /* IMPROVED CHECKBOX STYLING - FILLED WHEN SELECTED */
            .stCheckbox {
                margin-bottom: 0.05rem !important;
                background: transparent !important;
            }

            /* Checkbox label styling */
            .stCheckbox > label {
                color: #2c3e50 !important;
                font-weight: 600 !important;
                text-shadow: 0px 1px 2px rgba(255,255,255,0.8);
                background: transparent !important;
                padding: 0.15rem !important;
                border-radius: 8px !important;
                transition: all 0.2s ease !important;
                display: flex !important;
                align-items: center !important;
                gap: 0.3rem !important;
                margin: 0 !important;
            }

            .stCheckbox > label:hover {
                background: rgba(255, 255, 255, 0.15) !important;
                transform: scale(1.02);
            }

            /* Checkbox input container - the actual checkbox */
            .stCheckbox > label > div:first-child {
                width: 20px !important;
                height: 20px !important;
                border: 2px solid #667eea !important;
                border-radius: 4px !important;
                background-color: rgba(255, 255, 255, 0.95) !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                transition: all 0.3s ease !important;
                position: relative !important;
                flex-shrink: 0 !important;
            }

            /* Checked box background - RIEMPIMENTO COMPLETO DELLA CHECKBOX */
            .stCheckbox > label > input[type="checkbox"]:checked + div {
                background-color: #667eea !important;
                border-color: #667eea !important;
                box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.3) !important;
            }

            /* Checkmark migliorato - più piccolo e centrato */
            .stCheckbox > label > div:first-child::after {
                content: "✓";
                color: white;
                font-size: 12px;
                font-weight: bold;
                opacity: 0;
                transition: opacity 0.3s ease;
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
            }

            /* Show checkmark when checked */
            .stCheckbox > label > input[type="checkbox"]:checked + div::after {
                opacity: 1;
            }

            /* Checkbox text */
            .stCheckbox > label > div:last-child {
                color: #2c3e50 !important;
                font-weight: 600 !important;
                text-shadow: 0px 1px 2px rgba(255,255,255,0.8);
                font-size: 0.9rem !important;
            }

            /* More specific targeting for section containers */
            .section-container .stCheckbox {
                background: transparent !important;
                margin-bottom: 0.05rem !important;
            }

            .section-container .stCheckbox > label {
                background: transparent !important;
                padding: 0.15rem !important;
            }

            /* Target specific checkbox containers by data attributes */
            div[data-testid="stCheckbox"] {
                background: transparent !important;
                margin-bottom: 0.05rem !important;
            }

            div[data-testid="stCheckbox"] > label {
                background: transparent !important;
                color: #2c3e50 !important;
                font-weight: 600 !important;
                text-shadow: 0px 1px 2px rgba(255,255,255,0.8);
                padding: 0.15rem !important;
                margin: 0 !important;
            }

            div[data-testid="stCheckbox"] > label > div:first-child {
                background-color: rgba(255, 255, 255, 0.95) !important;
                border: 2px solid #667eea !important;
                border-radius: 4px !important;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
                width: 20px !important;
                height: 20px !important;
            }

            /* Enhanced checkbox checked state - RIEMPIMENTO COMPLETO DELLA CHECKBOX */
            div[data-testid="stCheckbox"] input:checked + div {
                background-color: #667eea !important;
                border-color: #667eea !important;
                box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.3) !important;
            }

            /* Aggiungi il checkmark anche per data-testid */
            div[data-testid="stCheckbox"] > label > div:first-child::after {
                content: "✓";
                color: white;
                font-size: 12px;
                font-weight: bold;
                opacity: 0;
                transition: opacity 0.3s ease;
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
            }

            div[data-testid="stCheckbox"] input:checked + div::after {
                opacity: 1;
            }

            /* Override any Streamlit default white backgrounds on checkboxes */
            .stCheckbox * {
                background: transparent !important;
            }

            /* Selectbox dropdown */
            div[data-baseweb="popover"] > div > ul {
                background-color: rgba(255, 255, 255, 0.98) !important;
                border-radius: 8px !important;
                border: 1px solid rgba(255, 255, 255, 0.3) !important;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }

            div[data-baseweb="popover"] > div > ul > li {
                color: #333333 !important;
            }

            /* Sidebar styling */
            .css-1d391kg {
                background: rgba(255, 255, 255, 0.95) !important;
                padding: 1rem !important;
                border-right: 1px solid rgba(255, 255, 255, 0.3) !important;
                box-shadow: 2px 0 8px rgba(0,0,0,0.1) !important;
            }

            .sidebar-section-container {
                background: rgba(248, 249, 250, 0.8);
                border-radius: 10px;
                padding: 1rem;
                margin-bottom: 1rem;
                border: 1px solid rgba(224, 224, 224, 0.5);
            }

            .sidebar-section-container h3 {
                color: #667eea !important;
            }

            .sidebar-section-container p, 
            .sidebar-section-container strong {
                color: #555555 !important;
            }

            /* Itinerary display - semi-transparent */
            .itinerary-container {
                background: rgba(255, 255, 255, 0.9);
                border-radius: 20px;
                padding: 2rem;
                margin: 1.5rem 0;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            }

            /* Code block styling */
            .itinerary-container pre {
                background-color: rgba(248, 249, 250, 0.9);
                border-radius: 10px;
                padding: 1rem;
                border: 1px solid rgba(224, 224, 224, 0.5);
                color: #333333;
                white-space: pre-wrap;
                word-wrap: break-word;
            }

            /* Progress bar */
            .stProgress > div > div {
                background: linear-gradient(45deg, #667eea, #764ba2);
                border-radius: 10px;
            }

            .stProgress > div {
                background: rgba(255, 255, 255, 0.3);
                border-radius: 10px;
            }

            /* Footer */
            .stApp footer {
                background: transparent !important;
                color: #2c3e50 !important;
            }

            .stApp footer p {
                color: #2c3e50 !important;
                text-shadow: 0px 1px 2px rgba(255,255,255,0.8);
            }

            /* REDUCE SPACING BETWEEN ELEMENTS - ULTRA COMPATTO */
            .stMarkdown {
                margin-bottom: 0rem !important;
                margin-top: 0rem !important;
            }

            /* Column spacing - più compatto */
            .stColumn {
                padding: 0.05rem !important;
            }

            /* Compact form elements - MARGINI RIDOTTI AL MINIMO */
            .stSelectbox,
            .stNumberInput,
            .stDateInput,
            .stTextInput {
                margin-bottom: 0.1rem !important;
                margin-top: 0.1rem !important;
            }

            /* Reduce space between form elements */
            .element-container {
                background: transparent !important;
                margin-bottom: 0.05rem !important;
                margin-top: 0.05rem !important;
                padding: 0 !important;
            }

            /* Make sure all containers are transparent */
            .stContainer {
                background: transparent !important;
                padding: 0 !important;
                margin: 0 !important;
            }

            /* Reduce vertical spacing in columns */
            .stColumn > div {
                gap: 0.05rem !important;
                padding: 0 !important;
            }

            /* Additional spacing reduction */
            .stSelectbox > div,
            .stNumberInput > div,
            .stDateInput > div,
            .stTextInput > div {
                margin-bottom: 0.05rem !important;
                margin-top: 0.05rem !important;
            }

            /* Riduci spazi nei form */
            .stForm {
                padding: 0.5rem !important;
                margin: 0.25rem 0 !important;
            }

            /* Riduci spazi nelle sezioni */
            .section-container {
                background: transparent !important;
                border-radius: 0px;
                padding: 0.1rem 0 !important;
                margin: 0.1rem 0 !important;
                box-shadow: none;
                border-left: none;
            }

            /* Headers più compatti */
            .section-container h3 {
                color: #2c3e50 !important;
                margin-bottom: 0.25rem !important;
                margin-top: 0.25rem !important;
                font-size: 1.1rem !important;
                font-weight: bold !important;
                text-shadow: 0px 1px 2px rgba(255,255,255,0.8);
            }

            /* Riduci spazio tra grid di checkbox */
            .stColumn {
                padding-left: 0.05rem !important;
                padding-right: 0.05rem !important;
            }

            /* Containers compatti */
            div[data-testid="column"] {
                padding: 0.05rem !important;
            }

            /* Spazio minimo tra le righe */
            .block-container .element-container {
                margin: 0.05rem 0 !important;
            }
            
            /* Migliora l'allineamento del country selector */
            .country-selector-row {
                display: flex;
                align-items: end;
                gap: 1rem;
            }

            /* Allinea il pulsante con il selectbox */
            .stButton > button {
                margin-top: 0.5rem;
            }

            /* Country selection grouped styling */
            .stSelectbox option[data-testid*="continent"] {
                font-weight: bold !important;
                background: linear-gradient(45deg, #667eea, #764ba2) !important;
                color: white !important;
                padding: 0.5rem !important;
                border-bottom: 1px solid #ddd !important;
            }

            /* Country options styling */
            .stSelectbox option {
                padding: 0.3rem !important;
                border-bottom: 1px solid #f0f0f0 !important;
            }

            .stSelectbox option:hover {
                background-color: rgba(102, 126, 234, 0.1) !important;
            }

            /* Better spacing for grouped selectbox */
            .country-selector-row .stSelectbox {
                margin-bottom: 0.5rem !important;
            }

            /* Make continent headers appear disabled/non-selectable */
            .stSelectbox option[value*="────"] {
                background-color: #f5f5f5 !important;
                color: #888 !important;
                font-style: italic !important;
                cursor: not-allowed !important;
                pointer-events: none !important;
            }

            /* Style continent headers in dropdown */
            div[data-baseweb="popover"] > div > ul > li[aria-label*="────"] {
                background-color: #f8f9fa !important;
                color: #6c757d !important;
                font-weight: bold !important;
                text-align: center !important;
                cursor: not-allowed !important;
                pointer-events: none !important;
                border-top: 2px solid #dee2e6 !important;
                border-bottom: 1px solid #dee2e6 !important;
            }

            /* Improve visual separation between continents and countries */
            div[data-baseweb="popover"] > div > ul > li[aria-label*="   "] {
                padding-left: 1rem !important;
                border-left: 3px solid #667eea !important;
                margin-left: 0.5rem !important;
            }

        </style>
        """, unsafe_allow_html=True)

    @staticmethod
    def render_header():
        """Render the main application header"""
        st.markdown(
            f'<h1 class="main-header">{AppConfig.APP_TITLE}</h1>',
            unsafe_allow_html=True
        )

    @staticmethod
    def create_step_indicator(current_step: int):
        """Create a step progress indicator"""
        steps = [
            ("1", "Preferences", 1),
            ("2", "Options", 2),
            ("3", "Review", 3)
        ]
        cols = st.columns(len(steps))
        for idx, (num, label, step_num) in enumerate(steps):
            css_class = "step"
            if step_num < current_step:
                css_class += " completed"
            elif step_num == current_step:
                css_class += " active"

            with cols[idx]:
                st.markdown(f'<div class="{css_class}">{num}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="step-text">{label}</div>', unsafe_allow_html=True)

    @staticmethod
    def render_vacation_styles() -> List[str]:
        """Render vacation style selection"""
        with st.container():
            st.markdown('<div class="section-container">', unsafe_allow_html=True)
            st.markdown('<h3>🎨 What\'s your vacation style?</h3>', unsafe_allow_html=True)

            selected_styles = []
            cols = st.columns(len(AppConfig.VACATION_STYLES))

            for i, (key, label) in enumerate(AppConfig.VACATION_STYLES.items()):
                with cols[i]:
                    if st.checkbox(label, key=f"style_{key}"):
                        selected_styles.append(key)

            st.markdown('</div>', unsafe_allow_html=True)
            
        return selected_styles

    @staticmethod
    def process_itinerary_data(itinerary_data: Any) -> str:
        """Process itinerary data and return formatted text"""
        try:
            if isinstance(itinerary_data, str):
                try:
                    parsed_data = json.loads(itinerary_data)
                except json.JSONDecodeError:
                    return itinerary_data
            else:
                parsed_data = itinerary_data

            if isinstance(parsed_data, list):
                if len(parsed_data) > 1:
                    st.info("🎯 Multiple itinerary options available")
                    selected_itinerary_index = st.selectbox(
                        "Choose your preferred itinerary:",
                        range(len(parsed_data)),
                        format_func=lambda x: f"Option {x + 1}",
                        key="itinerary_selector"
                    )
                    return json.dumps(parsed_data[selected_itinerary_index], indent=2) if isinstance(parsed_data[selected_itinerary_index], (dict, list)) else str(parsed_data[selected_itinerary_index])
                elif len(parsed_data) == 1:
                    return json.dumps(parsed_data[0], indent=2) if isinstance(parsed_data[0], (dict, list)) else str(parsed_data[0])
                else:
                    return "No itinerary data found."
            else:
                return json.dumps(parsed_data, indent=2) if isinstance(parsed_data, (dict, list)) else str(parsed_data)
        except Exception as e:
            st.error(f"Error processing itinerary data: {e}")
            return str(itinerary_data)

    @staticmethod
    def render_itinerary(json_itinerary: dict):
        """Render itinerary details in a formatted block"""
        st.markdown('<div class="itinerary-container">', unsafe_allow_html=True)
        st.markdown("### Itinerary JSON")
        st.code(json.dumps(json_itinerary, indent=2), language="json")
        st.markdown('</div>', unsafe_allow_html=True)
        
    @staticmethod
    def render_duration_section() -> Tuple[int, Optional[date]]:
        """Render the duration and period selection section"""
        with st.container():
            st.markdown('<div class="section-container">', unsafe_allow_html=True)
            st.markdown('<h3>📅 Trip Duration & Timing</h3>', unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                duration = st.number_input("Duration (days)", min_value=1, max_value=30, value=7, key="duration_input")
            with col2:
                period = st.date_input("Preferred travel period", value=date.today(), key="period_input")

            st.markdown('</div>', unsafe_allow_html=True)
            
        return duration, period

    @staticmethod
    def render_sidebar():
        """Render the sidebar with app information"""
        with st.sidebar:
            st.markdown("""
            <div class="sidebar-section-container">
                <h3>🌍 TripMatch</h3>
                <p>Your AI-powered travel planner</p>
            </div>
            """, unsafe_allow_html=True)

            if SessionState.is_workflow_started():
                st.markdown("""
                <div class="sidebar-section-container">
                    <h3>📊 Session Info</h3>
                """, unsafe_allow_html=True)

                workflow_id = SessionState.get("workflow_id", "")
                st.markdown(f"**Workflow ID:** `{workflow_id[:8]}...`")
                st.markdown(f"**Step:** {SessionState.get_current_step()}/3")

                selected_country = SessionState.get("selected_country")
                if selected_country:
                    st.markdown(f"**Country:** {selected_country}")

                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("""
            <div class="sidebar-section-container">
                <h3>🆘 Support</h3>
                <p>Having issues? Contact our support team!</p>
            </div>
            """, unsafe_allow_html=True)

            if st.checkbox("🔧 Debug Mode", key="debug_mode_checkbox"):
                debug_info = SessionState.get_debug_info()
                st.json(debug_info)
                
                # Aggiungi informazioni workflow se disponibile
                workflow_id = SessionState.get("workflow_id")
                if workflow_id:
                    from components.workflow_manager import WorkflowManager
                    # Nota: Questo richiederà l'accesso al workflow_manager
                    st.markdown("**Workflow Status:**")
                    if st.button("🔍 Show Workflow Details", key="workflow_debug_btn"):
                        st.json({"workflow_id": workflow_id})

    @staticmethod
    def render_footer():
        """Render the application footer"""
        st.markdown("---")
        st.markdown(
            """
            <div style="text-align: center; padding: 1rem 0; color: #2c3e50;">
                <p>🌍 <strong>TripMatch</strong> - Powered by Orkes Conductor & Streamlit</p>
                <p>Made with ❤️ for travelers worldwide</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    @staticmethod
    def handle_workflow_error():
        """Handle workflow errors with user-friendly interface"""
        st.error("⚠️ Something went wrong with your trip planning workflow.")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔄 Restart Planning", use_container_width=True):
                SessionState.reset()
                st.rerun()

        with col2:
            if st.button("🔍 Show Debug Info", use_container_width=True):
                st.json(SessionState.get_debug_info())
    
    @staticmethod
    def render_destination_types() -> List[str]:
        """Render destination type selection"""
        with st.container():
            st.markdown('<div class="section-container">', unsafe_allow_html=True)
            st.markdown('<h3>🏞️ What type of destination appeals to you?</h3>', unsafe_allow_html=True)

            selected_destinations = []
            cols = st.columns(len(AppConfig.DESTINATION_TYPES))

            for i, (key, label) in enumerate(AppConfig.DESTINATION_TYPES.items()):
                with cols[i]:
                    if st.checkbox(label, key=f"dest_{key}"):
                        selected_destinations.append(key)

            st.markdown('</div>', unsafe_allow_html=True)
            
        return selected_destinations

    @staticmethod
    def render_country_selection() -> str:
        """Render country selection dropdown grouped by continent with flags"""
        with st.container():
            st.markdown('<div class="section-container">', unsafe_allow_html=True)
            st.markdown('<h3>🌍 Preferred Country</h3>', unsafe_allow_html=True)
            st.markdown('<p style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">Countries are organized by continent for easier selection</p>', unsafe_allow_html=True)

            # Avvia riga con stile custom
            st.markdown('<div class="country-selector-row">', unsafe_allow_html=True)

            # Use grouped country options
            country_options = ["Select a country (optional)"] + AppConfig.get_country_options_grouped()
            
            # Initialize session state for tracking valid selections
            if "last_valid_country_index" not in st.session_state:
                st.session_state.last_valid_country_index = 0
            
            # Find current valid index (avoid continent headers)
            current_index = st.session_state.last_valid_country_index
            
            selected_option = st.selectbox(
                "🌍 Choose your destination country:",
                country_options,
                index=current_index,
                key="country_selector",
                help="Countries are grouped by continent. Select any country to see it highlighted on the map.",
                format_func=lambda x: (
                    f"🌍 {x.replace('────', '').strip()} 🌍" if x.startswith("────") 
                    else x
                )
            )
            
            # Get the current selection index
            try:
                selected_index = country_options.index(selected_option)
            except ValueError:
                selected_index = 0
            
            # Check if user selected a continent header (should not be allowed)
            if selected_option.startswith("────"):
                # Show warning and reset to default
                st.warning("⚠️ Continent headers are not selectable. Please choose a specific country.")
                selected_country = ""
                # Keep last valid index as fallback
            else:
                # Update last valid selection index
                st.session_state.last_valid_country_index = selected_index
                
                # Extract the actual country name
                if selected_option == "Select a country (optional)":
                    selected_country = ""
                else:
                    selected_country = AppConfig.extract_country_from_grouped_option(selected_option)

            # Show selection info if a valid country is selected
            if selected_country:
                st.success(f"✅ Selected: **{selected_country}**")

            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        return selected_country

    @staticmethod
    def render_itinerary_display(itinerary_text: str):
        """Render the itinerary display"""
        with st.container():
            st.markdown('<div class="itinerary-container">', unsafe_allow_html=True)
            st.markdown("**📋 Your Travel Plan:**")
            st.code(itinerary_text, language="json" if itinerary_text.strip().startswith(("{", "[")) else "text")
            st.markdown('</div>', unsafe_allow_html=True)