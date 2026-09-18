import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

df = pd.read_csv("ml_training/data/instagram_fake_accounts.csv")

feature_columns = [
    "profile pic", "nums/length username", "fullname words",
    "nums/length fullname", "name==username", "description length",
    "external URL", "private", "#posts", "#followers", "#follows"
]

X = df[feature_columns]
y = df["fake"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

os.makedirs("backend/ml_models", exist_ok=True)
joblib.dump(model, "backend/ml_models/fake_profile_model.pkl")
print("Model saved to backend/ml_models/fake_profile_model.pkl")