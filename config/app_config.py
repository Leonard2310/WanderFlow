"""
Configuration module for TripMatch application
"""

import os
from typing import Dict, Any, List, Tuple
import streamlit as st
from dotenv import load_dotenv

class AppConfig:
    """Centralized configuration management"""

    # App constants
    APP_TITLE = "TripMatch - Plan Your Adventure"
    APP_ICON = "🌍"

    # Workflow configuration
    WORKFLOW_NAME = "TripMatch_BPA"
    WORKFLOW_VERSION = 26

    # UI Configuration
    MAX_ATTEMPTS = 30
    POLL_INTERVAL = 2  # seconds

    # Countries data organized by region
    COUNTRIES_DATA = {
        "Europe": {
            "countries": ["Italy", "France", "Spain", "Germany", "Greece", "Portugal",
                         "United Kingdom", "Malta", "Netherlands", "Switzerland", "Austria",
                         "Norway", "Sweden", "Finland", "Ireland", "Poland", "Croatia",
                         "Czech Republic", "Hungary", "Belgium", "Denmark", "Iceland"],
            "center": [54.5, 15.2],
            "zoom": 4
        },
        "Asia": {
            "countries": ["Japan", "China", "Thailand", "India", "Indonesia", "Vietnam",
                         "South Korea", "Philippines", "Singapore", "Maldives", "Nepal",
                         "Sri Lanka", "Malaysia", "Cambodia", "Laos", "Myanmar"],
            "center": [30, 100],
            "zoom": 3
        },
        "Africa": {
            "countries": ["Egypt", "Morocco", "South Africa", "Kenya", "Tanzania",
                         "Mauritius", "Madagascar", "Tunisia", "Namibia", "Botswana",
                         "Zimbabwe", "Zambia", "Uganda", "Ethiopia"],
            "center": [0, 20],
            "zoom": 3
        },
        "North America": {
            "countries": ["United States", "Canada", "Mexico", "Cuba", "Dominican Republic",
                         "Jamaica", "Bahamas", "Costa Rica", "Panama", "Guatemala"],
            "center": [45, -100],
            "zoom": 3
        },
        "South America": {
            "countries": ["Colombia", "Peru", "Chile", "Argentina", "Brazil", "Uruguay",
                         "Ecuador", "Bolivia", "Venezuela", "Paraguay", "Suriname"],
            "center": [-15, -60],
            "zoom": 3
        },
        "Oceania": {
            "countries": ["Australia", "New Zealand", "Fiji", "Samoa", "French Polynesia",
                         "Vanuatu", "Tonga", "Papua New Guinea"],
            "center": [-25, 140],
            "zoom": 4
        },
        "Middle East": {
            "countries": ["United Arab Emirates", "Israel", "Jordan", "Turkey", "Qatar",
                         "Saudi Arabia", "Oman", "Kuwait", "Lebanon", "Cyprus"],
            "center": [29, 45],
            "zoom": 5
        }
    }

    # Country flags mapping (added for better UX)
    COUNTRY_FLAGS = {
        "Italy": "🇮🇹", "France": "🇫🇷", "Spain": "🇪🇸", "Germany": "🇩🇪", "Greece": "🇬🇷", "Portugal": "🇵🇹",
        "United Kingdom": "🇬🇧", "Malta": "🇲🇹", "Netherlands": "🇳🇱", "Switzerland": "🇨🇭", "Austria": "🇦🇹",
        "Norway": "🇳🇴", "Sweden": "🇸🇪", "Finland": "🇫🇮", "Ireland": "🇮🇪", "Poland": "🇵🇱", "Croatia": "🇭🇷",
        "Czech Republic": "🇨🇿", "Hungary": "🇭🇺", "Belgium": "🇧🇪", "Denmark": "🇩🇰", "Iceland": "🇮🇸",
        "Japan": "🇯🇵", "China": "🇨🇳", "Thailand": "🇹🇭", "India": "🇮🇳", "Indonesia": "🇮🇩", "Vietnam": "🇻🇳",
        "South Korea": "🇰🇷", "Philippines": "🇵🇭", "Singapore": "🇸🇬", "Maldives": "🇲🇻", "Nepal": "🇳🇵",
        "Sri Lanka": "🇱🇰", "Malaysia": "🇲🇾", "Cambodia": "🇰🇭", "Laos": "🇱🇦", "Myanmar": "🇲🇲",
        "Egypt": "🇪🇬", "Morocco": "🇲🇦", "South Africa": "🇿🇦", "Kenya": "🇰🇪", "Tanzania": "🇹🇿",
        "Mauritius": "🇲🇺", "Madagascar": "🇲🇬", "Tunisia": "🇹🇳", "Namibia": "🇳🇦", "Botswana": "🇧🇼",
        "Zimbabwe": "🇿🇼", "Zambia": "🇿🇲", "Uganda": "🇺🇬", "Ethiopia": "🇪🇹",
        "United States": "🇺🇸", "Canada": "🇨🇦", "Mexico": "🇲🇽", "Cuba": "🇨🇺", "Dominican Republic": "🇩🇴",
        "Jamaica": "🇯🇲", "Bahamas": "🇧🇸", "Costa Rica": "🇨🇷", "Panama": "🇵🇦", "Guatemala": "🇬🇹",
        "Colombia": "🇨🇴", "Peru": "🇵🇪", "Chile": "🇨🇱", "Argentina": "🇦🇷", "Brazil": "🇧🇷", "Uruguay": "🇺🇾",
        "Ecuador": "🇪🇨", "Bolivia": "🇧🇴", "Venezuela": "🇻🇪", "Paraguay": "🇵🇾", "Suriname": "🇸🇷",
        "Australia": "🇦🇺", "New Zealand": "🇳🇿", "Fiji": "🇫🇯", "Samoa": "🇼🇸", "French Polynesia": "🇵🇫",
        "Vanuatu": "🇻🇺", "Tonga": "🇹🇴", "Papua New Guinea": "🇵🇬",
        "United Arab Emirates": "🇦🇪", "Israel": "🇮🇱", "Jordan": "🇯🇴", "Turkey": "🇹🇷", "Qatar": "🇶🇦",
        "Saudi Arabia": "🇸🇦", "Oman": "🇴🇲", "Kuwait": "🇰🇼", "Lebanon": "🇱🇧", "Cyprus": "🇨🇾"
    }

    # Form options
    DESTINATION_TYPES = {
        "natura": "🌿 Nature & Wildlife",
        "città": "🏙️ Cities & Culture",
        "mare": "🏖️ Beach & Coast",
        "montagna": "⛰️ Mountains & Hiking"
    }

    VACATION_STYLES = {
        "relax": "😌 Relaxation & Wellness",
        "villeggiatura": "🏖️ Resort & Leisure",
        "avventura": "🎒 Adventure & Exploration",
        "cultura": "🎭 Culture & History",
        "gastronomia": "🍽️ Food & Gastronomy"
    }

    # GeoJSON URL for world countries
    WORLD_GEOJSON_URL = "https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json"

    @classmethod
    def get_country_options(cls) -> List[str]:
        """Get all country options for selectbox with flags"""
        country_options = []  # Removed empty option for cleaner UI
        for region, region_data in cls.COUNTRIES_DATA.items():
            for country in region_data["countries"]:
                flag = cls.COUNTRY_FLAGS.get(country, "🗺️")
                country_options.append(f"{country} {flag}")
        return country_options

    @classmethod
    def get_countries_by_region(cls) -> Dict[str, List[str]]:
        """Get countries organized by region with flags"""
        countries_by_region = {}
        for region, region_data in cls.COUNTRIES_DATA.items():
            countries_by_region[region] = []
            for country in region_data["countries"]:
                flag = cls.COUNTRY_FLAGS.get(country, "🗺️")
                countries_by_region[region].append(f"{country} {flag}")
        return countries_by_region

    @classmethod
    def get_country_options_grouped(cls) -> List[str]:
        """Get all country options grouped by continent for better UX"""
        grouped_options = []
        
        # Order of continents for better UX
        continent_order = ["Europe", "North America", "Asia", "Africa", "South America", "Oceania", "Middle East"]
        
        for continent in continent_order:
            if continent in cls.COUNTRIES_DATA:
                region_data = cls.COUNTRIES_DATA[continent]
                # Add continent header
                grouped_options.append(f"──── {continent} ────")
                
                # Add countries in this continent
                for country in region_data["countries"]:
                    flag = cls.COUNTRY_FLAGS.get(country, "🗺️")
                    grouped_options.append(f"   {country} {flag}")
        
        return grouped_options

    @classmethod
    def extract_country_from_grouped_option(cls, option: str) -> str:
        """Extract country name from grouped selectbox option"""
        if not option or option.startswith("────") or option.startswith("Select"):
            return ""
        
        # Remove leading spaces and flag
        option = option.strip()
        if option.startswith("   "):
            option = option[3:]  # Remove the 3 leading spaces
        
        # Remove flag at the end
        for flag in cls.COUNTRY_FLAGS.values():
            if option.endswith(flag):
                return option.replace(flag, "").strip()
        
        return option.strip()

    @classmethod
    def extract_country_from_option(cls, option: str) -> str:
        """Extract country name from selectbox option, removing flag"""
        if option:
            # Remove any flag emoji at the end
            for flag in cls.COUNTRY_FLAGS.values():
                if option.endswith(flag):
                    return option.replace(flag, "").strip()
            # If no flag found, assume it's just the country name
            return option.strip()
        return ""

    @classmethod
    def get_region_info(cls, country: str) -> Tuple[List[float], int]:
        """Get region center and zoom for a country"""
        for region_data in cls.COUNTRIES_DATA.values():
            if country in region_data["countries"]:
                return region_data["center"], region_data["zoom"]
        return [30, 0], 2  # Default center and zoom

    @classmethod
    def get_country_specific_info(cls, country: str) -> Dict[str, Any]:
        """Get specific coordinates and zoom for individual countries"""
        # Extended mapping for better country-specific positioning
        country_coords = {
            "Italy": {"center": [41.8719, 12.5674], "zoom": 6},
            "France": {"center": [46.2276, 2.2137], "zoom": 6},
            "Spain": {"center": [40.4637, -3.7492], "zoom": 6},
            "Germany": {"center": [51.1657, 10.4515], "zoom": 6},
            "Greece": {"center": [39.0742, 21.8243], "zoom": 6},
            "Portugal": {"center": [39.3999, -8.2245], "zoom": 6},
            "United Kingdom": {"center": [55.3781, -3.4360], "zoom": 6},
            "Japan": {"center": [36.2048, 138.2529], "zoom": 6},
            "Thailand": {"center": [15.8700, 100.9925], "zoom": 6},
            "United States": {"center": [39.8283, -98.5795], "zoom": 4},
            "Australia": {"center": [-25.2744, 133.7751], "zoom": 5},
            "Brazil": {"center": [-14.2350, -51.9253], "zoom": 4},
            "Canada": {"center": [56.1304, -106.3468], "zoom": 4},
            "China": {"center": [35.8617, 104.1954], "zoom": 4},
            "India": {"center": [20.5937, 78.9629], "zoom": 5},
            "Egypt": {"center": [26.8206, 30.8025], "zoom": 6},
            "Morocco": {"center": [31.7917, -7.0926], "zoom": 6},
            "South Africa": {"center": [-30.5595, 22.9375], "zoom": 6},
            "Turkey": {"center": [38.9637, 35.2433], "zoom": 6},
            "Mexico": {"center": [23.6345, -102.5528], "zoom": 5},
            "Argentina": {"center": [-38.4161, -63.6167], "zoom": 5},
            "Chile": {"center": [-35.6751, -71.5430], "zoom": 5},
            "Colombia": {"center": [4.5709, -74.2973], "zoom": 6},
            "Peru": {"center": [-9.1900, -75.0152], "zoom": 6},
            "New Zealand": {"center": [-40.9006, 174.8860], "zoom": 6},
            "Norway": {"center": [60.4720, 8.4689], "zoom": 5},
            "Sweden": {"center": [60.1282, 18.6435], "zoom": 5},
            "Finland": {"center": [61.9241, 25.7482], "zoom": 5},
            "Iceland": {"center": [64.9631, -19.0208], "zoom": 7},
            "Indonesia": {"center": [-0.7893, 113.9213], "zoom": 5},
            "Philippines": {"center": [12.8797, 121.7740], "zoom": 6},
            "Vietnam": {"center": [14.0583, 108.2772], "zoom": 6},
            "Malaysia": {"center": [4.2105, 101.9758], "zoom": 6},
            "Singapore": {"center": [1.3521, 103.8198], "zoom": 11},
            "Maldives": {"center": [3.2028, 73.2207], "zoom": 8},
            "Nepal": {"center": [28.3949, 84.1240], "zoom": 7},
            "Sri Lanka": {"center": [7.8731, 80.7718], "zoom": 7},
            "United Arab Emirates": {"center": [23.4241, 53.8478], "zoom": 7},
            "Israel": {"center": [31.0461, 34.8516], "zoom": 7},
            "Jordan": {"center": [30.5852, 36.2384], "zoom": 7},
            "Malta": {"center": [35.9375, 14.3754], "zoom": 10},
            "Cyprus": {"center": [35.1264, 33.4299], "zoom": 8},
            "Ireland": {"center": [53.1424, -7.6921], "zoom": 7},
            "Switzerland": {"center": [46.8182, 8.2275], "zoom": 7},
            "Austria": {"center": [47.5162, 14.5501], "zoom": 7},
            "Netherlands": {"center": [52.1326, 5.2913], "zoom": 7},
            "Belgium": {"center": [50.5039, 4.4699], "zoom": 7},
            "Denmark": {"center": [56.2639, 9.5018], "zoom": 7},
            "Poland": {"center": [51.9194, 19.1451], "zoom": 6},
            "Croatia": {"center": [45.1000, 15.2000], "zoom": 7},
            "Czech Republic": {"center": [49.8175, 15.4730], "zoom": 7},
            "Hungary": {"center": [47.1625, 19.5033], "zoom": 7},
            "South Korea": {"center": [35.9078, 127.7669], "zoom": 7},
            "Cambodia": {"center": [12.5657, 104.9910], "zoom": 7},
            "Laos": {"center": [19.8563, 102.4955], "zoom": 7},
            "Myanmar": {"center": [21.9162, 95.9560], "zoom": 6},
            "Kenya": {"center": [-0.0236, 37.9062], "zoom": 6},
            "Tanzania": {"center": [-6.3690, 34.8888], "zoom": 6},
            "Mauritius": {"center": [-20.3484, 57.5522], "zoom": 10},
            "Madagascar": {"center": [-18.7669, 46.8691], "zoom": 6},
            "Tunisia": {"center": [33.8869, 9.5375], "zoom": 7},
            "Namibia": {"center": [-22.9576, 18.4904], "zoom": 6},
            "Botswana": {"center": [-22.3285, 24.6849], "zoom": 6},
            "Zimbabwe": {"center": [-19.0154, 29.1549], "zoom": 6},
            "Zambia": {"center": [-13.1339, 27.8493], "zoom": 6},
            "Uganda": {"center": [1.3733, 32.2903], "zoom": 7},
            "Ethiopia": {"center": [9.1450, 40.4897], "zoom": 6},
            "Cuba": {"center": [21.5218, -77.7812], "zoom": 7},
            "Dominican Republic": {"center": [18.7357, -70.1627], "zoom": 8},
            "Jamaica": {"center": [18.1096, -77.2975], "zoom": 8},
            "Bahamas": {"center": [25.0343, -77.3963], "zoom": 8},
            "Costa Rica": {"center": [9.7489, -83.7534], "zoom": 8},
            "Panama": {"center": [8.5380, -80.7821], "zoom": 8},
            "Guatemala": {"center": [15.7835, -90.2308], "zoom": 7},
            "Uruguay": {"center": [-32.5228, -55.7658], "zoom": 7},
            "Ecuador": {"center": [-1.8312, -78.1834], "zoom": 7},
            "Bolivia": {"center": [-16.2902, -63.5887], "zoom": 6},
            "Venezuela": {"center": [6.4238, -66.5897], "zoom": 6},
            "Paraguay": {"center": [-23.4425, -58.4438], "zoom": 6},
            "Suriname": {"center": [3.9193, -56.0278], "zoom": 7},
            "Fiji": {"center": [-16.7784, 179.4144], "zoom": 8},
            "Samoa": {"center": [-13.7590, -172.1046], "zoom": 10},
            "French Polynesia": {"center": [-17.6797, -149.4068], "zoom": 8},
            "Vanuatu": {"center": [-15.3767, 166.9592], "zoom": 8},
            "Tonga": {"center": [-21.1789, -175.1982], "zoom": 9},
            "Papua New Guinea": {"center": [-6.3149, 143.9555], "zoom": 6},
            "Qatar": {"center": [25.3548, 51.1839], "zoom": 9},
            "Saudi Arabia": {"center": [23.8859, 45.0792], "zoom": 5},
            "Oman": {"center": [21.4735, 55.9754], "zoom": 6},
            "Kuwait": {"center": [29.3117, 47.4818], "zoom": 8},
            "Lebanon": {"center": [33.8547, 35.8623], "zoom": 8}
        }
        
        if country in country_coords:
            return country_coords[country]["center"], country_coords[country]["zoom"]
        else:
            # Fallback to region info
            return cls.get_region_info(country)

    @classmethod
    @st.cache_data
    def load_environment(cls):
        """Load environment variables"""
        load_dotenv("credentials.env")
        return {
            "auth_key": os.getenv("CONDUCTOR_AUTH_KEY"),
            "auth_secret": os.getenv("CONDUCTOR_AUTH_SECRET"),
            "server_url": os.getenv("CONDUCTOR_SERVER_URL")
        }

    @classmethod
    def validate_environment(cls) -> bool:
        """Validate that all required environment variables are set"""
        env_vars = cls.load_environment()
        return all(env_vars.values())