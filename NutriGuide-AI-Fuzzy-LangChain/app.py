
import os
import pandas as pd
import plotly.express as px
import streamlit as st

from utils.data_loader import load_foods
from utils.calculations import calculate_bmi, calculate_bmr, calculate_tdee, calorie_target, protein_target
from utils.recommender import generate_plan, apply_diet_filter, apply_allergy_filter
from utils.llm_reasoner import generate_llm_explanation

st.set_page_config(page_title="NutriGuide AI", page_icon="🥗", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root{--g:#16805b;--dark:#17231f;--muted:#68756f;--line:#e2ebe6}
html,body,[class*="css"]{font-family:Inter,sans-serif}
.stApp{background:#f7faf8;color:var(--dark)}
.block-container{max-width:1250px;padding-top:1.4rem}
.brand{font-size:1.45rem;font-weight:800;color:#12382c}
.brand span{color:var(--g)}
.hero{background:linear-gradient(135deg,#edf9f3,#fff);border:1px solid var(--line);border-radius:26px;padding:48px;margin:12px 0 28px}
.hero h1{font-size:clamp(2.5rem,6vw,4.6rem);line-height:.98;letter-spacing:-3px;margin:0 0 18px}
.hero p{font-size:1.08rem;color:var(--muted);max-width:700px;line-height:1.7}
.pill{display:inline-block;padding:7px 12px;border-radius:99px;background:#dff3ea;color:#116346;font-weight:700;font-size:.78rem}
.card,.food{background:#fff;border:1px solid var(--line);border-radius:18px;padding:20px;box-shadow:0 8px 28px rgba(18,56,44,.05)}
.metric{background:#fff;border:1px solid var(--line);border-radius:16px;padding:16px}
.metric .label{font-size:.8rem;color:#728079}.metric .value{font-size:1.45rem;font-weight:800;margin-top:4px}
.section{font-size:1.7rem;font-weight:800;margin:26px 0 8px}
.subtle{color:#68756f}
.food{margin:10px 0}
.food h3{margin:0 0 8px}
.footer{text-align:center;color:#77847e;padding:35px 0 10px;border-top:1px solid var(--line);margin-top:45px}
</style>
""", unsafe_allow_html=True)

try:
    foods = load_foods()
except Exception as exc:
    st.error(f"Food database could not be loaded: {exc}")
    st.stop()

st.markdown('<div class="brand">🥗 NutriGuide <span>AI</span></div>', unsafe_allow_html=True)
st.caption("Smart food recommendations for your daily goals • Fuzzy Logic + optional LangChain/LLM reasoning")

with st.sidebar:
    st.markdown("### Navigation")
    page = st.radio("Go to", ["Home","Recommendation","Food Explorer","AI Architecture","IKS","About"], key="nav")
    st.markdown("---")
    st.markdown("**AI components**")
    st.write("✓ Genuine fuzzy inference")
    st.write("✓ Explainable scoring")
    st.write("✓ Optional LangChain LLM")
    st.caption("No API key is required for the core application.")

def metric(label,value):
    st.markdown(f'<div class="metric"><div class="label">{label}</div><div class="value">{value}</div></div>',unsafe_allow_html=True)

if page == "Home":
    st.markdown("""
    <div class="hero">
      <span class="pill">EXPLAINABLE AI NUTRITION</span>
      <h1>Eat smarter.<br>Reach your goals.</h1>
      <p>NutriGuide AI combines deterministic nutrition calculations, a genuine fuzzy inference system and an optional LangChain/LLM explanation layer to create understandable food recommendations.</p>
    </div>
    """,unsafe_allow_html=True)
    a,b,c=st.columns(3)
    with a: st.markdown('<div class="card"><h3>🧠 Fuzzy Logic</h3><p class="subtle">Handles gradual concepts such as low, medium and high nutrition needs instead of rigid yes/no thresholds.</p></div>',unsafe_allow_html=True)
    with b: st.markdown('<div class="card"><h3>🔗 LangChain / LLM</h3><p class="subtle">Optionally converts structured AI results into natural-language reasoning. The core system works without an API key.</p></div>',unsafe_allow_html=True)
    with c: st.markdown('<div class="card"><h3>🔍 Explainable</h3><p class="subtle">Every recommendation can be traced to profile filters, nutrition values, fuzzy outputs and scoring rules.</p></div>',unsafe_allow_html=True)
    st.markdown('<div class="section">AI pipeline</div>',unsafe_allow_html=True)
    st.info("User Profile → BMI/BMR/TDEE → Fuzzy Membership Functions → Fuzzy Rules → Food Filtering & Scoring → Optional LangChain/LLM Explanation → Diet Plan")
    if st.button("Get My Recommendations",type="primary",use_container_width=True):
        st.session_state["nav"]="Recommendation"; st.rerun()
    st.warning("Academic disclaimer: this is an educational recommendation prototype, not a medical diagnosis or treatment system. Users with medical conditions should consult a qualified healthcare professional.")

elif page == "Recommendation":
    st.markdown('<div class="section">Personalized AI recommendation</div>',unsafe_allow_html=True)
    with st.form("profile"):
        c1,c2,c3=st.columns(3)
        with c1:
            name=st.text_input("Name *")
            age=st.number_input("Age *",0,120,24)
            gender=st.selectbox("Gender",["Male","Female"])
            height=st.number_input("Height (cm) *",0.0,300.0,170.0)
        with c2:
            weight=st.number_input("Weight (kg) *",0.0,400.0,70.0)
            activity=st.selectbox("Activity Level",["Sedentary","Lightly Active","Moderately Active","Very Active"])
            goal=st.selectbox("Fitness Goal",["Weight Loss","Weight Maintenance","Weight Gain","Muscle Building","Healthy Eating"])
            diet=st.selectbox("Dietary Preference",["Vegetarian","Non-Vegetarian","Vegan","Eggetarian"])
        with c3:
            allergy=st.selectbox("Food Allergies",["None","Milk/Dairy","Gluten","Nuts","Eggs","Soy"])
            meals=st.selectbox("Meals per day",[3,4,5],index=2)
            budget=st.selectbox("Budget Preference",["Low","Medium","Premium"])
            cuisine=st.selectbox("Cuisine Preference",["Indian","North Indian","South Indian","Mixed"])
        submit=st.form_submit_button("Generate My Diet Plan",type="primary",use_container_width=True)

    if submit:
        if not name.strip() or not (18<=age<=100) or not (100<=height<=250) or not (25<=weight<=300):
            st.warning("Please provide a name and realistic age, height and weight values.")
        else:
            bmi,bmi_cat=calculate_bmi(weight,height)
            bmr=calculate_bmr(weight,height,int(age),gender)
            tdee=calculate_tdee(bmr,activity)
            target=calorie_target(tdee,goal)
            prot=protein_target(weight,goal)
            profile={"Name":name,"Age":int(age),"Gender":gender,"Height":height,"Weight":weight,"Activity":activity,
                     "Fitness Goal":goal,"Dietary Preference":diet,"Allergy":allergy,"Meals":meals,"Budget":budget,"Cuisine":cuisine,"BMI":bmi}
            plan,fuzzy,fuzzy_summary=generate_plan(foods,profile,tdee,target)
            metrics={"bmi":bmi,"bmi_cat":bmi_cat,"bmr":bmr,"tdee":tdee,"target":target,"protein":prot}
            st.session_state.update(profile=profile,plan=plan,fuzzy=fuzzy,metrics=metrics,fuzzy_summary=fuzzy_summary)

    if "profile" in st.session_state:
        profile=st.session_state["profile"]; plan=st.session_state["plan"]; fuzzy=st.session_state["fuzzy"]; m=st.session_state["metrics"]
        st.success(f"AI analysis completed for {profile['Name'].strip().title()}.")
        cols=st.columns(6)
        vals=[("BMI",f"{m['bmi']} • {m['bmi_cat']}"),("BMR",f"{m['bmr']:.0f} kcal"),("TDEE",f"{m['tdee']:.0f} kcal"),("Calorie target",f"{m['target']:.0f} kcal"),("Protein target",f"{m['protein']:.0f} g"),("Fuzzy protein need",f"{fuzzy['protein_need']:.0f}/100")]
        for col,(lab,val) in zip(cols,vals):
            with col: metric(lab,val)

        st.markdown('<div class="section">Fuzzy inference result</div>',unsafe_allow_html=True)
        f1,f2,f3=st.columns(3)
        with f1: metric("Weight-loss need",f"{fuzzy['weight_loss_need']:.0f}/100")
        with f2: metric("Protein need",f"{fuzzy['protein_need']:.0f}/100")
        with f3: metric("Energy need",f"{fuzzy['energy_need']:.0f}/100")
        st.caption(f"Fuzzy interpretation: {st.session_state['fuzzy_summary']}.")

        st.markdown('<div class="section">Generated daily plan</div>',unsafe_allow_html=True)
        totals={k:0 for k in ["Calories","Protein","Carbohydrates","Fat","Fiber"]}
        for meal,item in plan.items():
            row=item["row"]
            for k in totals: totals[k]+=float(row[k])
            st.markdown(f"#### {meal.upper()}")
            reasons="; ".join(item["reasons"]) if item["reasons"] else "matches your profile"
            st.markdown(f"""
            <div class="food">
              <h3>🥗 {row['Food Name']}</h3>
              <b>{row['Calories']:.0f} kcal</b> • <b>{row['Protein']:.0f}g protein</b> • {row['Carbohydrates']:.0f}g carbs • {row['Fat']:.0f}g fat • {row['Fiber']:.0f}g fiber<br>
              <span class="subtle">Why recommended: {reasons}. Fuzzy score contribution is included in the ranking.</span>
            </div>""",unsafe_allow_html=True)
            filtered=apply_allergy_filter(apply_diet_filter(foods,profile["Dietary Preference"]),profile["Allergy"])
            alts=filtered[(filtered["Category"]==row["Category"])&(filtered["Food Name"]!=row["Food Name"])].head(3)
            if not alts.empty: st.caption("Alternatives: "+" → ".join(alts["Food Name"].tolist()))

        st.markdown('<div class="section">Nutrition dashboard</div>',unsafe_allow_html=True)
        cols=st.columns(5)
        for col,k in zip(cols,totals):
            with col: metric(k,f"{totals[k]:.0f} {'g' if k!='Calories' else 'kcal'}")
        st.progress(min(totals["Calories"]/m["target"],1.0),text=f"Calories {totals['Calories']:.0f} / {m['target']:.0f} kcal")
        st.progress(min(totals["Protein"]/m["protein"],1.0),text=f"Protein {totals['Protein']:.0f} / {m['protein']:.0f} g")
        chart=pd.DataFrame({"Nutrient":["Protein","Carbohydrates","Fat","Fiber"],"Amount":[totals["Protein"],totals["Carbohydrates"],totals["Fat"],totals["Fiber"]]})
        st.plotly_chart(px.bar(chart,x="Nutrient",y="Amount",template="simple_white",title="Macronutrient snapshot"),use_container_width=True)

        st.markdown('<div class="section">LangChain / LLM reasoning</div>',unsafe_allow_html=True)
        if os.getenv("OPENAI_API_KEY"):
            st.success("LLM provider detected. Generate an optional natural-language explanation.")
            if st.button("Generate AI Explanation"):
                with st.spinner("Generating explanation..."):
                    st.write(generate_llm_explanation(profile,m, fuzzy, plan))
        else:
            st.info("No OPENAI_API_KEY is configured. The application is still fully functional using local fuzzy inference and deterministic reasoning. Set OPENAI_API_KEY only if your academic deployment permits an LLM provider.")
            st.write(generate_llm_explanation(profile,m, fuzzy, plan))

elif page == "Food Explorer":
    st.markdown('<div class="section">Food Explorer</div>',unsafe_allow_html=True)
    q=st.text_input("Search food",placeholder="paneer, rice, banana...")
    c1,c2,c3,c4=st.columns(4)
    with c1: df_diet=st.selectbox("Diet",["All","Vegetarian","Vegan","Eggetarian","Non-Veg"])
    with c2: nf=st.selectbox("Nutrition",["All","High Protein","Low Calorie"])
    with c3: bf=st.selectbox("Budget",["All","Low","Medium","Premium"])
    with c4: cf=st.selectbox("Cuisine",["All","Indian","North Indian","South Indian","Mixed"])
    df=foods.copy()
    if q.strip(): df=df[df["Food Name"].str.contains(q.strip(),case=False,na=False)]
    if df_diet!="All": df=apply_diet_filter(df,"Non-Vegetarian" if df_diet=="Non-Veg" else df_diet)
    if nf=="High Protein": df=df[df["Protein"]>=12]
    if nf=="Low Calorie": df=df[df["Calories"]<=180]
    if bf!="All": df=df[df["Budget"]==bf]
    if cf!="All": df=df[df["Cuisine"]==cf]
    st.dataframe(df[["Food Name","Category","Calories","Protein","Carbohydrates","Fat","Fiber","Cuisine","Budget"]],use_container_width=True,hide_index=True)

elif page == "AI Architecture":
    st.markdown('<div class="section">AI Architecture</div>',unsafe_allow_html=True)
    st.markdown("""
    <div class="card">
    <h3>1. Deterministic nutrition layer</h3>
    <p>BMI, BMR and TDEE are calculated using explicit formulas. This layer provides stable numerical inputs.</p>
    <h3>2. Genuine Fuzzy Logic inference</h3>
    <p>Triangular/trapezoidal membership functions represent gradual concepts such as low, normal and high BMI/activity/energy states. Rules use fuzzy AND operations and the final output is defuzzified using the centroid method.</p>
    <h3>3. Recommendation layer</h3>
    <p>Diet and allergy filters are applied first. The fuzzy outputs then contribute to food ranking together with cuisine, budget, meal suitability and protein suitability.</p>
    <h3>4. LangChain / LLM reasoning</h3>
    <p>When an LLM key is configured, LangChain receives only the already-computed structured results and produces a natural-language explanation. It does not replace the fuzzy inference or nutrition formulas.</p>
    </div>
    """,unsafe_allow_html=True)
    st.markdown("### Example fuzzy rules")
    st.code("""IF BMI is HIGH
AND Fitness Goal is WEIGHT LOSS
THEN Weight-loss Need is HIGH

IF Activity is HIGH
AND Fitness Goal is MUSCLE BUILDING
THEN Protein Need is HIGH

IF Activity is HIGH
AND Fitness Goal is MUSCLE BUILDING
THEN Energy Need is HIGH""")
    st.markdown("### Why fuzzy logic?")
    st.write("Nutrition needs are not always clean yes/no categories. Fuzzy membership lets a value partially belong to categories such as low, medium and high, which is useful for an explainable academic recommendation prototype.")

elif page == "IKS":
    st.markdown('<div class="section">Indian Knowledge Systems (IKS)</div>',unsafe_allow_html=True)
    st.write("The project connects traditional Indian food knowledge with modern digital nutrition calculations.")
    st.markdown('<div class="card"><h3>Traditional Indian Food Knowledge</h3><p>🌾 Grains and millets • 🫘 Dal and legumes • 🍊 Seasonal fruits and vegetables • 🥣 Fermented foods • 🌿 Diverse plant foods</p></div>',unsafe_allow_html=True)
    st.markdown("**Traditional Indian Food Knowledge** ↓ **Grains / Pulses / Millets / Seasonal Foods** ↓ **Modern Nutrition Understanding** ↓ **Digital Recommendation System**")
    st.info("Ayurveda is treated only as historical/cultural context. The application does not diagnose or treat health conditions using Ayurveda.")

elif page == "About":
    st.markdown('<div class="section">About the Project</div>',unsafe_allow_html=True)
    st.markdown("""
    <div class="card">
    <h3>Project</h3><p>Diet Food Recommendation System — NutriGuide AI</p>
    <h3>Technology</h3><p>Python, Streamlit, Pandas, NumPy, Plotly, custom fuzzy inference, optional LangChain + LLM</p>
    <h3>Academic objective</h3><p>Demonstrate an explainable real-world AI application that combines deterministic nutrition calculations, fuzzy inference and optional natural-language reasoning.</p>
    <h3>Future scope</h3><p>Machine learning trained on larger nutrition datasets, user feedback, richer dietary datasets, multilingual explanations and improved personalization.</p>
    </div>
    """,unsafe_allow_html=True)
    st.code("""Diet-Food-Recommendation/
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── data/foods.csv
├── utils/
│   ├── calculations.py
│   ├── data_loader.py
│   ├── fuzzy_engine.py
│   ├── recommender.py
│   └── llm_reasoner.py
└── assets/logo.svg""")
    st.warning("Disclaimer: Educational prototype only. Not a medical diagnosis or treatment system.")

st.markdown('<div class="footer">NutriGuide AI | Diet Food Recommendation System<br>Academic Project • Fuzzy Logic + LangChain/LLM Reasoning</div>',unsafe_allow_html=True)
