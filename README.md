# Healthcare AI - Model Training

A minimal Machine Learning project focused on training a disease prediction model using a Random Forest Classifier.

## 📂 Project Structure

```
Healthcare_AI/
│
├── data/
│     └── Testing.csv
│
├── trained_model.pkl
│
├── Healthcare_Model_Training.ipynb
│
├── README.md
│
└── requirements.txt
```
*(Note: Other legacy directories like `backend/`, `models/`, and `utils/` may exist in the repository but are not part of the active ML workflow).*

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the Jupyter Notebook
```bash
jupyter notebook Healthcare_Model_Training.ipynb
```

## 🧠 Model Training Details
The notebook covers the entire workflow for training the Disease Predictor:
1. Data loading and understanding.
2. Missing value analysis and preprocessing.
3. Feature encoding (Label Encoding).
4. Train/Test split.
5. Training the **Random Forest Classifier**.
6. Model evaluation (Accuracy, Precision, Recall, F1 Score, Confusion Matrix, Classification Report).
7. Feature Importance analysis.
8. Model persistence (saving to `.pkl` via `joblib`).