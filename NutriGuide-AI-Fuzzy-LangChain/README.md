# NutriGuide AI — Diet Food Recommendation System
## Fuzzy Logic + LangChain/LLM Reasoning

NutriGuide AI is a college-level academic AI application that recommends foods using a **genuine fuzzy inference system** and an optional **LangChain/LLM explanation layer**.

The system is deliberately hybrid:

1. **Deterministic nutrition calculations** calculate BMI, BMR and TDEE.
2. **Fuzzy Logic inference** models gradual nutrition needs using membership functions, fuzzy rules and centroid defuzzification.
3. **Food filtering** enforces dietary preferences and allergy constraints.
4. **Recommendation scoring** combines fuzzy outputs with meal, cuisine, budget and nutrition suitability.
5. **LangChain/LLM reasoning** optionally converts structured results into a natural-language explanation. The LLM does not replace the deterministic calculations or fuzzy inference.

> **Disclaimer:** This is an academic recommendation prototype, not a medical diagnosis or treatment system. Users with medical conditions should consult a qualified healthcare professional.

## Main Features

- Professional Streamlit UI
- BMI / BMR / TDEE calculations
- 57-food local nutrition dataset
- Vegetarian / Vegan / Eggetarian / Non-Vegetarian filtering
- Allergy filtering
- Cuisine and budget filtering
- Five-meal diet plan
- Genuine fuzzy inference system
- Fuzzy membership functions
- Fuzzy rule aggregation
- Centroid defuzzification
- Explainable recommendation scoring
- Optional LangChain + OpenAI LLM explanation
- Local fallback when no LLM key is available
- Food Explorer
- Nutrition charts
- IKS section
- Streamlit Community Cloud ready

## Technology

- Python
- Streamlit
- Pandas
- NumPy
- Plotly
- LangChain
- LangChain OpenAI integration
- Custom fuzzy inference implementation
- HTML/CSS through Streamlit

## Architecture

```text
                 USER PROFILE
                      |
             BMI / BMR / TDEE
                      |
                      v
            +-------------------+
            | FUZZY INFERENCE   |
            | Membership Funcs  |
            | Fuzzy Rules       |
            | Centroid Output   |
            +-------------------+
                      |
                      v
            FOOD FILTERING
       / Dietary / Allergy /
                      |
                      v
          FUZZY + RULE SCORE
                      |
                      v
              DIET PLAN
                      |
          +-----------+-----------+
          |                       |
          v                       v
  Nutrition Dashboard     LangChain / LLM
                          Explanation Layer
```

## Why Fuzzy Logic?

Human nutrition categories are not always binary. For example, an activity level or BMI can be closer to one category while still partially belonging to another.

NutriGuide uses:

- triangular membership functions
- trapezoidal membership functions
- fuzzy AND using minimum
- rule aggregation using maximum
- centroid defuzzification

### Example

```text
IF BMI is HIGH
AND Goal is WEIGHT LOSS
THEN Weight-loss Need is HIGH
```

```text
IF Activity is HIGH
AND Goal is MUSCLE BUILDING
THEN Protein Need is HIGH
```

```text
IF Activity is HIGH
AND Goal is MUSCLE BUILDING
THEN Energy Need is HIGH
```

The resulting fuzzy values are numerical scores from 0–100 and are used directly by the food-ranking engine.

## LangChain / LLM Layer

The LLM layer is optional.

Without an API key, the complete recommendation system still works because all calculations and fuzzy inference are local.

With an API key:

```text
Structured recommendation results
            ↓
       LangChain prompt
            ↓
          LLM
            ↓
Natural-language explanation
```

The LLM is explicitly instructed not to:

- diagnose diseases
- prescribe treatment
- modify computed nutrition numbers
- override allergy filtering

### Environment variables

Copy `.env.example` to `.env` if running locally and configure:

```text
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

The application also reads normal environment variables, which is suitable for Streamlit Community Cloud Secrets.

## Installation

Open PowerShell in the project folder (`NutriGuide-AI-Fuzzy-LangChain` if you cloned the parent repository), then run:

```bash
python -m venv .venv
```

Activate the environment in PowerShell:

```bash
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use the environment's Python directly instead:

```bash
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

When activation succeeds, install with:

```bash
python -m pip install -r requirements.txt
```

## Run

```bash
python -m streamlit run app.py
```

No LLM key is required to run the core application.

## Streamlit Community Cloud

1. Push this project to a GitHub repository. If you cloned the parent repository, keep the `NutriGuide-AI-Fuzzy-LangChain` folder and its `data/`, `utils/`, and `.streamlit/` directories together.
2. In [Streamlit Community Cloud](https://share.streamlit.io/), create an app and select that repository and branch.
3. Set **Main file path** to `NutriGuide-AI-Fuzzy-LangChain/app.py` when deploying from the parent repository. If this project folder is the repository root, use `app.py`.
4. Deploy. The dependency manifest is `NutriGuide-AI-Fuzzy-LangChain/requirements.txt` (or `requirements.txt` when the project folder is the repository root).

The LLM is optional; the application works without a key. To enable it, open the app's **Settings → Secrets** and add:

```toml
OPENAI_API_KEY = "your-api-key"
OPENAI_MODEL = "gpt-4o-mini"
```

For local development, copy `.env.example` to `.env` and set the same values there. Never commit `.env` or `.streamlit/secrets.toml`; they are excluded by the repository `.gitignore`.

## Project Structure

```text
Diet-Food-Recommendation/
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── data/
│   └── foods.csv
├── utils/
│   ├── __init__.py
│   ├── calculations.py
│   ├── data_loader.py
│   ├── fuzzy_engine.py
│   ├── recommender.py
│   └── llm_reasoner.py
└── assets/
    ├── logo.svg
    └── logo.png
```

## Viva Explanation

### What makes this an AI project?

It combines a fuzzy inference system for reasoning under gradual/uncertain categories with an optional LLM reasoning layer for natural-language explanation.

### Is it machine learning?

The current version is not trained machine learning. It is an **explainable AI / knowledge-based system** using fuzzy inference. Future versions can add ML trained on a larger nutrition dataset.

### Why not let the LLM calculate everything?

Nutrition calculations and safety-related filtering should be deterministic and reproducible. The LLM is therefore used for explanation rather than replacing the core inference logic.

### What is fuzzification?

Converting a crisp input, such as BMI 27.5, into membership degrees such as partially normal and partially high.

### What is defuzzification?

Converting the aggregated fuzzy output back into a single numerical value. This project uses the centroid method.

### What is LangChain?

LangChain provides a structured framework for connecting application data and prompts to an LLM. In this project it is an optional explanation layer.

### Future Scope

- ML-based recommendation models
- Larger nutrition datasets
- User feedback learning
- Multilingual AI explanations
- More sophisticated fuzzy rules
- Personalized meal quantities
- Nutrition-label import
- Offline/local LLM support

## Academic Disclaimer

NutriGuide AI is an educational software prototype. It does not provide medical diagnosis, treatment, or clinical nutrition advice. Users with medical conditions should consult a qualified healthcare professional.
