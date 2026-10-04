import pandas as pd
import numpy as np
import os

def generate_synthetic_data(num_samples=2000):
    np.random.seed(42)
    
    print("Generating synthetic data for AquaSync AI...")
    
    # Base features
    temperatures = np.random.uniform(20, 45, num_samples) # Celsius
    humidity = np.random.uniform(20, 90, num_samples) # Percentage
    rainfall_forecast = np.random.uniform(0, 50, num_samples) # mm in next 24h
    soil_moisture = np.random.uniform(10, 60, num_samples) # Percentage
    
    # Categorical features
    crop_types = np.random.choice(['Wheat', 'Rice', 'Cotton', 'Maize', 'Sugarcane'], num_samples)
    soil_types = np.random.choice(['Clay', 'Sandy', 'Loamy'], num_samples)
    crop_stages = np.random.choice(['Seedling', 'Vegetative', 'Flowering', 'Maturity'], num_samples)
    
    # Base water requirement factors (mock multipliers)
    crop_factor = {'Wheat': 1.0, 'Rice': 1.8, 'Cotton': 1.2, 'Maize': 1.1, 'Sugarcane': 1.5}
    soil_factor = {'Clay': 0.8, 'Sandy': 1.3, 'Loamy': 1.0}
    stage_factor = {'Seedling': 0.6, 'Vegetative': 1.0, 'Flowering': 1.3, 'Maturity': 0.7}
    
    # Target Variable Generation: Required Irrigation (mm/day)
    # Equation = (Base Evapotranspiration + Temp effect - Moisture effect - Rain forecast effect) * Factors
    base_et = (temperatures * 0.4) + (100 - humidity) * 0.1
    
    irrigation_needed = []
    water_stress_risk = []
    
    for i in range(num_samples):
        cf = crop_factor[crop_types[i]]
        sf = soil_factor[soil_types[i]]
        stf = stage_factor[crop_stages[i]]
        
        # Calculate raw requirement
        req = (base_et[i] * cf * stf * sf) - (soil_moisture[i] * 0.1) - (rainfall_forecast[i] * 0.5)
        
        # Add some noise
        req += np.random.normal(0, 2)
        
        # Cannot be negative
        req = max(0, req)
        
        irrigation_needed.append(round(req, 2))
        
        # Determine Stress Risk
        if soil_moisture[i] < 20 and temperatures[i] > 35:
            stress = "High"
        elif soil_moisture[i] < 30 or (temperatures[i] > 30 and rainfall_forecast[i] < 5):
            stress = "Medium"
        else:
            stress = "Low"
            
        water_stress_risk.append(stress)
        
    df = pd.DataFrame({
        'temperature_c': temperatures,
        'humidity_percent': humidity,
        'rainfall_forecast_mm': rainfall_forecast,
        'soil_moisture_percent': soil_moisture,
        'crop_type': crop_types,
        'soil_type': soil_types,
        'crop_stage': crop_stages,
        'irrigation_required_mm': irrigation_needed,
        'water_stress_risk': water_stress_risk
    })
    
    # Save to CSV
    output_path = os.path.join(os.path.dirname(__file__), 'crop_water_data.csv')
    df.to_csv(output_path, index=False)
    print(f"Dataset generated successfully at: {output_path}")
    print(f"Shape: {df.shape}")

if __name__ == "__main__":
    generate_synthetic_data()
