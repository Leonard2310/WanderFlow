# 🌍 TripMatch BPA - Intelligent Travel Planning System

The digital transformation of travel planning has created new opportunities for **intelligent automation** and **personalized user experiences**. As travelers increasingly demand customized itineraries that match their specific preferences, duration, and destination choices, traditional static planning tools fall short. **TripMatch BPA** addresses this gap by implementing a **Business Process Automation (BPA)** solution that seamlessly integrates workflow orchestration with interactive user interfaces.

**TripMatch BPA** is a sophisticated travel planning platform that leverages **Orkes Conductor** for workflow orchestration and **Streamlit** for dynamic user interaction. The system intelligently adapts to trip duration—offering **three curated city options for short trips (≤3 days)** and **comprehensive regional itineraries for longer journeys (≥5 days)**. Through its modular architecture, the platform handles complex decision trees, user preferences, and real-time task management while providing an intuitive, map-integrated interface.

The platform addresses the challenge of **dynamic workflow routing** based on user input, implementing conditional logic that determines whether travelers receive multiple city options or a single comprehensive itinerary. This intelligent bifurcation ensures optimal user experience while maintaining workflow efficiency and scalability across different travel scenarios.

## Features

- **🔄 Intelligent Workflow Orchestration** using Orkes Conductor
- **🗺️ Interactive Map Integration** with country selection and visualization
- **⏱️ Dynamic Trip Duration Handling** (≤3 days: multiple options, ≥5 days: single itinerary)
- **📋 Comprehensive Preference Management** (destinations, vacation styles, countries)
- **📄 Professional PDF Generation** with enhanced styling and branding
- **💬 Additional Information Requests** with conditional workflow branching
- **🎨 Modern UI/UX** with custom CSS styling and responsive design
- **📱 Progressive Step Indicators** for enhanced user experience

## Requirements

- **Python 3.8+**
  All dependencies are listed in `requirements.txt`. Install via:
  ```bash
  pip install -r requirements.txt
  ```

- **Orkes Conductor Access**
  Active subscription and API credentials for workflow orchestration:
  - `CONDUCTOR_AUTH_KEY`
  - `CONDUCTOR_AUTH_SECRET` 
  - `CONDUCTOR_SERVER_URL`

- **Virtual Environment** (Recommended)
  Create and activate a virtual environment:
  ```bash
  python -m venv BPA_TripMatch
  source BPA_TripMatch/bin/activate  # On macOS/Linux
  ```

## Architecture & Module Overview

TripMatch BPA follows a modular, service-oriented architecture designed for scalability and maintainability:

### Core Components

1. **`app.py`** - Main Application Controller
   - **Streamlit Interface**: Renders the primary user interface with step-by-step navigation
   - **Workflow Integration**: Manages Orkes Conductor workflow lifecycle and task polling
   - **Route Management**: Implements intelligent routing based on trip duration and user selections
   - **Session Management**: Handles persistent state across user interactions
   - **Error Handling**: Provides comprehensive error recovery and user feedback

2. **`components/workflow_manager.py`** - Workflow Orchestration Layer
   - **Task Management**: Handles workflow initialization, task polling, and completion
   - **Conditional Logic**: Implements business rules for short vs. long trip routing
   - **API Integration**: Manages Orkes Conductor API communication and error handling
   - **Data Processing**: Transforms workflow outputs into user-friendly formats
   - **Debug Utilities**: Provides workflow introspection and troubleshooting tools

3. **`components/ui_components.py`** - User Interface Components
   - **Form Rendering**: Creates interactive forms for user preferences and selections
   - **Data Visualization**: Renders travel itineraries with enhanced formatting
   - **Input Validation**: Ensures data integrity and provides user feedback
   - **Styling Management**: Applies consistent CSS styling across components
   - **Responsive Design**: Adapts to different screen sizes and device types

4. **`components/map_components.py`** - Geographic Visualization
   - **Interactive Maps**: Renders Folium-based maps with country highlighting
   - **Geographic Data**: Processes GeoJSON data for country boundaries and features
   - **Dynamic Centering**: Automatically adjusts map view based on selected countries
   - **Performance Optimization**: Implements caching for improved map loading times
   - **User Interaction**: Handles map clicks, zooms, and selection feedback

5. **`utils/session_state.py`** - State Management
   - **Persistent Storage**: Manages user session data across page interactions
   - **State Validation**: Ensures data consistency and prevents corruption
   - **Debug Information**: Provides comprehensive state inspection utilities
   - **Migration Support**: Handles schema changes and backward compatibility
   - **Performance Optimization**: Minimizes state overhead and memory usage

6. **`utils/pdf_generator.py`** - Document Generation
   - **Professional Styling**: Creates branded PDF documents with consistent formatting
   - **Dynamic Content**: Integrates user preferences and itinerary data
   - **Multi-language Support**: Handles various text encodings and special characters
   - **Template Management**: Provides flexible document structure and layout
   - **Export Options**: Supports multiple output formats and quality settings

