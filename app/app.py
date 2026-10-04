import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go
import os

st.set_page_config(page_title="AquaSync AI", page_icon="💧", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .main { background-color: #f4f9f4; }
    .stMetric { background-color: #ffffff; border-radius: 10px; padding: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .card { background-color: #ffffff; border-radius: 10px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px;}
    .title-text { color: #1e3d59; font-weight: 700; }
    .sub-text { color: #43655a; }
    .highlight-green { color: #2ecc71; font-weight: bold; }
    .highlight-red { color: #e74c3c; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- LOAD MODELS ---
@st.cache_resource
def load_models():
    base_path = os.path.dirname(__file__)
    model_path = os.path.join(base_path, '../models/irrigation_model.pkl')
    try:
        if not os.path.exists(model_path):
            import sys
            sys.path.append(os.path.abspath(os.path.join(base_path, '..')))
            from data.generate_data import generate_synthetic_data
            from models.train_model import train_models
            generate_synthetic_data()
            train_models()

        reg_model = joblib.load(os.path.join(base_path, '../models/irrigation_model.pkl'))
        clf_model = joblib.load(os.path.join(base_path, '../models/stress_model.pkl'))
        encoders = joblib.load(os.path.join(base_path, '../models/label_encoders.pkl'))
        return reg_model, clf_model, encoders
    except Exception as e:
        st.error(f"Error loading models. Details: {e}")
        return None, None, None

reg_model, clf_model, encoders = load_models()

# --- SIDEBAR NAVIGATION ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3037/3037142.png", width=60)
st.sidebar.title("AquaSync AI")
st.sidebar.markdown("*Precision Climate Intelligence*")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigation", ["Dashboard", "Farm Analysis", "Climate Intelligence", "Impact Simulator"])

# --- HELPER FUNCTIONS ---
def get_prediction(temp, humidity, rain, moisture, crop, soil, stage):
    if reg_model is None: return 0, "Unknown"
    
    # Encode inputs
    crop_enc = encoders['crop_type'].transform([crop])[0]
    soil_enc = encoders['soil_type'].transform([soil])[0]
    stage_enc = encoders['crop_stage'].transform([stage])[0]
    
    input_data = pd.DataFrame([[temp, humidity, rain, moisture, crop_enc, soil_enc, stage_enc]],
                              columns=['temperature_c', 'humidity_percent', 'rainfall_forecast_mm', 
                                       'soil_moisture_percent', 'crop_type', 'soil_type', 'crop_stage'])
    
    irrigation_req = reg_model.predict(input_data)[0]
    stress_enc = clf_model.predict(input_data)[0]
    stress_risk = encoders['water_stress_risk'].inverse_transform([stress_enc])[0]
    
    return irrigation_req, stress_risk

# --- PAGES ---
if page == "Dashboard":
    st.markdown("<h1 class='title-text'>🌍 AquaSync AI - Global Overview</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-text'>AI-powered water optimization for climate-smart agriculture.</p>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Active Farms (Simulated)", "1,245", "+12 this week")
    col2.metric("Water Saved (Liters)", "45.2 M", "+1.2 M today")
    col3.metric("CO2 Emission Prevented", "12.4 Tons", "Reduced Pumping")
    col4.metric("Avg Regional Stress", "Medium", "Monsoon expected")

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 📊 Water Conservation Trend")
    # Dummy chart
    dates = pd.date_range(start='2023-01-01', periods=30)
    savings = np.cumsum(np.random.normal(500, 100, 30))
    fig = go.Figure(data=go.Scatter(x=dates, y=savings, line=dict(color='#2ecc71', width=3)))
    fig.update_layout(height=300, margin=dict(l=0, r=0, t=30, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

elif page == "Farm Analysis":
    st.markdown("<h1 class='title-text'>🌾 Farm-Level Analysis & AI Recommendations</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### Input Farm Data")
        crop = st.selectbox("Crop Type", ["Wheat", "Rice", "Cotton", "Maize", "Sugarcane"])
        stage = st.selectbox("Crop Stage", ["Seedling", "Vegetative", "Flowering", "Maturity"])
        soil = st.selectbox("Soil Type", ["Clay", "Sandy", "Loamy"])
        area = st.number_input("Farm Area (Hectares)", min_value=0.1, value=5.0)
        
        st.markdown("### Sensor / Weather Data")
        temp = st.slider("Temperature (°C)", 10, 50, 32)
        humidity = st.slider("Humidity (%)", 10, 100, 45)
        moisture = st.slider("Soil Moisture (%)", 0, 100, 25)
        rain = st.slider("Forecasted Rainfall (mm)", 0, 100, 0)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 🤖 AI Prediction Results")
        if st.button("Generate Recommendation", type="primary"):
            with st.spinner("AI analyzing climate and soil data..."):
                irrig_req, stress = get_prediction(temp, humidity, rain, moisture, crop, soil, stage)
                
                total_water_liters = (irrig_req * 10) * area * 1000 # Rough conversion mm to liters per hectare
                traditional_water = (irrig_req * 1.4 * 10) * area * 1000 # Assume 40% waste in traditional
                saved_water = traditional_water - total_water_liters
                
                c1, c2 = st.columns(2)
                c1.metric("Required Irrigation (mm/day)", f"{irrig_req:.2f} mm")
                
                stress_color = "red" if stress == "High" else "orange" if stress == "Medium" else "green"
                c2.metric("Crop Water Stress Risk", stress, delta_color="inverse")
                
                st.markdown("---")
                st.markdown("#### 💡 Explainable AI Recommendation")
                
                if rain > 10:
                    st.info(f"🌧️ **Recommendation:** Postpone irrigation. {rain}mm of rainfall is expected, which fulfills the crop requirement.")
                elif moisture > 40:
                    st.success(f"🌱 **Recommendation:** Do not irrigate today. Soil moisture is sufficient for {crop} at {stage} stage.")
                else:
                    st.warning(f"💧 **Recommendation:** Irrigate {irrig_req:.1f} mm. Apply precision irrigation to avoid deep percolation. High temperature ({temp}°C) is increasing evapotranspiration.")
                
                st.markdown("#### 🌍 Estimated Environmental Impact (Today)")
                col_a, col_b = st.columns(2)
                col_a.metric("Water Saved (vs Traditional)", f"{saved_water:,.0f} L")
                col_b.metric("Energy Saved (Pumping)", f"{(saved_water/1000)*0.8:,.1f} kWh")
        else:
            st.info("👈 Enter farm parameters and click 'Generate Recommendation'.")
        st.markdown("</div>", unsafe_allow_html=True)

elif page == "Climate Intelligence":
    st.markdown("<h1 class='title-text'>🌤️ Climate Intelligence</h1>", unsafe_allow_html=True)
    st.markdown("Visualizing synthetic climate trends and anomaly detection for predictive resilience.")
    st.image("https://images.unsplash.com/photo-1592658804680-779836173007?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80", use_column_width=True)

elif page == "Impact Simulator":
    st.markdown("<h1 class='title-text'>📈 Scalability & Impact Simulator</h1>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("Simulate the impact of AquaSync AI across regions.")
    
    farms = st.slider("Number of Farms Adopted", 10, 100000, 1000)
    avg_hectares = st.slider("Avg Hectares per Farm", 1, 50, 5)
    
    annual_water_saved = farms * avg_hectares * 150000 # Liters saved per hectare annually (assumption)
    annual_co2_saved = (annual_water_saved / 1000) * 0.8 * 0.5 # kWh * kgCO2/kWh
    
    st.markdown(f"### 💧 Projected Annual Water Savings: **{annual_water_saved / 1e9:.2f} Billion Liters**")
    st.markdown(f"### 🌬️ Projected Annual CO2 Reduction: **{annual_co2_saved / 1000:.2f} Metric Tons**")
    st.markdown("</div>", unsafe_allow_html=True)
