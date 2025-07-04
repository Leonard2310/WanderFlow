"""
Session State Management for WanderFlow Application

This module provides centralized session state management for the WanderFlow
travel planning application, ensuring consistent state handling across
different components and workflow stages.
"""

import streamlit as st
from typing import Dict, Any, Optional

class SessionState:
    """
    Manages session state in an organized and consistent manner.
    
    This class provides a centralized interface for managing all session
    state variables used throughout the WanderFlow application, including
    workflow IDs, task states, user preferences, and UI state.
    """
    
    # Default values for all session state variables
    DEFAULTS = {
        "workflow_id": None,
        "pref_task_id": None,
        "show_task_id": None,
        "choice_task_id": None,
        "choice_travel_city_task_id": None,     # For ChoiceTravelCity (short trips)
        "request_confirmation_task_id": None,   # For AskforAddInfo_ref workflow task
        "show_more_info_task_id": None,         # For ShowMoreInformation task
        "confirmation_response": None,          # For Yes/No response handling
        "itinerary": None,
        "travel_options": None,                 # For 3 short trip options
        "selected_travel_option": None,         # User's selected option
        "choice_task_completed": False,         # Indicates if ChoiceTravelCity task is completed
        "is_short_trip": False,                 # Indicates if trip is ≤3 days
        "trip_duration": None,                  # Trip duration for flow determination
        "extra_requested": False,
        "extra_info": None,
        "selected_country": "",
        "confirmed_country": "",                # Country confirmed with button
        "last_selected_country": "",
        "last_confirmed_country": "",           # For tracking confirmed country changes
        "current_step": 0,
        "map_zoom": 2,
        "map_center": [30, 0],
        "preferences_submitted": False,
        "itinerary_confirmed": False,
        "workflow_completed": False,            # For tracking workflow completion
        "country_selection_made": False,        # For tracking country selection
        "map_needs_update": False               # For tracking map updates
    }
    
    @classmethod
    def initialize(cls):
        """
        Initialize all default values if they don't exist in session state.
        
        This method ensures all required session state variables are set
        to their default values when the application starts.
        """
        for key, value in cls.DEFAULTS.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    @classmethod
    def reset(cls):
        """
        Reset session state to default values.
        
        This method resets all session state variables to their initial
        default values, effectively starting a new session.
        """
        for key, value in cls.DEFAULTS.items():
            st.session_state[key] = value
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """
        Get a value from session state.
        
        Args:
            key (str): Session state key to retrieve
            default (Any, optional): Default value if key doesn't exist
            
        Returns:
            Any: Value from session state or default
        """
        return st.session_state.get(key, default)
    
    @classmethod
    def set(cls, key: str, value: Any):
        """
        Set a value in session state.
        
        Args:
            key (str): Session state key to set
            value (Any): Value to store
        """
        st.session_state[key] = value
    
    @classmethod
    def update(cls, **kwargs):
        """
        Update multiple values in session state.
        
        Args:
            **kwargs: Key-value pairs to update in session state
        """
        for key, value in kwargs.items():
            st.session_state[key] = value
    
    @classmethod
    def get_debug_info(cls) -> Dict[str, Any]:
        """
        Get debug information about current session state.
        
        This method provides a comprehensive overview of the current
        session state for debugging and monitoring purposes.
        
        Returns:
            Dict[str, Any]: Dictionary containing key session state information
        """
        return {
            "workflow_id": cls.get("workflow_id"),
            "current_step": cls.get("current_step"),
            "pref_task_id": cls.get("pref_task_id"),
            "show_task_id": cls.get("show_task_id"),
            "choice_task_id": cls.get("choice_task_id"),
            "request_confirmation_task_id": cls.get("request_confirmation_task_id"),
            "show_more_info_task_id": cls.get("show_more_info_task_id"),
            "confirmation_response": cls.get("confirmation_response"),
            "extra_requested": cls.get("extra_requested"),
            "has_itinerary": cls.has_itinerary(),
            "has_extra_info": bool(cls.get("extra_info")),
            "selected_country": cls.get("selected_country"),
            "confirmed_country": cls.get("confirmed_country"),
            "preferences_submitted": cls.get("preferences_submitted"),
            "itinerary_confirmed": cls.get("itinerary_confirmed"),
            "country_selection_made": cls.get("country_selection_made"),
            "map_center": cls.get("map_center"),
            "map_zoom": cls.get("map_zoom")
        }
    
    @classmethod
    def is_workflow_started(cls) -> bool:
        """
        Check if a workflow has been started.
        
        Returns:
            bool: True if workflow is active, False otherwise
        """
        return bool(cls.get("workflow_id"))
    
    @classmethod
    def has_itinerary(cls) -> bool:
        """
        Check if an itinerary has been generated.
        
        Returns:
            bool: True if itinerary exists, False otherwise
        """
        return bool(cls.get("itinerary"))
    
    @classmethod
    def is_extra_requested(cls) -> bool:
        """
        Check if additional information has been requested.
        
        Returns:
            bool: True if extra info was requested, False otherwise
        """
        return bool(cls.get("extra_requested"))
    
    @classmethod
    def get_current_step(cls) -> int:
        """
        Get the current workflow step.
        
        Returns:
            int: Current step number (0-3)
        """
        return cls.get("current_step", 0)
    
    @classmethod
    def advance_step(cls):
        """
        Advance to the next workflow step.
        
        This method increments the current step by 1, with a maximum of 3.
        """
        current = cls.get_current_step()
        cls.set("current_step", min(current + 1, 3))
    
    @classmethod
    def set_step(cls, step: int):
        """
        Set a specific workflow step.
        
        Args:
            step (int): Step number to set (0-3)
        """
        cls.set("current_step", max(0, min(step, 3)))
    
    # Country management methods
    @classmethod
    def has_confirmed_country(cls) -> bool:
        """
        Check if a country has been confirmed.
        
        Returns:
            bool: True if country is confirmed, False otherwise
        """
        return bool(cls.get("confirmed_country"))
    
    @classmethod
    def get_confirmed_country(cls) -> str:
        """
        Get the confirmed country name.
        
        Returns:
            str: Name of confirmed country or empty string
        """
        return cls.get("confirmed_country", "")
    
    @classmethod
    def confirm_country(cls, country: str):
        """
        Confirm a country for map display.
        
        This method sets the confirmed country and updates related
        map state flags.
        
        Args:
            country (str): Name of country to confirm
        """
        cls.update(
            confirmed_country=country,
            country_selection_made=True,
            map_needs_update=True
        )
    
    @classmethod
    def reset_country_selection(cls):
        """
        Reset country selection to initial state.
        
        This method clears all country-related session state and
        resets the map to world view.
        """
        cls.update(
            selected_country="",
            confirmed_country="",
            last_selected_country="",
            last_confirmed_country="",
            country_selection_made=False,
            map_needs_update=True,
            map_center=[30, 0],
            map_zoom=2
        )
    
    @classmethod
    def country_changed(cls) -> bool:
        """
        Check if the confirmed country has changed.
        
        Returns:
            bool: True if confirmed country changed, False otherwise
        """
        current = cls.get("confirmed_country", "")
        last = cls.get("last_confirmed_country", "")
        return current != last
    
    @classmethod
    def mark_country_processed(cls):
        """
        Mark that the country change has been processed.
        
        This method updates the last confirmed country to match
        the current confirmed country.
        """
        cls.set("last_confirmed_country", cls.get("confirmed_country", ""))
    
    @classmethod
    def needs_map_update(cls) -> bool:
        """
        Check if the map needs to be updated.
        
        Returns:
            bool: True if map needs update, False otherwise
        """
        return bool(cls.get("map_needs_update"))
    
    @classmethod
    def map_updated(cls):
        """
        Mark that the map has been updated.
        
        This method clears the map update flag after the map
        has been successfully updated.
        """
        cls.set("map_needs_update", False)