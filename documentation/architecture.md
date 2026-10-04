# System Architecture

The AquaSync AI platform is designed to be lightweight, scalable, and farmer-friendly.

```mermaid
graph TD
    %% Data Sources Layer
    subgraph Layer 1: Data Sources
        W[Weather API / Forecast]
        S[Soil Moisture Sensors / Manual Input]
        F[Farmer Inputs: Crop, Stage, Area]
    end

    %% Processing Layer
    subgraph Layer 2: Data Processing & ML
        DP[Data Preprocessing]
        ML1[Random Forest: Water Requirement Predictor]
        ML2[Random Forest: Water Stress Classifier]
    end

    %% Recommendation Layer
    subgraph Layer 3: Recommendation Engine
        RE[Explainable AI Engine]
        DB[(Impact Database)]
    end

    %% Presentation Layer
    subgraph Layer 4: User Interface
        UI[Streamlit Web Dashboard / Mobile App]
    end

    %% Flow
    W --> DP
    S --> DP
    F --> DP
    DP --> ML1
    DP --> ML2
    ML1 --> RE
    ML2 --> RE
    RE --> UI
    RE --> DB
    UI --> |Farmer Action| DB
```

## Layer Explanations
1. **Data Sources:** Accepts synthetic local climate data (temperature, humidity, rain forecast) and farm specs.
2. **ML Engine:** Uses Scikit-learn (Random Forest) to predict the exact `mm` of water required today and classifies the risk of drought stress.
3. **Recommendation Engine:** Translates raw ML outputs into plain-text advice (e.g., "Postpone irrigation, 15mm rain expected tomorrow").
4. **Dashboard:** A clean, metric-driven interface showing immediate ROI and environmental impact.
