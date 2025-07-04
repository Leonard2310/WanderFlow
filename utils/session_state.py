"""
Session state management for TripMatch application
"""

import streamlit as st
from typing import Dict, Any, Optional

class SessionState:
    """Gestisce lo stato della sessione in modo più organizzato e consistente."""
    
    # Aggiornato con i nuovi campi per la gestione del pulsante di conferma
    DEFAULTS = {
        "workflow_id": None,
        "pref_task_id": None,
        "show_task_id": None,
        "choice_task_id": None,
        "itinerary": None,
        "extra_requested": False,
        "extra_info": None,
        "selected_country": "",
        "confirmed_country": "",  # Nuovo: paese confermato con il pulsante
        "last_selected_country": "",
        "last_confirmed_country": "",  # Nuovo: per tracking del cambio di paese confermato
        "current_step": 0,
        "map_zoom": 2,
        "map_center": [30, 0],
        "preferences_submitted": False,
        "itinerary_confirmed": False,
        "workflow_completed": False,  # Nuovo: per tracking completamento workflow
        "country_selection_made": False,  # Nuovo: per tracking selezione paese
        "map_needs_update": False  # Nuovo: per tracking aggiornamenti mappa
    }
    
    @classmethod
    def initialize(cls):
        """Inizializza tutti i valori di default se non esistono in st.session_state."""
        for key, value in cls.DEFAULTS.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    @classmethod
    def reset(cls):
        """Resetta lo stato della sessione ai valori di default."""
        for key, value in cls.DEFAULTS.items():
            st.session_state[key] = value
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Ottiene un valore dallo stato della sessione."""
        return st.session_state.get(key, default)
    
    @classmethod
    def set(cls, key: str, value: Any):
        """Imposta un valore nello stato della sessione."""
        st.session_state[key] = value
    
    @classmethod
    def update(cls, **kwargs):
        """Aggiorna più valori nello stato della sessione."""
        for key, value in kwargs.items():
            st.session_state[key] = value
    
    @classmethod
    def get_debug_info(cls) -> Dict[str, Any]:
        """Ottiene informazioni di debug sullo stato attuale."""
        return {
            "workflow_id": cls.get("workflow_id"),
            "current_step": cls.get("current_step"),
            "pref_task_id": cls.get("pref_task_id"),
            "show_task_id": cls.get("show_task_id"),
            "choice_task_id": cls.get("choice_task_id"),
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
        """Verifica se un workflow è stato avviato."""
        return bool(cls.get("workflow_id"))
    
    @classmethod
    def has_itinerary(cls) -> bool:
        """Verifica se l'itinerario è stato generato."""
        return bool(cls.get("itinerary"))
    
    @classmethod
    def is_extra_requested(cls) -> bool:
        """Verifica se sono state richieste informazioni aggiuntive."""
        return bool(cls.get("extra_requested"))
    
    @classmethod
    def get_current_step(cls) -> int:
        """Ottiene il passo corrente del workflow."""
        return cls.get("current_step", 0)
    
    @classmethod
    def advance_step(cls):
        """Avanza al passo successivo."""
        current = cls.get_current_step()
        cls.set("current_step", min(current + 1, 3))
    
    @classmethod
    def set_step(cls, step: int):
        """Imposta un passo specifico."""
        cls.set("current_step", max(0, min(step, 3)))
    
    # Nuovi metodi per la gestione del paese confermato
    @classmethod
    def has_confirmed_country(cls) -> bool:
        """Verifica se un paese è stato confermato."""
        return bool(cls.get("confirmed_country"))
    
    @classmethod
    def get_confirmed_country(cls) -> str:
        """Ottiene il paese confermato."""
        return cls.get("confirmed_country", "")
    
    @classmethod
    def confirm_country(cls, country: str):
        """Conferma un paese per la visualizzazione sulla mappa."""
        cls.update(
            confirmed_country=country,
            country_selection_made=True,
            map_needs_update=True
        )
    
    @classmethod
    def reset_country_selection(cls):
        """Resetta la selezione del paese."""
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
        """Verifica se il paese confermato è cambiato."""
        current = cls.get("confirmed_country", "")
        last = cls.get("last_confirmed_country", "")
        return current != last
    
    @classmethod
    def mark_country_processed(cls):
        """Segna che il cambio di paese è stato processato."""
        cls.set("last_confirmed_country", cls.get("confirmed_country", ""))
    
    @classmethod
    def needs_map_update(cls) -> bool:
        """Verifica se la mappa necessita di aggiornamento."""
        return bool(cls.get("map_needs_update"))
    
    @classmethod
    def map_updated(cls):
        """Segna che la mappa è stata aggiornata."""
        cls.set("map_needs_update", False)