# backend/logic.py
# ---------------------------------------------------------
# Core ML logic module. Maps user symptoms to disease predictions
# and retrieves treatment recommendations from datasets.
# ---------------------------------------------------------

import pandas as pd
import numpy as np
import joblib
from pathlib import Path

# Resolve path to locate datasets and the trained model relative to this file
ROOT_DIR = Path(__file__).resolve().parent.parent

# --- 1. Load Medical Datasets ---
try:
    # Load prescription and routine recommendations
    med_df = pd.read_csv(ROOT_DIR / 'data' / 'medical data.csv')
    routine_df = pd.read_csv(ROOT_DIR / 'data' / 'disease_diet_workout_dataset.csv')
except Exception as e:
    print(f"Error loading datasets: {e}")
    med_df = None
    routine_df = None

# --- 2. Load the Pre-trained ML Model ---
try:
    # Load trained MultinomialNB model, label encoder, and feature list
    model_data = joblib.load(ROOT_DIR / 'trained_model.pkl')
    model = model_data['model']               
    le = model_data['label_encoder']          
    features_list = model_data['features']    
except Exception as e:
    print(f"Error loading model: {e}")
    model = None
    le = None
    features_list = []

# --- 3. Frontend Symptom Schema ---
# Curated list of 132 symptoms for the UI dropdown
valid_symptoms = ["acidity", "indigestion", "blurred_and_distorted_vision", "high_fever", "irritability", "malaise", "bruising", "skin_rash", "abnormal_menstruation", "blood_in_sputum", "ulcers_on_tongue", "small_dents_in_nails", "cramps", "mood_swings", "prominent_veins_on_calf", "depression", "yellowing_of_eyes", "weight_gain", "loss_of_appetite", "vomiting", "family_history", "scurring", "hip_joint_pain", "blackheads", "cough", "mild_fever", "movement_stiffness", "joint_pain", "silver_like_dusting", "increased_appetite", "dizziness", "chest_pain", "weight_loss", "restlessness", "passage_of_gases", "breathlessness", "obesity", "stomach_pain", "swollen_extremeties", "diarrhoea", "phlegm", "brittle_nails", "visual_disturbances", "sweating", "rusty_sputum", "fatigue", "loss_of_balance", "painful_walking", "enlarged_thyroid", "chills", "cold_hands_and_feets", "lethargy", "stiff_neck", "puffy_face_and_eyes", "internal_itching", "swelled_lymph_nodes", "skin_peeling", "lack_of_concentration", "irregular_sugar_level", "polyuria", "inflammatory_nails", "mucoid_sputum", "neck_pain", "muscle_weakness", "swollen_blood_vessels", "swollen_legs", "abdominal_pain", "headache", "knee_pain", "excessive_hunger", "swelling_joints", "pus_filled_pimples", "fast_heart_rate"]

# Resolves naming inconsistencies between ML output and CSV datasets
DISEASE_MAPPING = {"GERD": "GERD (Acid Reflux)", "Peptic ulcer diseae": "Peptic Ulcer", "Diabetes ": "Type 2 Diabetes", "Bronchial Asthma": "Asthma", "Hypertension ": "Hypertension", "Migraine": "Migraine", "Tuberculosis": "Tuberculosis (Recovery Phase)", "Pneumonia": "Bronchial Pneumonia (Recovery)", "Heart attack": "Coronary Artery Disease", "Varicose veins": "Varicose Veins", "Hypothyroidism": "Hypothyroidism", "Hyperthyroidism": "Hyperthyroidism", "Osteoarthristis": "Osteoarthritis", "Arthritis": "Rheumatoid Arthritis", "Acne": "Acne", "Psoriasis": "Psoriasis"}

# --- 4. Prediction Logic ---
def predict_disease_and_recommend(symptoms_input):
    if model is None:
        return {"error": "Model not loaded."}

    # Step A: One-Hot Encode symptoms into a binary array
    input_vector = np.zeros(len(features_list))
    for symptom in symptoms_input:
        if symptom in features_list:
            idx = features_list.index(symptom)
            input_vector[idx] = 1 
            
    # Step B: Run prediction via MultinomialNB Model
    # Wrap in DataFrame to prevent sklearn feature-name warnings
    input_df = pd.DataFrame([input_vector], columns=features_list)
    pred_encoded = model.predict(input_df)[0]
    
    # Step C: Decode class index to string and apply mapping
    predicted_disease = le.inverse_transform([pred_encoded])[0] 
    mapped_disease = DISEASE_MAPPING.get(predicted_disease, predicted_disease)
    
    # Step D: Look up medication using partial string matching
    medicines = "Consult a doctor for appropriate medication."
    if med_df is not None:
        match = med_df[med_df['Disease'].astype(str).str.contains(mapped_disease, case=False, na=False)]
        if not match.empty:
            medicines = match.iloc[0]['Medicine']
            
    # Step E: Look up diet & workout using exact case-insensitive match
    diet = "Maintain a balanced diet and stay hydrated."
    workout = "Engage in light physical activity as tolerated."
    if routine_df is not None:
        match_routine = routine_df[routine_df['Disease'].str.lower() == mapped_disease.lower()]
        if not match_routine.empty:
            diet = match_routine.iloc[0]['Diet_Recommendation']
            workout = match_routine.iloc[0]['Workout_Recommendation']
            
    return {
        "predicted_disease": mapped_disease,
        "medicines": medicines,
        "diet": diet,
        "workout": workout
    }
