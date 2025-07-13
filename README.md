# 🌍 WanderFlow - AI-Powered Travel Planning System

The digital transformation of travel planning has created new opportunities for **intelligent automation** and **personalized user experiences**. As travelers increasingly demand customized itineraries that match their specific preferences, duration, and destination choices, traditional static planning tools fall short. **WanderFlow** addresses this gap by implementing a **Business Process Automation (BPA)** solution that seamlessly integrates **AI-powered workflow orchestration** with interactive user interfaces.

**WanderFlow** is a sophisticated travel planning platform that leverages **Orkes Conductor** for workflow orchestration, **Large Language Models (LLMs)** for intelligent content generation, and **Streamlit** for dynamic user interaction. The system intelligently adapts to trip duration—offering **three AI-curated city options for short trips (≤3 days)** and **comprehensive regional itineraries for longer journeys (≥5 days)**. Through its modular architecture and advanced prompt engineering, the platform handles complex decision trees, user preferences, and real-time task management while providing an intuitive, map-integrated interface.

The platform addresses the challenge of **dynamic workflow routing** and **AI-driven content generation** based on user input, implementing conditional logic that determines whether travelers receive multiple city options or a single comprehensive itinerary. This intelligent bifurcation, combined with LLM-powered quality assurance, ensures optimal user experience while maintaining workflow efficiency and scalability across different travel scenarios.

## ✨ AI-Powered Features

- **🔄 Intelligent Workflow Orchestration** using Orkes Conductor with AI-driven dynamic decision trees
- **🤖 LLM-Powered Itinerary Generation** leveraging Mistral AI models via OpenRouter for personalized travel planning
- **🎯 Advanced Prompt Engineering** with role-based prompting, context preservation, and multi-layer quality validation
- **🔄 AI Quality Assurance Loops** using iterative LLM validation (DO_WHILE) for coherent and structured outputs
- **🗺️ Smart Map Integration** with AI-guided country selection, geographic visualization, and intelligent centering
- **⏱️ AI-Driven Trip Duration Logic** (≤3 days: 3 AI-curated city options via parallel processing, ≥5 days: single comprehensive AI itinerary)
- **📋 Intelligent Preference Management** with AI-driven preference analysis and prioritization throughout generation
- **🧠 Context-Aware AI Content Generation** adapting to user preferences, trip duration, and geographic constraints
- **📄 AI-Enhanced PDF Generation** with professional styling, branding, and dynamic LLM-generated content integration
- **💬 Smart Travel Recommendations** providing AI-powered practical advice, safety tips, and cultural insights
- **🎨 Modern AI-Optimized UI/UX** with custom CSS styling, responsive design for LLM content, and seamless interaction
- **📱 Progressive AI Journey Tracking** with step indicators for enhanced user feedback during AI processing
- **🔧 Robust AI-Resilient Error Handling** with retry mechanisms, graceful degradation, and workflow resilience

## 📋 AI-Enabled Requirements

- **Python 3.8+** with AI/ML library support
  All dependencies including AI-specific packages are listed in `requirements.txt`.

- **Orkes Conductor Access** for AI workflow orchestration
  Active subscription and API credentials for intelligent workflow management.

- **OpenRouter API Access** for LLM integration
  API key for AI-powered content generation using Mistral models and intelligent travel planning with quality validation.

- **Virtual Environment** (Recommended for AI dependencies)
  Create and activate a virtual environment to isolate AI packages and ensure compatibility.

## 🏗️ Architecture & Module Overview

WanderFlow follows a **modular, AI-integrated architecture** designed for scalability, maintainability, and intelligent automation:

### 🧩 Core Components

1. **`app.py`** - Main Application Controller & AI Integration Hub
   - **Streamlit Interface**: Renders the primary user interface with step-by-step navigation
   - **AI Workflow Integration**: Manages Orkes Conductor lifecycle and LLM-powered task polling
   - **Intelligent Route Management**: Implements AI-driven routing based on trip duration and user selections
   - **Session Management**: Handles persistent state across user interactions with AI context preservation
   - **Error Handling**: Provides comprehensive error recovery and user feedback for AI operations

2. **`components/workflow_manager.py`** - AI Workflow Orchestration Layer
   - **LLM Task Management**: Handles AI workflow initialization, task polling, and completion
   - **Conditional AI Logic**: Implements business rules for short vs. long trip routing with LLM integration
   - **API Integration**: Manages Orkes Conductor and OpenRouter API communication
   - **AI Data Processing**: Transforms LLM outputs into user-friendly formats
   - **Debug Utilities**: Provides AI workflow introspection and troubleshooting tools

