
"""Optional LangChain/LLM explanation layer.

The deterministic calculations and fuzzy inference always run locally.
LangChain is used only to turn structured results into a readable explanation
when an API key/provider is configured. If unavailable, a local explanation is
returned so the application remains usable and deployable without an LLM key.
"""
import os

import streamlit as st
from dotenv import load_dotenv
from streamlit.errors import StreamlitSecretNotFoundError

load_dotenv()


def _get_setting(name, default=""):
    value = os.getenv(name, "").strip()
    if value:
        return value

    try:
        return str(st.secrets.get(name, default)).strip()
    except StreamlitSecretNotFoundError:
        return default


def build_prompt(profile, metrics, fuzzy, plan):
    foods = []
    for meal, item in plan.items():
        r = item["row"]
        foods.append(f"{meal}: {r['Food Name']} ({r['Calories']:.0f} kcal, {r['Protein']:.0f}g protein)")
    return f"""
You are the explanation layer of NutriGuide AI, an academic nutrition recommendation prototype.
Do not diagnose disease, prescribe treatment, or make medical claims.
Explain the already-computed recommendation. Do not change the computed numbers.

Profile:
- Goal: {profile['Fitness Goal']}
- Dietary preference: {profile['Dietary Preference']}
- Cuisine: {profile['Cuisine']}
- Budget: {profile['Budget']}
- Allergy: {profile['Allergy']}
- BMI: {metrics['bmi']}
- BMR: {metrics['bmr']:.0f}
- TDEE: {metrics['tdee']:.0f}
- Calorie target: {metrics['target']:.0f}
- Protein target: {metrics['protein']:.0f}

Fuzzy inference outputs:
- Weight-loss need: {fuzzy['weight_loss_need']}
- Protein need: {fuzzy['protein_need']}
- Energy need: {fuzzy['energy_need']}

Generated meals:
{chr(10).join(foods)}

Write a concise 4-6 sentence explanation of why the system selected these foods.
""".strip()

def generate_llm_explanation(profile, metrics, fuzzy, plan):
    api_key = _get_setting("OPENAI_API_KEY")
    if not api_key:
        return (
            "LLM reasoning is optional in this deployment. The local fuzzy inference system "
            f"identified {('high' if fuzzy['protein_need'] >= 60 else 'moderate' if fuzzy['protein_need'] >= 40 else 'balanced')} "
            "protein need and combined that result with dietary preference, cuisine, budget, "
            "meal suitability and nutrition values to rank foods. The generated plan is therefore "
            "traceable to deterministic calculations plus fuzzy inference."
        )

    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import ChatPromptTemplate
        prompt = build_prompt(profile, metrics, fuzzy, plan)
        llm = ChatOpenAI(model=_get_setting("OPENAI_MODEL", "gpt-4o-mini"), temperature=0.2, api_key=api_key)
        response = llm.invoke([("system", "You are a careful academic nutrition explanation assistant."), ("human", prompt)])
        return response.content
    except Exception as exc:
        return (
            "The configured LLM explanation service was unavailable, so NutriGuide AI used its "
            f"local explainable fallback. Technical detail: {type(exc).__name__}. "
            "The fuzzy inference and food recommendation calculations remain available."
        )
