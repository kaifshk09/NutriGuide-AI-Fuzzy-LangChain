
"""Explainable food recommendation engine integrating fuzzy inference."""
import pandas as pd
from .fuzzy_engine import infer_fuzzy_needs, fuzzy_explanation

ALLERGY_COLUMNS = {
    "Milk/Dairy": ["Milk", "Curd", "Yogurt", "Greek Yogurt", "Paneer", "Paneer Bhurji", "Palak Paneer", "Lassi"],
    "Gluten": ["Oats", "Vegetable Sandwich", "Roti", "Vegetable Paratha", "Bajra Roti", "Jowar Roti"],
    "Nuts": ["Peanuts", "Almonds", "Hummus"],
    "Eggs": ["Eggs", "Boiled Eggs", "Vegetable Sandwich"],
    "Soy": ["Soy Milk", "Tofu", "Soya Chunks"],
}
MEAL_MAP = {
    "Breakfast": "Breakfast",
    "Mid-morning Snack": "Snack",
    "Lunch": "Lunch",
    "Evening Snack": "Snack",
    "Dinner": "Dinner",
}

def apply_diet_filter(df, preference):
    col = {"Vegetarian":"Vegetarian","Vegan":"Vegan","Eggetarian":"Eggetarian","Non-Vegetarian":"Non-Veg"}[preference]
    return df[df[col].astype(str).str.lower().eq("yes")].copy()

def apply_allergy_filter(df, allergy):
    if allergy == "None":
        return df.copy()
    banned = set(ALLERGY_COLUMNS.get(allergy, []))
    return df[~df["Food Name"].isin(banned)].copy()

def score_food(row, goal, cuisine, budget, meal, calorie_budget, fuzzy):
    score = 0.0
    reasons = []
    meal_col = MEAL_MAP[meal]

    if str(row[meal_col]).lower() == "yes":
        score += 3; reasons.append("matches the selected meal")
    if row["Cuisine"] in (cuisine, "Mixed"):
        score += 2; reasons.append("matches your cuisine preference")
    if row["Budget"] == budget:
        score += 2; reasons.append("fits your budget")
    if row["Protein"] >= 10:
        score += 2; reasons.append("provides useful protein")

    # Fuzzy inference contributes to recommendation ranking.
    protein_bonus = min(5.0, fuzzy["protein_need"] / 20.0) if row["Protein"] >= 12 else 0
    energy_bonus = min(4.0, fuzzy["energy_need"] / 25.0) if row["Calories"] >= 150 else 0
    weight_bonus = min(4.0, fuzzy["weight_loss_need"] / 25.0) if row["Calories"] <= calorie_budget else 0
    score += protein_bonus + energy_bonus + weight_bonus

    if goal == "Weight Loss" and row["Calories"] <= calorie_budget:
        score += 3; reasons.append("fits a lower-calorie goal")
    elif goal in ("Muscle Building", "Weight Gain") and row["Protein"] >= 12:
        score += 3; reasons.append("supports a higher-protein goal")
    elif goal == "Healthy Eating" and row["Fiber"] >= 4:
        score += 3; reasons.append("provides fiber")

    return score, reasons

def generate_plan(df, profile, tdee, calorie_target_value):
    fuzzy = infer_fuzzy_needs(
        profile["BMI"], profile["Activity"],
        calorie_target_value - tdee, profile["Fitness Goal"]
    )
    meals = ["Breakfast","Mid-morning Snack","Lunch","Evening Snack","Dinner"]
    plan, used = {}, set()
    per_meal = calorie_target_value / len(meals)

    for meal in meals:
        filtered = apply_allergy_filter(apply_diet_filter(df, profile["Dietary Preference"]), profile["Allergy"])
        filtered = filtered[~filtered["Food Name"].isin(used)].copy()
        scored = []
        for _, row in filtered.iterrows():
            score, reasons = score_food(row, profile["Fitness Goal"], profile["Cuisine"], profile["Budget"], meal, per_meal, fuzzy)
            scored.append((score, row, reasons))
        scored.sort(key=lambda x: (x[0], x[1]["Protein"], -x[1]["Calories"]), reverse=True)
        if scored:
            best = scored[0]
            used.add(best[1]["Food Name"])
            plan[meal] = {"row":best[1], "score":round(best[0],1), "reasons":best[2]}
    return plan, fuzzy, fuzzy_explanation(fuzzy)