3. **`components/ui_components.py`** - User Interface Components
   - **Form Rendering**: Creates interactive forms for user preferences and AI input collection
   - **AI Data Visualization**: Renders LLM-generated travel itineraries with enhanced formatting
   - **Input Validation**: Ensures data integrity for AI processing and provides user feedback
   - **Styling Management**: Applies consistent CSS styling across AI-powered components
   - **Responsive Design**: Adapts to different screen sizes while maintaining AI content readability

4. **`components/map_components.py`** - Geographic Visualization & AI Integration
   - **Interactive Maps**: Renders Folium-based maps with AI-recommended country highlighting
   - **Geographic Data**: Processes GeoJSON data for country boundaries and AI-driven features
   - **Dynamic Centering**: Automatically adjusts map view based on AI-selected destinations
   - **Performance Optimization**: Implements caching for improved map loading with AI data
   - **User Interaction**: Handles map clicks, zooms, and AI-driven selection feedback

5. **`utils/session_state.py`** - State Management & AI Context
   - **Persistent Storage**: Manages user session data and AI context across page interactions
   - **AI State Validation**: Ensures data consistency for LLM operations and prevents corruption
   - **Debug Information**: Provides comprehensive state inspection utilities for AI workflows
   - **Migration Support**: Handles schema changes and backward compatibility for AI features
   - **Performance Optimization**: Minimizes state overhead while preserving AI context

6. **`utils/pdf_generator.py`** - Document Generation & AI Content Integration
   - **Professional Styling**: Creates branded PDF documents with AI-generated content formatting
   - **Dynamic AI Content**: Integrates LLM-generated itineraries and user preferences
   - **Multi-language Support**: Handles various text encodings from AI models and special characters
   - **Template Management**: Provides flexible document structure for AI-generated content
   - **Export Options**: Supports multiple output formats optimized for AI content presentation

7. **`config/app_config.py`** - Configuration Management & AI Settings
   - **Environment Variables**: Centralizes API keys for Orkes, OpenRouter, and AI services
   - **Country Data**: Maintains comprehensive geographic information for AI city selection
   - **UI Constants**: Defines styling, colors, and layout parameters for AI components
   - **AI Workflow Settings**: Configures LLM timeouts, retry policies, and model versions
   - **Feature Flags**: Enables conditional AI feature activation and testing

### 🔄 AI Workflow Architecture

