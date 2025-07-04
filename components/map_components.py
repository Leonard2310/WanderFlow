"""
Map components for WanderFlow application - Fixed version with conditional map display
"""

import streamlit as st
import folium
from streamlit_folium import st_folium
import geopandas as gpd
import pandas as pd
from typing import Optional

from config.app_config import AppConfig
from utils.session_state import SessionState

class MapComponents:
    """Collection of map-related components"""

    @staticmethod
    @st.cache_data(show_spinner=False)
    def load_countries_geojson():
        """Load GeoJSON data for countries"""
        try:
            gdf = gpd.read_file(AppConfig.WORLD_GEOJSON_URL)
            return gdf
        except Exception as e:
            st.error(f"Error loading geographic data for map: {e}")
            return None

    @staticmethod
    def create_enhanced_map(selected_country: str = "") -> folium.Map:
        """Create an enhanced map with dynamic zoom"""

        # Defaults from session state
        map_center = SessionState.get("map_center", [30, 0])
        map_zoom = SessionState.get("map_zoom", 2)

        # Adjust map parameters based on whether a country is selected
        if selected_country:
            # Country selected - use specific zoom and center
            map_config = {
                "location": map_center,
                "zoom_start": map_zoom,
                "prefer_canvas": True,
                "max_zoom": 16,  # Stamen Watercolor ha un max zoom più basso
                "min_zoom": 2
            }
        else:
            # No country selected - use world view with better fit
            map_config = {
                "location": [20, 0],  # Better world center
                "zoom_start": 2,
                "prefer_canvas": True,
                "max_zoom": 16,  # Stamen Watercolor ha un max zoom più basso
                "min_zoom": 1
            }

        m = folium.Map(**map_config)
        
        # Aggiungi il tile layer Stamen Watercolor con attribuzione minimale
        folium.raster_layers.TileLayer(
            tiles="https://stamen-tiles.a.ssl.fastly.net/watercolor/{z}/{x}/{y}.jpg",
            attr=".",  # Attribuzione minimale (solo un punto)
            name="Stamen Watercolor",
            overlay=False,
            control=False  # Nasconde il controllo layer
        ).add_to(m)

        countries_gdf = MapComponents.load_countries_geojson()
        if countries_gdf is None:
            return m

        if selected_country:
            try:
                country_data = countries_gdf[
                    countries_gdf['name'].str.contains(selected_country, case=False, na=False) |
                    countries_gdf.get('NAME', pd.Series()).str.contains(selected_country, case=False, na=False)
                ]

                if not country_data.empty:
                    geometry = country_data.geometry.iloc[0]
                    if hasattr(geometry, 'centroid') and not geometry.is_empty:
                        centroid = geometry.centroid
                        new_center = [centroid.y, centroid.x]
                        new_zoom = 6

                        m.location = new_center
                        m.zoom_start = new_zoom

                        current_session_center = SessionState.get("map_center")
                        current_session_zoom = SessionState.get("map_zoom")

                        # Controllo difensivo prima di confrontare
                        if (
                            isinstance(current_session_center, (list, tuple)) and len(current_session_center) >= 2
                            and (abs(new_center[0] - current_session_center[0]) > 0.1 or
                                 abs(new_center[1] - current_session_center[1]) > 0.1)
                        ) or new_zoom != current_session_zoom:
                            SessionState.update(
                                map_center=new_center,
                                map_zoom=new_zoom
                            )

                        folium.GeoJson(
                            geometry,
                            style_function=lambda x: {
                                'fillColor': '#667eea',
                                'color': '#ffffff',
                                'weight': 3,
                                'fillOpacity': 0.7,
                                'dashArray': '5, 5'
                            },
                            tooltip=folium.Tooltip(
                                f"<strong>{selected_country}</strong><br>Selected destination",
                                permanent=True,
                                direction='center'
                            )
                        ).add_to(m)

                        folium.Marker(
                            new_center,
                            popup=f"<b>{selected_country}</b><br>Your selected destination!",
                            icon=folium.Icon(color='red', icon='star', prefix='fa')
                        ).add_to(m)

            except Exception as e:
                st.warning(f"Unable to process map for '{selected_country}': {e}")
                m.location = SessionState.get("map_center", [30, 0])
                m.zoom_start = SessionState.get("map_zoom", 2)

        return m

    @staticmethod
    def render_country_selector_with_confirm(available_countries: list, current_selection: str = "") -> tuple:
        """
        Render country selector with confirm button
        Returns: (selected_country, confirmed_country, button_pressed)
        """
        # Layout con colonne per allineamento sinistra-destra
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Selectbox per selezione paese - allineato a sinistra
            selected_country = st.selectbox(
                "🌍 Select your destination country:",
                options=[""] + available_countries,
                index=0 if not current_selection else (
                    available_countries.index(current_selection) + 1 
                    if current_selection in available_countries else 0
                ),
                key="country_selector"
            )
        
        with col2:
            # Pulsante di conferma - allineato a destra
            # Aggiungi spazio per allineare il pulsante al selectbox
            st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
            confirm_button = st.button(
                "🗺️ Show Map",
                disabled=(not selected_country),
                type="primary",
                key="confirm_country_button",
                use_container_width=True
            )
        
        # Pulsante reset in una nuova riga, centrato
        col_reset1, col_reset2, col_reset3 = st.columns([1, 1, 1])
        with col_reset2:
            reset_button = st.button(
                "🔄 Reset",
                key="reset_country_button",
                use_container_width=True
            )
        
        # Gestione della logica di conferma
        confirmed_country = SessionState.get("confirmed_country", "")
        
        if confirm_button and selected_country:
            # Aggiorna il paese confermato
            SessionState.set("confirmed_country", selected_country)
            confirmed_country = selected_country
            st.success(f"✅ Map will show: **{selected_country}**")
            
        elif reset_button:
            # Reset completo
            SessionState.update(
                confirmed_country="",
                selected_country="",
                last_selected_country="",
                map_center=[20, 0],
                map_zoom=2
            )
            confirmed_country = ""
            st.info("🔄 Selection reset")
            st.rerun()
        
        # Mostra stato attuale
        if confirmed_country and confirmed_country != selected_country:
            st.info(f"📍 Currently showing: **{confirmed_country}** | Selected: **{selected_country or 'None'}**")
        
        return selected_country, confirmed_country, confirm_button

    @staticmethod
    def render_interactive_map(confirmed_country: str = ""):
        """Render the interactive map component with dynamic height - ONLY if country is confirmed."""
        
        # CORREZIONE PRINCIPALE: Non mostrare nulla se non c'è un paese confermato
        if not confirmed_country:
            # Se non c'è paese confermato, non renderizzare nessun elemento (mappa scompare completamente)
            return None

        current_last_confirmed = SessionState.get("last_confirmed_country", "")
        if confirmed_country != current_last_confirmed:
            # Aggiorna stato prima di creare la mappa
            MapComponents.update_map_state(confirmed_country)
            SessionState.set("last_confirmed_country", confirmed_country)

        # Paese confermato - mostra la mappa completa
        map_height = 400 

        # Ora crea la mappa con stato aggiornato
        map_to_render = MapComponents.create_enhanced_map(confirmed_country)

        # Add custom CSS for better map display
        st.markdown("""
        <style>
        .map-container {
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            margin: 0.5rem 0;
        }
        .map-container iframe {
            border-radius: 10px;
        }
        .stButton > button {
            width: 100%;
            margin-top: 1.5rem;
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown('<div class="map-container">', unsafe_allow_html=True)
        map_data = st_folium(
            map_to_render,
            use_container_width=True,
            height=map_height,
            key="folium_map"
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # Aggiorna stato se zoom o centro cambiano per interazione utente
        if map_data and map_data.get("zoom") is not None and map_data.get("center") is not None:
            current_zoom = SessionState.get("map_zoom")
            current_center = SessionState.get("map_center")

            new_zoom = map_data["zoom"]
            new_center = map_data["center"]

            if (
                isinstance(new_center, (list, tuple)) and len(new_center) >= 2 and
                isinstance(current_center, (list, tuple)) and len(current_center) >= 2
            ):
                if new_zoom != current_zoom or \
                abs(new_center[0] - current_center[0]) > 0.01 or \
                abs(new_center[1] - current_center[1]) > 0.01:
                    SessionState.update(
                        map_zoom=new_zoom,
                        map_center=new_center
                    )

        return map_data

    @staticmethod
    def get_country_center_and_zoom(country: str) -> tuple:
        """Get center coordinates and zoom level for a country"""
        center, zoom = AppConfig.get_region_info(country)
        return center, zoom

    @staticmethod
    def update_map_state(country: str):
        """Update map state based on selected country."""
        if country:
            center, zoom = MapComponents.get_country_center_and_zoom(country)
            SessionState.update(
                map_center=center,
                map_zoom=zoom,
                selected_country=country
            )
        else:
            SessionState.update(
                map_center=[20, 0],  # Better world center
                map_zoom=2,
                selected_country="",
                last_confirmed_country=""
            )