
"""Genuine fuzzy inference engine for NutriGuide AI.

This module intentionally implements the fuzzy mathematics directly instead of
pretending a normal if/else score is fuzzy logic.

Inputs:
- BMI
- Activity intensity (mapped from activity level)
- Calorie surplus/deficit relative to TDEE
- Fitness goal

Outputs:
- Weight-loss need
- Protein need
- Energy need

The system uses triangular/trapezoidal membership functions, min for AND,
max for rule aggregation, and centroid defuzzification.
"""

import numpy as np

def trapmf(x, a, b, c, d):
    x = np.asarray(x, dtype=float)
    left = np.divide(x-a, b-a, out=np.zeros_like(x), where=(b-a)!=0)
    right = np.divide(d-x, d-c, out=np.zeros_like(x), where=(d-c)!=0)
    return np.maximum(0, np.minimum(np.minimum(left, 1), right))

def trimf(x, a, b, c):
    x = np.asarray(x, dtype=float)
    left = np.divide(x-a, b-a, out=np.zeros_like(x), where=(b-a)!=0)
    right = np.divide(c-x, c-b, out=np.zeros_like(x), where=(c-b)!=0)
    return np.maximum(0, np.minimum(left, right))

def memberships(value, sets):
    return {name: float(fn(value)) for name, fn in sets.items()}

def centroid(universe, aggregated):
    denominator = np.sum(aggregated)
    if denominator == 0:
        return float(np.mean(universe))
    return float(np.sum(universe * aggregated) / denominator)

def infer_fuzzy_needs(bmi, activity_level, calorie_delta, goal):
    # Normalized input: activity intensity 0-100.
    activity_values = {
        "Sedentary": 15,
        "Lightly Active": 40,
        "Moderately Active": 65,
        "Very Active": 90,
    }
    activity = activity_values.get(activity_level, 40)

    bmi_sets = {
        "low": lambda x: trapmf(x, 12, 12, 18.5, 20),
        "normal": lambda x: trimf(x, 18.5, 22, 25),
        "high": lambda x: trapmf(x, 24, 25, 30, 34),
    }
    activity_sets = {
        "low": lambda x: trapmf(x, 0, 0, 25, 45),
        "medium": lambda x: trimf(x, 30, 55, 75),
        "high": lambda x: trapmf(x, 60, 75, 100, 100),
    }
    delta_sets = {
        "deficit": lambda x: trapmf(x, -800, -600, -250, -50),
        "balanced": lambda x: trimf(x, -100, 0, 100),
        "surplus": lambda x: trapmf(x, 50, 250, 600, 800),
    }

    bmi_m = memberships(bmi, bmi_sets)
    activity_m = memberships(activity, activity_sets)
    delta_m = memberships(calorie_delta, delta_sets)

    # Goal memberships are crisp because the goal is a selected categorical input.
    goal_weight_loss = 1.0 if goal == "Weight Loss" else 0.0
    goal_muscle = 1.0 if goal == "Muscle Building" else 0.0
    goal_gain = 1.0 if goal == "Weight Gain" else 0.0
    goal_healthy = 1.0 if goal == "Healthy Eating" else 0.0

    universe = np.linspace(0, 100, 1001)
    low = trapmf(universe, 0, 0, 25, 45)
    medium = trimf(universe, 30, 50, 70)
    high = trapmf(universe, 55, 75, 100, 100)

    wl = []
    protein = []
    energy = []

    # Rule 1: high BMI + weight-loss goal -> high weight-loss need
    wl.append(min(bmi_m["high"], goal_weight_loss))
    # Rule 2: calorie deficit + weight-loss goal -> high weight-loss need
    wl.append(min(delta_m["deficit"], goal_weight_loss))
    # Rule 3: high activity + muscle building -> high protein need
    protein.append(min(activity_m["high"], goal_muscle))
    # Rule 4: high activity + weight gain/muscle building -> high energy need
    energy.append(max(min(activity_m["high"], goal_gain), min(activity_m["high"], goal_muscle)))
    # Rule 5: low activity + high BMI -> medium/high weight-loss need
    wl.append(min(activity_m["low"], bmi_m["high"]))
    # Rule 6: muscle building + balanced/surplus calories -> high protein need
    protein.append(max(min(goal_muscle, delta_m["balanced"]), min(goal_muscle, delta_m["surplus"])))
    # Rule 7: weight gain + calorie surplus -> high energy need
    energy.append(min(goal_gain, delta_m["surplus"]))
    # Rule 8: healthy eating + normal BMI -> medium balanced need
    healthy_balanced = min(goal_healthy, bmi_m["normal"])
    protein.append(healthy_balanced * 0.6)
    energy.append(healthy_balanced * 0.6)

    def aggregate(strengths):
        arr = np.zeros_like(universe)
        if strengths:
            # First strength maps to high; all rules in this output are interpreted
            # as "high need" rules. Add a baseline medium rule for non-extreme cases.
            for s in strengths:
                arr = np.maximum(arr, np.minimum(s, high))
        return arr

    wl_agg = aggregate(wl)
    protein_agg = aggregate(protein)
    energy_agg = aggregate(energy)

    # Baseline medium memberships preserve useful outputs for neutral profiles.
    neutral_strength = max(0.15, 1 - max(wl, default=0), 1 - max(protein, default=0), 1 - max(energy, default=0))
    protein_agg = np.maximum(protein_agg, np.minimum(0.25 * neutral_strength, medium))
    energy_agg = np.maximum(energy_agg, np.minimum(0.25 * neutral_strength, medium))

    return {
        "weight_loss_need": round(centroid(universe, wl_agg), 1),
        "protein_need": round(centroid(universe, protein_agg), 1),
        "energy_need": round(centroid(universe, energy_agg), 1),
        "activity_intensity": activity,
        "memberships": {
            "bmi": bmi_m,
            "activity": activity_m,
            "calorie_delta": delta_m,
        },
    }

def fuzzy_explanation(result):
    p = result["protein_need"]
    w = result["weight_loss_need"]
    e = result["energy_need"]
    parts = []
    if p >= 60:
        parts.append("high protein need")
    elif p >= 40:
        parts.append("moderate protein need")
    if w >= 60:
        parts.append("high weight-management focus")
    elif w >= 40:
        parts.append("moderate weight-management focus")
    if e >= 60:
        parts.append("high energy need")
    elif e >= 40:
        parts.append("moderate energy need")
    return ", ".join(parts) if parts else "balanced nutrition needs"