![TripMatch_BPA](https://github.com/user-attachments/assets/4c3cc777-70c7-44fe-bd91-0dd792c9ca74)

The **WanderFlow** workflow implements an intelligent decision-making system that adapts to user preferences and trip duration. The architecture features:

- **Smart Duration Classification**: Automatic routing based on trip length (≤3 days vs ≥5 days)
- **Parallel AI Processing**: Simultaneous generation of multiple travel options for short trips
- **Quality Validation Loops**: Iterative improvement through LLM-based content validation
- **Conditional Logic Flow**: Dynamic workflow branching based on user choices and preferences
- **Comprehensive Integration**: Seamless connection between user interface, AI processing, and final output generation

## 🧠 AI-Powered Workflow Engine

WanderFlow rappresenta una soluzione all'avanguardia che combina **Large Language Models (LLMs)** con **tecniche avanzate di prompt engineering** attraverso un sofisticato workflow Orkes Conductor. Il sistema integra modelli **Mistral AI** tramite OpenRouter API per fornire una pianificazione di viaggio intelligente e contestualmente consapevole, con meccanismi integrati di garanzia della qualità.

### 🤖 Integrazione LLM & Strategia di Prompt Engineering

Il workflow implementa **strategie di prompt engineering multi-livello** per garantire output di alta qualità:

#### **1. Design Sistematico dei Prompt**
- **Prompting Basato su Ruoli**: Ogni chiamata LLM definisce un ruolo specifico (pianificatore di viaggio, assistente per il controllo qualità)
- **Istruzioni Guidate da Vincoli**: Requisiti espliciti di formato di output e vincoli comportamentali
- **Preservazione del Contesto**: Le preferenze dell'utente e la durata del viaggio vengono mantenute costantemente attraverso il workflow
- **Prioritizzazione delle Preferenze**: Enfasi dedicata sulle preferenze specificate dall'utente durante tutta la generazione

#### **2. Selezione Intelligente delle Città**
**Implementazione della Strategia**:
- **Viaggi Brevi (≤3 giorni)**: Genera 3 città europee geograficamente distanti per la massima varietà
- **Viaggi Lunghi (≥5 giorni)**: Seleziona 3 città vicine nella stessa regione per un'esplorazione completa
- **Approccio Preferenze-First**: Tutte le selezioni di città si allineano rigorosamente con le preferenze specificate dall'utente

#### **3. Generazione Adattiva degli Itinerari**
Il sistema impiega **prompt engineering consapevole del contesto** che si adatta alle caratteristiche del viaggio con prompt specializzati per diverse durate di viaggio e preferenze dell'utente.

### 🔄 Garanzia di Qualità Tramite Validazione AI

TripMatch implementa un **meccanismo sofisticato di controllo qualità** utilizzando validazione basata su LLM:

#### **Loop di Qualità Iterativi (DO_WHILE)**
Ogni generazione di itinerario è avvolta in un loop `DO_WHILE` che continua fino al raggiungimento degli standard di qualità utilizzando una logica di validazione sofisticata. Questo approccio garantisce che ogni itinerario generato soddisfi criteri rigorosi prima di essere presentato all'utente.

#### **Validazione Attraverso Prompt Engineering**
Il sistema utilizza prompt specializzati per il controllo qualità che assicurano che ogni itinerario soddisfi gli standard di coerenza, allineamento alle preferenze e completezza. Questo processo di validazione multi-livello rappresenta un'innovazione chiave nell'applicazione dell'AI alla pianificazione di viaggio.

**Metriche di Qualità**:
- ✅ **Coerenza**: Flusso logico e struttura
- ✅ **Allineamento alle Preferenze Utente**: Aderenza rigorosa alle preferenze specificate
- ✅ **Appropriatezza della Durata**: Il contenuto corrisponde alla durata del viaggio specificata
- ✅ **Completezza**: Copertura comprensiva di attività e logistica

### 🔀 Orchestrazione Avanzata del Workflow

#### **Alberi Decisionali Dinamici**
Il workflow utilizza **logica condizionale basata su JavaScript** per il routing intelligente basato sulla durata del viaggio e le preferenze dell'utente. Questa architettura decisionale permette al sistema di adattarsi dinamicamente alle esigenze specifiche di ogni utente.

#### **Elaborazione Parallela con FORK_JOIN**
Per i viaggi brevi, il sistema genera tre itinerari **simultaneamente** utilizzando un'architettura di elaborazione parallela per prestazioni ottimali. Questa tecnica avanzata riduce significativamente i tempi di risposta mantenendo alta la qualità del contenuto.

#### **Gestione degli Errori & Resilienza**
- **Meccanismi di Retry**: Retry automatico con backoff esponenziale per le richieste LLM fallite
- **Degradazione Graduale**: Strategie di fallback per scenari non gestiti con notifica utente
- **Validazione Input**: Validazione pre-elaborazione per prevenire fallimenti del workflow
- **Gestione Timeout**: Timeout configurabili per prevenire loop infiniti con controllo qualità automatico

### 🎯 Funzionalità Avanzate AI

#### **Informazioni Aggiuntive Contestuali**
Il sistema fornisce **raccomandazioni di viaggio intelligenti** attraverso prompt specializzati che offrono consigli pratici e orientati alla sicurezza, personalizzati per destinazioni specifiche e esigenze dell'utente. Questa funzionalità rappresenta un valore aggiunto significativo per l'esperienza utente.

**Categorie di Informazioni**:
- 📋 **Requisiti Documentali**: Visti, passaporti, permessi
- 💉 **Salute & Sicurezza**: Vaccinazioni, raccomandazioni mediche
- 🌤️ **Insights Meteorologici**: Considerazioni stagionali e consigli per il bagaglio
- 🍽️ **Raccomandazioni Culinarie**: Ristorazione locale ed esperienze gastronomiche
- 🎨 **Attrazioni Culturali**: Siti imperdibili ed esperienze autentiche
- 📅 **Prenotazioni Anticipate**: Prenotazioni e accordi sensibili al tempo

#### **Configurazione del Modello AI**
- **Modello Primario**: `mistralai/mistral-7b-instruct` via OpenRouter per performance ottimali
- **Integrazione API**: Chiamate HTTP RESTful con autenticazione appropriata e gestione errori
- **Parsing delle Risposte**: Estrazione JSON strutturata e validazione automatica
- **Filtraggio dei Contenuti**: Controlli integrati di sicurezza e appropriatezza del contenuto

### 📊 Metriche del Workflow & Monitoraggio

Il sistema traccia metriche comprensive per il miglioramento continuo:
- **Tasso di Successo Generazione**: Percentuale di generazioni di itinerario riuscite (>95%)
- **Tasso di Superamento Qualità**: Metriche di successo della validazione (>90%)
- **Tempo di Risposta**: Tempi medi di risposta LLM (<30 secondi)
- **Soddisfazione Utente**: Feedback implicito attraverso le scelte dell'utente
- **Allineamento Preferenze**: Accuratezza del matching delle preferenze (>90%)

Questa architettura alimentata dall'AI garantisce che ogni itinerario generato non sia solo personalizzato, ma anche di alta qualità, coerente e perfettamente allineato con le aspettative dell'utente, mantenendo l'affidabilità e le prestazioni del sistema.

## 🔧 AI Technical Specifications

### **LLM Model Configuration**
- **Primary Model**: `mistralai/mistral-7b-instruct` via OpenRouter API
- **Backup Models**: Configurable fallback models for enhanced reliability
- **Context Window**: 8,192 tokens per request for comprehensive travel planning
- **Temperature**: 0.7 for balanced creativity and consistency in travel recommendations
- **Max Tokens**: 1,500-2,000 per response depending on itinerary complexity

### **AI Quality Metrics**
- **Generation Success Rate**: >95% successful itinerary generations
- **Quality Validation Pass Rate**: >90% first-pass validation success
- **Average Response Time**: <30 seconds for complex multi-city itineraries
- **User Preference Alignment**: >90% accuracy in preference matching
- **Content Coherence Score**: Validated through automated LLM assessment

### **Prompt Engineering Standards**
- **Role-Based Prompting**: Systematic role assignment for consistent AI behavior
- **Constraint-Driven Instructions**: Explicit format and content requirements
- **Context Preservation**: User preferences maintained across all AI interactions
- **Multi-Layer Validation**: Iterative quality checks with DO_WHILE loops
- **Preference Prioritization**: Dedicated emphasis on user-specified preferences

### **AI Workflow Resilience**
- **Retry Mechanisms**: Exponential backoff for failed LLM requests
- **Fallback Strategies**: Alternative prompts for edge cases
- **Error Recovery**: Graceful degradation with user notification
- **Timeout Management**: Configurable timeouts to prevent infinite loops
- **Quality Assurance**: Automated content validation before user presentation

## 🚀 Setup & AI-Powered Usage

### 1. **Clone and Install AI Dependencies**
```bash
git clone https://github.com/your-username/WanderFlow.git
cd WanderFlow

# Create virtual environment for AI packages
python -m venv BPA_TripMatch
source BPA_TripMatch/bin/activate  # On macOS/Linux
# or
BPA_TripMatch\Scripts\activate  # On Windows

# Install dependencies including AI/ML libraries
pip install -r requirements.txt
```

### 2. **Configure AI & Workflow Environment Variables**
Create a `credentials.env` file in the root directory:
```env
# Orkes Conductor API Configuration (for AI workflow orchestration)
CONDUCTOR_AUTH_KEY=your_orkes_auth_key
CONDUCTOR_AUTH_SECRET=your_orkes_auth_secret
CONDUCTOR_SERVER_URL=https://developer.orkescloud.com/api

# OpenRouter API Configuration (for LLM/AI content generation)
OPENROUTER_API_KEY=your_openrouter_api_key
```

To import the workflow, access the Orkes Cloud Console, navigate to the Workflows section, click on Create Workflow → Import JSON, and upload the WanderFlow.json file. For HTTP tasks using OpenRouter, make sure to include the X-OpenRouter-API-Key header with your API token.

### 3. **Deploy AI-Powered Workflow to Orkes Conductor**
Ensure your TripMatch_BPA workflow (version 26) is deployed and active in your Orkes Conductor instance with all AI-integrated tasks:
- `UserPreferences` - Collects and processes user input for AI preference analysis
- `TripDecision` - JavaScript-based intelligent routing with AI-driven duration analysis
- `Prompt3CitiesFar` - LLM-powered distant city generation for short trips using advanced prompting
- `Prompt3CitiesNear` - LLM-powered regional city selection for long trips with geographic AI
- `ItineraryCity1/2/3` - Parallel AI itinerary generation with iterative quality validation loops
- `ChoiceTravelCity` - User selection interface for AI-generated travel options
- `ShowItinerary` - Single comprehensive AI-generated itinerary with quality assurance
- `AskforAddInfo_ref` - Conditional additional information request with AI context
- `TravelRecommendation` - AI-powered practical travel advice generation using specialized prompts
- `ShowMoreInformation` - Enhanced information display with AI insights and recommendations

### 4. **Launch the AI-Powered Application**
```bash
# Activate virtual environment
source venv_folder/bin/activate

# Start Streamlit application with AI backend
streamlit run app.py
```

The AI-powered application will be available at `http://localhost:8501`

### 5. **Using the AI-Driven Travel Planning System**

1. **Welcome Screen**: Click "Start Planning Your Trip" to begin the AI-driven planning process
2. **Intelligent Preferences Collection with AI Analysis**: 
   - Select trip duration (1-10+ days) for AI routing decision and workflow optimization
   - Choose travel period for seasonal AI recommendations and weather-aware planning
   - Select destination types (nature, cities, beach, mountains) for AI preference analysis and matching
   - Pick a country from the interactive map for geographic AI context and regional optimization
   - Choose vacation styles (relaxation, adventure, culture, etc.) for AI personality profiling and customization
3. **AI-Powered Trip Planning Engine**:
   - **Short trips (≤3 days)**: Choose from three AI-curated city options generated via parallel LLM processing
   - **Long trips (≥5 days)**: Review the comprehensive AI-generated regional itinerary with quality validation
4. **AI Acceptance & Smart Customization**: Accept your AI-generated itinerary and optionally request additional AI-powered travel information
5. **Enhanced Export**: Download your personalized travel plan as a professional PDF with AI-enhanced content formatting

## 🎨 AI-Enhanced User Interface Features

### Smart Interactive Map Integration
- **AI-Guided Country Selection**: Intelligent visual country picker with geographic highlighting and contextual recommendations
- **Dynamic AI-Driven Zoom**: Automatic map centering based on AI-selected destinations and user preference patterns
- **Real-time AI Updates**: Instant map updates reflecting AI-processed user choices and workflow decisions
- **Geographic AI Context**: Comprehensive country boundary and feature data for enhanced AI geographic understanding

### Responsive Design Optimized for AI Content
- **Multi-device AI Content Support**: Optimized display for desktop, tablet, and mobile viewing of LLM-generated itineraries
- **Progressive AI Enhancement**: Graceful degradation for slower connections while maintaining full AI functionality
- **AI-Accessible Design**: WCAG-compliant design with keyboard navigation support for AI-powered interfaces
- **AI Performance Optimization**: Optimized loading times and smooth interactions during LLM content generation

### Modern UI Components with Integrated AI Features
- **AI Progress Indicators**: Visual progress tracking throughout the intelligent planning process with real-time workflow status
- **AI-Optimized Styling**: Consistent branding and professional appearance specifically designed for AI-generated content display
- **Smart Interactive Forms**: Real-time validation and user feedback systems optimized for AI input processing and preference analysis
- **AI-Aware Animations**: Smooth transitions and micro-interactions during AI content generation and quality validation processes

## Development & AI Customization

### Adding New Countries with AI Integration
Update the application configuration to include geographic context for AI processing by modifying the countries data structure with regional information, coordinates, and zoom levels.

### AI Workflow Customization
Modify AI workflow logic in the workflow manager to implement custom task waiting logic with LLM integration and add AI quality validation for enhanced performance.

### UI Customization for AI Content
Extend AI-optimized UI components to add new interfaces optimized for AI-generated content and implement custom formatting for LLM-generated travel itineraries.

### LLM Prompt Engineering Customization
Customize AI prompts in workflow definitions to create specialized travel AI assistants with custom instructions tailored to specific use cases or regional preferences.

## Testing & AI Debugging

### AI Debug Mode
Enable comprehensive debug information including AI workflow analysis by configuring the session state to include both general debugging and AI-specific monitoring capabilities.

### AI Workflow Debugging
Use built-in AI debugging utilities to check AI workflow status and LLM task performance, analyze workflow routing and decision logic, monitor response quality and validation results, and debug prompt engineering effectiveness.

### AI Performance Monitoring
Track AI-specific metrics for optimization including LLM response times and success rates, quality validation patterns, and user satisfaction with AI-generated content to continuously improve the system performance.

## Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork the repository** and create a feature branch
2. **Follow coding standards** with proper documentation
3. **Add tests** for new functionality
4. **Update documentation** as needed
5. **Submit a pull request** with a clear description

## Authors

* [Leonardo Catello](https://github.com/Leonard2310)
* [Aurora D'Ambrosio](https://github.com/AuroraD-99)
* [Luisa Ciniglio](https://github.com/LuisaCiniglio)

## License

This project is licensed under the [GPL-3.0 license](LICENSE). For full terms, see the LICENSE file. 