7. **`config/app_config.py`** - Configuration Management
   - **Environment Variables**: Centralizes API keys and service endpoints
   - **Country Data**: Maintains comprehensive geographic and cultural information
   - **UI Constants**: Defines styling, colors, and layout parameters
   - **Workflow Settings**: Configures task timeouts, retry policies, and versions
   - **Feature Flags**: Enables conditional feature activation and testing

### Workflow Architecture

![TripMatch_BPA](https://github.com/user-attachments/assets/4c3cc777-70c7-44fe-bd91-0dd792c9ca74)

## Setup & Usage

### 1. **Clone and Install Dependencies**
```bash
git clone https://github.com/your-username/TripMatchBPA.git
cd TripMatchBPA

# Create virtual environment
python -m venv BPA_TripMatch
source BPA_TripMatch/bin/activate  # On macOS/Linux
# or
BPA_TripMatch\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. **Configure Environment Variables**
Create a `credentials.env` file in the root directory:
```env
CONDUCTOR_AUTH_KEY=your_orkes_auth_key
CONDUCTOR_AUTH_SECRET=your_orkes_auth_secret
CONDUCTOR_SERVER_URL=https://developer.orkescloud.com/api
```

### 3. **Deploy Workflow to Orkes Conductor**
Ensure your TripMatch_BPA workflow (version 26) is deployed and active in your Orkes Conductor instance with the following tasks:
- `UserPreferences` - Collects user input
- `ShowItinerary` - Generates single itinerary (long trips)
- `ChoiceTravelCity` - Provides three options (short trips)
- `AskforAddInfo_ref` - Requests additional information
- `ShowMoreInformation` - Provides additional details

### 4. **Launch the Application**
```bash
# Activate virtual environment
source BPA_TripMatch/bin/activate

# Start Streamlit application
streamlit run app.py
```

The application will be available at `http://localhost:8501`

### 5. **Using the Application**

1. **Welcome Screen**: Click "Start Planning Your Trip" to begin
2. **Preferences Form**: 
   - Select trip duration (1-10+ days)
   - Choose travel period
   - Select destination types (nature, cities, beach, mountains)
   - Pick a country from the interactive map
   - Choose vacation styles (relaxation, adventure, culture, etc.)
3. **Trip Planning**:
   - **Short trips (≤3 days)**: Choose from three curated city options
   - **Long trips (≥5 days)**: Review the comprehensive regional itinerary
4. **Acceptance & Customization**: Accept your itinerary and optionally request additional information
5. **Export**: Download your personalized travel plan as a professional PDF

## User Interface Features

### Interactive Map Integration
- **Country Selection**: Visual country picker with geographic highlighting
- **Dynamic Zoom**: Automatic map centering based on selected destinations
- **Real-time Updates**: Instant map updates reflecting user choices
- **Geographic Data**: Comprehensive country boundary and feature data

### Responsive Design
- **Multi-device Support**: Optimized for desktop, tablet, and mobile viewing
- **Progressive Enhancement**: Graceful degradation for slower connections
- **Accessibility**: WCAG-compliant design with keyboard navigation support
- **Performance**: Optimized loading times and smooth interactions

### Modern UI Components
- **Step Indicators**: Visual progress tracking throughout the planning process
- **Custom Styling**: Consistent branding and professional appearance
- **Interactive Forms**: Real-time validation and user feedback
- **Animation**: Smooth transitions and micro-interactions

## Development & Customization

### Adding New Countries
Update `config/app_config.py`:
```python
COUNTRIES_DATA = {
    "Your_Region": {
        "countries": ["New Country 1", "New Country 2"],
        "center": [latitude, longitude],
        "zoom": zoom_level
    }
}
```

### Workflow Customization
Modify workflow logic in `components/workflow_manager.py`:
```python
def wait_for_custom_task(self, wf_id: str) -> Optional[Dict]:
    # Implement custom task waiting logic
    pass
```

### UI Customization
Extend UI components in `components/ui_components.py`:
```python
@staticmethod
def render_custom_component():
    # Add new UI components
    pass
```

## Testing & Debugging

### Debug Mode
Enable debug information by adding to your session state:
```python
SessionState.set("debug_mode", True)
```

### Workflow Debugging
Use built-in debugging utilities:
```python
# Check workflow status
debug_info = workflow_manager.get_workflow_debug_info(workflow_id)

# Analyze workflow routing
switch_analysis = workflow_manager.debug_workflow_switch_logic(workflow_id)
```

## Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork the repository** and create a feature branch
2. **Follow coding standards** with proper documentation
3. **Add tests** for new functionality
4. **Update documentation** as needed
5. **Submit a pull request** with a clear description

## License

This project is licensed under the [GPL-3.0 license](LICENSE). For full terms, see the LICENSE file.

## Authors

* [Leonardo Catello](https://github.com/Leonard2310)
* [Aurora D'Ambrosio](https://github.com/AuroraD-99)
* [Luisa Ciniglio](https://github.com/LuisaCiniglio)
