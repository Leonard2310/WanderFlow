"""
Map Components for WanderFlow Application

This module provides interactive map functionality for the WanderFlow travel
planning application, including country selection, map rendering, and geographic
data visualization using Folium and GeoPandas.
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
    """
    Collection of map-related components for geographic visualization.
    
    This class provides static methods for creating interactive maps,
    handling country selection, and managing map state within the
    WanderFlow application.
    """

    @staticmethod
    @st.cache_data(show_spinner=False)
    def load_countries_geojson():
        """
        Load GeoJSON data for world countries with caching.
        
        This method fetches geographic data from a remote source and caches
        it to improve performance on subsequent loads.
        
        Returns:
            GeoDataFrame or None: Geographic data for world countries,
                                 None if loading fails
        """
        try:
            gdf = gpd.read_file(AppConfig.WORLD_GEOJSON_URL)
            return gdf
        except Exception as e:
            st.error(f"Error loading geographic data for map: {e}")
            return None

    @staticmethod
    def create_enhanced_map(selected_country: str = "") -> folium.Map:
        """
        Create an enhanced interactive map with dynamic zoom and styling.
        
        This method creates a Folium map with custom styling, dynamic zoom
        levels, and country highlighting based on user selection.
        
        Args:
            selected_country (str): Name of the selected country to highlight
            
        Returns:
            folium.Map: Configured Folium map instance
        """
        # Get defaults from session state
        map_center = SessionState.get("map_center", [30, 0])
        map_zoom = SessionState.get("map_zoom", 2)

        # Adjust map parameters based on whether a country is selected
        if selected_country:
            # Country selected - use specific zoom and center
            map_config = {
                "location": map_center,
                "zoom_start": map_zoom,
                "prefer_canvas": True,
                "max_zoom": 16,
                "min_zoom": 2
            }
        else:
            # No country selected - use world view with better fit
            map_config = {
                "location": [20, 0],
                "zoom_start": 2,
                "prefer_canvas": True,
                "max_zoom": 16,
                "min_zoom": 1
            }

        m = folium.Map(**map_config)
        
        # Add Stamen Watercolor tile layer with minimal attribution
        folium.raster_layers.TileLayer(
            tiles="https://stamen-tiles.a.ssl.fastly.net/watercolor/{z}/{x}/{y}.jpg",
            attr=".",
            name="Stamen Watercolor",
            overlay=False,
            control=False
        ).add_to(m)

        countries_gdf = MapComponents.load_countries_geojson()
        if countries_gdf is None:
            return m

        if selected_country:
            try:
                # Search for country in geographic data
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

                        # Update session state if coordinates have changed significantly
                        if (
                            isinstance(current_session_center, (list, tuple)) and len(current_session_center) >= 2
                            and (abs(new_center[0] - current_session_center[0]) > 0.1 or
                                 abs(new_center[1] - current_session_center[1]) > 0.1)
                        ) or new_zoom != current_session_zoom:
                            SessionState.update(
                                map_center=new_center,
                                map_zoom=new_zoom
                            )

                        # Add country highlight with custom styling
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

                        # Add marker at country center
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
        Render country selector interface with confirmation button.
        
        This method creates a two-column layout with a country selection dropdown
        and a confirmation button, along with a reset option. It manages the
        state between selected and confirmed countries.
        
        Args:
            available_countries (list): List of available country names
            current_selection (str): Currently selected country name
            
        Returns:
            tuple: (selected_country, confirmed_country, button_pressed)
                  - selected_country: Currently selected country from dropdown
                  - confirmed_country: Country confirmed with button press
                  - button_pressed: Boolean indicating if confirm button was pressed
        """
        # Layout with columns for left-right alignment
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Country selection dropdown - left aligned
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
            # Confirmation button - right aligned
            # Add spacing to align button with selectbox
            st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
            confirm_button = st.button(
                "🗺️ Show Map",
                disabled=(not selected_country),
                type="primary",
                key="confirm_country_button",
                use_container_width=True
            )
        
        # Reset button in new row, centered
        col_reset1, col_reset2, col_reset3 = st.columns([1, 1, 1])
        with col_reset2:
            reset_button = st.button(
                "🔄 Reset",
                key="reset_country_button",
                use_container_width=True
            )
        
        # Handle confirmation logic
        confirmed_country = SessionState.get("confirmed_country", "")
        
        if confirm_button and selected_country:
            # Update confirmed country
            SessionState.set("confirmed_country", selected_country)
            confirmed_country = selected_country
            st.success(f"✅ Map will show: **{selected_country}**")
            
        elif reset_button:
            # Complete reset
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
        
        # Show current status
        if confirmed_country and confirmed_country != selected_country:
            st.info(f"📍 Currently showing: **{confirmed_country}** | Selected: **{selected_country or 'None'}**")
        
        return selected_country, confirmed_country, confirm_button

    @staticmethod
    def render_interactive_map(confirmed_country: str = ""):
        """
        Render the interactive map component with conditional display.
        
        This method renders a Folium map only when a country has been confirmed
        by the user. It includes custom CSS styling and handles map state updates
        based on user interactions.
        
        Args:
            confirmed_country (str): Name of the confirmed country to display
            
        Returns:
            dict or None: Map interaction data if map is rendered, None otherwise
        """
        # Only render map if country is confirmed
        if not confirmed_country:
            return None

        current_last_confirmed = SessionState.get("last_confirmed_country", "")
        if confirmed_country != current_last_confirmed:
            # Update state before creating map
            MapComponents.update_map_state(confirmed_country)
            SessionState.set("last_confirmed_country", confirmed_country)

        # Country confirmed - show complete map
        map_height = 400 

        # Create map with updated state
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

        # Update state if zoom or center change due to user interaction
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
        """
        Get center coordinates and zoom level for a specific country.
        
        This method retrieves the geographic center and appropriate zoom level
        for a given country using the application configuration.
        
        Args:
            country (str): Name of the country
            
        Returns:
            tuple: (center_coordinates, zoom_level) where center_coordinates
                  is [latitude, longitude] and zoom_level is an integer
        """
        center, zoom = AppConfig.get_region_info(country)
        return center, zoom

    @staticmethod
    def update_map_state(country: str):
        """
        Update map state based on selected country.
        
        This method updates the session state with appropriate map center
        and zoom level for the selected country, or resets to world view
        if no country is selected.
        
        Args:
            country (str): Name of the selected country, empty string for reset
        """
        if country:
            center, zoom = MapComponents.get_country_center_and_zoom(country)
            SessionState.update(
                map_center=center,
                map_zoom=zoom,
                selected_country=country
            )
        else:
            SessionState.update(
                map_center=[20, 0],
                map_zoom=2,
                selected_country="",
                last_confirmed_country=""
            )