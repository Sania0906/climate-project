import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score, accuracy_score
import joblib
import os

def train_models():
    data_path = os.path.join(os.path.dirname(__file__), '../data/crop_water_data.csv')
    if not os.path.exists(data_path):
        print("Data not found. Run generate_data.py first.")
        return
        
    print("Loading dataset...")
    df = pd.read_csv(data_path)
    
    # Encode categorical variables
    le_dict = {}
    cat_cols = ['crop_type', 'soil_type', 'crop_stage']
    
    df_encoded = df.copy()
    for col in cat_cols:
        le = LabelEncoder()
        df_encoded[col] = le.fit_transform(df_encoded[col])
        le_dict[col] = le
        
    # Features and Targets
    X = df_encoded[['temperature_c', 'humidity_percent', 'rainfall_forecast_mm', 
                    'soil_moisture_percent', 'crop_type', 'soil_type', 'crop_stage']]
                    
    y_reg = df_encoded['irrigation_required_mm']
    
    le_stress = LabelEncoder()
    y_clf = le_stress.fit_transform(df_encoded['water_stress_risk'])
    le_dict['water_stress_risk'] = le_stress
    
    # Split Data
    X_train, X_test, y_reg_train, y_reg_test, y_clf_train, y_clf_test = train_test_split(
        X, y_reg, y_clf, test_size=0.2, random_state=42
    )
    
    # Train Regression Model (predict water quantity)
    print("Training Irrigation Prediction Model (Random Forest)...")
    reg_model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
    reg_model.fit(X_train, y_reg_train)
    
    reg_preds = reg_model.predict(X_test)
    mae = mean_absolute_error(y_reg_test, reg_preds)
    r2 = r2_score(y_reg_test, reg_preds)
    print(f"Regression MAE: {mae:.2f} mm")
    print(f"Regression R2: {r2:.2f}")
    
    # Train Classification Model (predict stress risk)
    print("Training Water Stress Risk Model (Random Forest)...")
    clf_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    clf_model.fit(X_train, y_clf_train)
    
    clf_preds = clf_model.predict(X_test)
    acc = accuracy_score(y_clf_test, clf_preds)
    print(f"Classification Accuracy: {acc:.2f}")
    
    # Save models and encoders
    models_dir = os.path.dirname(__file__)
    joblib.dump(reg_model, os.path.join(models_dir, 'irrigation_model.pkl'))
    joblib.dump(clf_model, os.path.join(models_dir, 'stress_model.pkl'))
    joblib.dump(le_dict, os.path.join(models_dir, 'label_encoders.pkl'))
    
    print("Models saved successfully in the 'models' directory.")

if __name__ == "__main__":
    train_models()
