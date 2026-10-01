
from pathlib import Path
import pandas as pd

def load_foods():
    path = Path(__file__).resolve().parents[1] / "data" / "foods.csv"
    if not path.exists():
        raise FileNotFoundError("Food database was not found.")
    df = pd.read_csv(path)
    for col in ["Calories", "Protein", "Carbohydrates", "Fat", "Fiber"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.dropna(subset=["Food Name", "Calories", "Protein"]).copy()
