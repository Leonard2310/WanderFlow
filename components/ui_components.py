"""
UI Components for WanderFlow travel planning application.

This module provides a comprehensive collection of reusable UI components
for the WanderFlow travel planning application. It includes custom CSS styling,
form elements, interactive components, and layout management functions.
"""

import streamlit as st
import json
from typing import List, Tuple, Optional, Any
from datetime import date

from config.app_config import AppConfig
from utils.session_state import SessionState

class UIComponents:
    """
    Collection of reusable UI components for the WanderFlow application.
    
    This class provides static methods for rendering various UI elements
    including styling, forms, navigation, and display components.
    """

    @staticmethod
    def apply_custom_css():
        """
        Apply custom CSS styling to the Streamlit application.
        
        Applies comprehensive styling including modern gradients, shadows,
        rounded inputs, and responsive design elements for better UX.
        """
        st.markdown("""
        <style>
            /* General app styling */
            .stApp {
                background: linear-gradient(135deg, #E0EAFB 0%, #F8FAFF 100%);
                background-attachment: fixed;
                color: #333333;
                font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
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
                color: #4A69BD !important;
                font-size: 2.5rem;
                font-weight: bold;
                margin-top: 0.5rem;
                margin-bottom: 0.5rem;
                text-shadow: 0px 2px 4px rgba(255,255,255,0.8);
            }

            /* Add dynamic, colored containers for sections */ 
            .section-container {
                background: linear-gradient(145deg, #FFFFFF, #EAF3FF);
                border-radius: 15px;
                padding: 0.2rem;
                margin: 1rem 0;
                box-shadow: 0 8px 25px rgba(0,0,0,0.15);
                border: 1px solid rgba(161, 196, 253, 0.4);
            }

            /* Allow inline styles to work properly */
            .stButton > button {
                width: 100%;
                border-radius: 20px;
                height: 3rem;
                font-weight: bold;
                transition: all 0.3s ease;
                border: none;
                background: linear-gradient(45deg, #7A97E0, #4A69BD); 
                color: white !important;
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            }

            .stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                background: linear-gradient(45deg, #7A97E0, #4A69BD);
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
                background: #4A69BD;
                color: white;
                box-shadow: 0 4px 12px rgba(74, 105, 189, 0.4);
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
                border: 1px solid rgba(161, 196, 253, 0.3) !important;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }

            /* Date input field styling */
            .stDateInput > div > div > div {
                background-color: rgba(255, 255, 255, 0.95) !important;
                border-radius: 8px !important;
                border: 1px solid rgba(161, 196, 253, 0.3) !important;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }

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

            .stSelectbox > div > div > div {
                color: #000000 !important;
            }

            .stNumberInput input[type="number"] {
                color: #000000 !important;
            }

            /* Selectbox dropdown */
            div[data-baseweb="popover"] > div > ul {
                background-color: rgba(255, 255, 255, 0.98) !important;
                border-radius: 8px !important;
                border: 1px solid rgba(161, 196, 253, 0.3) !important;
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
                color: #4A69BD !important;
            }

            .sidebar-section-container p,
            .sidebar-section-container strong {
                color: #555555 !important;
            }

            /* Itinerary display - add a light background for clarity */
            .itinerary-container {
                background: linear-gradient(145deg, #F0F5FF, #FFFFFF);
                border-radius: 15px;
                padding: 1.5rem !important;
                margin: 1rem 0 !important;
                box-shadow: 0 8px 25px rgba(0,0,0,0.15);
                border: 1px solid rgba(161, 196, 253, 0.4);
            }

            /* Code block styling - subtle background for readability, compact spacing */
            .itinerary-container pre {
                background-color: transparent;
                border-radius: 10px;
                padding: 0.75rem;
                margin: 0.25rem 0;
                border: none;
                color: #2c3e50;
                font-weight: 500;
                text-shadow: 0px 1px 2px rgba(255,255,255,0.8);
                white-space: pre-wrap;
                word-wrap: break-word;
            }

            /* Progress bar */
            .stProgress > div > div {
                background: linear-gradient(45deg, #7A97E0, #4A69BD);
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

            /* Remove any white backgrounds that might appear */
            .stContainer,
            .stColumn,
            .main .block-container,
            .element-container,
            .stMarkdown > div {
                background: transparent !important;
            }

            /* Success messages styling */
            .stSuccess,
            .stSuccess > div,
            .stSuccess p,
            .stSuccess h1,
            .stSuccess h2,
            .stSuccess h3,
            .stSuccess h4,
            div[data-testid="stSuccess"],
            div[data-testid="stSuccess"] p,
            div[data-testid="stSuccess"] h1,
            div[data-testid="stSuccess"] h2,
            div[data-testid="stSuccess"] h3,
            div[data-testid="stSuccess"] h4 {
                color: white !important;
                text-shadow: 0px 1px 2px rgba(0,0,0,0.3) !important;
            }

            /* Special styling for itinerary title */
            .stMarkdown h3:contains("Your Personalized Travel Itinerary"),
            .stMarkdown h3[id*="personalized"] {
            }

            /* Reduce spacing between elements - ultra compact */
            .stMarkdown {
                margin-bottom: 0rem !important;
                margin-top: 0rem !important;
            }

            /* Column spacing - more compact */
            .stColumn {
                padding: 0.05rem !important;
            }

            /* Compact form elements */
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

            /* Reduce spacing in forms */
            .stForm {
                padding: 0.5rem !important;
                margin: 0.25rem 0 !important;
            }

            /* Reduce spacing in sections */
            .section-container {
            }

            /* More compact headers */
            .section-container h3 {
                color: #2c3e50 !important;
                margin-bottom: 0.25rem !important;
                margin-top: 0.25rem !important;
                font-size: 1.1rem !important;
                font-weight: bold !important;
                text-shadow: 0px 1px 2px rgba(255,255,255,0.8);
            }

            /* Reduce space between checkbox grid */
            .stColumn {
                padding-left: 0.05rem !important;
                padding-right: 0.05rem !important;
            }

            /* Compact containers */
            div[data-testid="column"] {
                padding: 0.05rem !important;
            }

            /* Minimal spacing between rows */
            .block-container .element-container {
                margin: 0.05rem 0 !important;
            }
            
            /* Improve alignment of country selector */
            .country-selector-row {
                display: flex;
                align-items: end;
                gap: 1rem;
            }

            /* Align button with selectbox */
            .stButton > button {
                margin-top: 0.5rem;
            }

            /* Country selection grouped styling */
            .stSelectbox option[data-testid*="continent"] {
                font-weight: bold !important;
                background: linear-gradient(45deg, #7A97E0, #4A69BD);
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
                background-color: rgba(74, 105, 189, 0.1) !important;
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
            div[data-baseweb="popover"] > div > ul > li[aria-label*="   "] {
                padding-left: 1rem !important;
                border-left: 3px solid #4A69BD !important;
                margin-left: 0.5rem !important;
            }

            /* Completion banner styling */
            .completion-banner,
            .completion-banner *,
            .completion-banner h3,
            .completion-banner p,
            .completion-title,
            .completion-text {
                color: #FFFFFF !important;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;
            }

            div.completion-banner h3.completion-title,
            div.completion-banner p.completion-text {
                color: #FFFFFF !important;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;
            }

            /* Make sure markdown inside completion banner is white */
            .completion-banner .stMarkdown,
            .completion-banner .stMarkdown *,
            .completion-banner .stMarkdown h1,
            .completion-banner .stMarkdown h2,
            .completion-banner .stMarkdown h3,
            .completion-banner .stMarkdown h4,
            .completion-banner .stMarkdown p {
                color: #FFFFFF !important;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;
            }
        </style>
        """, unsafe_allow_html=True)

    @staticmethod
    def render_header():
        """
        Render the main application header.
        
        Displays the WanderFlow application title with custom styling
        using the configured app title from AppConfig.
        """
        st.markdown(
            f'<h1 class="main-header">{AppConfig.APP_TITLE}</h1>',
            unsafe_allow_html=True
        )

    @staticmethod
    def create_step_indicator(current_step: int):
        """
        Create a visual step progress indicator.
        
        Displays a three-step progress indicator showing the current position
        in the travel planning workflow.
        
        Args:
            current_step (int): The current step number (1-3)
        """
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
        """
        Render vacation style selection interface.
        
        Displays checkboxes for different vacation styles configured
        in AppConfig, allowing users to select multiple preferences.
        
        Returns:
            List[str]: List of selected vacation style keys
        """
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
        """
        Process itinerary data and return formatted text.
        
        Handles various itinerary data formats including JSON strings,
        lists, and dictionaries. Provides selection interface for multiple
        itinerary options and formats output appropriately.
        
        Args:
            itinerary_data (Any): Raw itinerary data in various formats
            
        Returns:
            str: Formatted itinerary text for display
        """
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
        """
        Render itinerary details in a formatted code block.
        
        Displays the itinerary data as formatted JSON within a styled
        container for clear presentation and readability.
        
        Args:
            json_itinerary (dict): Itinerary data as dictionary
        """
        st.markdown('<div class="itinerary-container">', unsafe_allow_html=True)
        st.markdown("### Itinerary JSON")
        st.code(json.dumps(json_itinerary, indent=2), language="json")
        st.markdown('</div>', unsafe_allow_html=True)
        
    @staticmethod
    def render_duration_section() -> Tuple[int, Optional[date]]:
        """
        Render the duration and period selection section.
        
        Displays input fields for trip duration (in days) and preferred
        travel period, providing a user-friendly interface for temporal
        trip planning parameters.
        
        Returns:
            Tuple[int, Optional[date]]: Trip duration and selected travel date
        """
        with st.container():
            st.markdown('<div class="section-container">', unsafe_allow_html=True)
            st.markdown('<h3>📅 Trip Duration & Timing</h3>', unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                duration = st.number_input("Duration (days)", min_value=1, max_value=30, value=7, key="duration_input")
            with col2:
                period = st.date_input("Preferred travel period", value=date.today(), key="period_input", format="DD/MM/YYYY")

            st.markdown('</div>', unsafe_allow_html=True)
            
        return duration, period

    @staticmethod
    def render_sidebar():
        """
        Render the sidebar with application information and debug tools.
        
        Displays WanderFlow branding, session information when a workflow
        is active, and optional debug information for development purposes.
        """
        with st.sidebar:
            st.markdown("""
            <div class="sidebar-section-container">
                <h3>🌍 WanderFlow</h3>
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

    @staticmethod
    def render_footer():
        """
        Render the application footer with branding.
        
        Displays WanderFlow branding and acknowledgments in a centered
        footer layout with appropriate styling.
        """
        st.markdown("---")
        st.markdown(
            """
            <div style="text-align: center; padding: 1rem 0; color: #2c3e50;">
                <p>🌍 <strong>WanderFlow</strong> - Powered by Orkes Conductor & Streamlit</p>
                <p>Made with ❤️ for travelers worldwide</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    @staticmethod
    def handle_workflow_error():
        """
        Handle workflow errors with user-friendly interface.
        
        Provides error messaging and recovery options when workflow
        issues occur, including restart and debug information display.
        """
        st.error("⚠️ Something went wrong with your trip planning workflow.")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔄 Restart Planning", use_container_width=True):
                SessionState.reset()
                st.rerun()

        with col2:
            pass
    
    @staticmethod
    def render_destination_types() -> List[str]:
        """
        Render destination type selection interface.
        
        Displays checkboxes for different destination types configured
        in AppConfig, allowing users to select multiple preferences.
        
        Returns:
            List[str]: List of selected destination type keys
        """
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
        """
        Render country selection dropdown grouped by continent.
        
        Displays an organized country selection interface with countries
        grouped by continent for easier navigation. Includes validation
        to prevent selection of continent headers.
        
        Returns:
            str: Selected country name, empty string if none selected
        """
        with st.container():
            st.markdown('<div class="section-container">', unsafe_allow_html=True)
            st.markdown('<h3>🌍 Preferred Country</h3>', unsafe_allow_html=True)
            st.markdown('<p style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">Countries are organized by continent for easier selection</p>', unsafe_allow_html=True)

            # Start row with custom styling
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
        """
        Render the itinerary display with proper formatting.
        
        Displays the generated itinerary text in a styled container
        with appropriate formatting for JSON or plain text content.
        
        Args:
            itinerary_text (str): The itinerary content to display
        """
        with st.container():
            st.code(itinerary_text, language="json" if itinerary_text.strip().startswith(("{", "[")) else "text")
            st.markdown('</div>', unsafe_allow_html=True)