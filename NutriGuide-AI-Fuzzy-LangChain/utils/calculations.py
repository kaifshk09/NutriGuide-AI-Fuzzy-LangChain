
"""Deterministic nutrition calculations used by the AI recommendation system."""

ACTIVITY_MULTIPLIERS = {
    "Sedentary": 1.2,
    "Lightly Active": 1.375,
    "Moderately Active": 1.55,
    "Very Active": 1.725,
}

def calculate_bmi(weight_kg, height_cm):
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obesity"
    return round(bmi, 1), category

def calculate_bmr(weight_kg, height_cm, age, gender):
    base = 10 * weight_kg + 6.25 * height_cm - 5 * age
    return base + 5 if gender == "Male" else base - 161

def calculate_tdee(bmr, activity_level):
    return bmr * ACTIVITY_MULTIPLIERS[activity_level]

def calorie_target(tdee, goal):
    if goal == "Weight Loss":
        return max(1200, tdee - 400)
    if goal == "Weight Gain":
        return tdee + 350
    if goal == "Muscle Building":
        return tdee + 300
    return tdee

def protein_target(weight_kg, goal):
    multipliers = {
        "Weight Loss": 1.6,
        "Weight Maintenance": 1.2,
        "Weight Gain": 1.4,
        "Muscle Building": 1.6,
        "Healthy Eating": 1.2,
    }
    return round(weight_kg * multipliers.get(goal, 1.2), 0)
