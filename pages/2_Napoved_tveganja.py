import streamlit as st
import pandas as pd
import numpy as np
from sklearn.naive_bayes import CategoricalNB
from sklearn.preprocessing import LabelEncoder
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="Napoved tveganja nesreče")

@st.cache_data
def load_data():
    df = pd.read_csv("merged_clean.csv")
    df['Starost'] = pd.to_numeric(df['Starost'], errors='coerce')
    df['VrednostAlkotesta'] = pd.to_numeric(df['VrednostAlkotesta'], errors='coerce')
    return df

df = load_data()


hude_klasifikacije = ['S HUDO TELESNO POŠKODBO', 'S SMRTNIM IZIDOM']
df['Target'] = df['KlasifikacijaNesrece'].apply(lambda x: 1 if x in hude_klasifikacije else 0)

features = [
    'Starost',
    'UporabaVarnostnegaPasu',
    'VrednostAlkotesta',
    'VremenskeOkoliscine',
    'VrstaVozisca',
    'VrstaCesteNaselja'
]

model_df = df[features + ['Target']].dropna().copy()

model_df['Starost'] = pd.cut(
    model_df['Starost'],
    bins=[0, 24, 40, 60, 120],
    labels=['0-24', '55-40', '41-60', '60+']
)

model_df['VrednostAlkotesta'] = pd.cut(
    model_df['VrednostAlkotesta'],
    bins=[-0.01, 0.0, 0.5, 10.0],
    labels=['Ni alkohola (0)', 'Nizek (0-0.5)', 'Visok (>0.5)']
)

encoders = {}
for col in features:
    le = LabelEncoder()
    model_df[col] = le.fit_transform(model_df[col].astype(str))
    encoders[col] = le

X = model_df[features]
y = model_df['Target']

model = CategoricalNB()
model.fit(X, y)


st.title("Napovedni model: Verjetnost pojava nesreče s hudimi poškodbami glede na vrednosti atributov")
st.write("""
Ta model uporablja algoritem **Naivnega Bayesa** za izracun verjetnosti, da se bo prometna nesreca
koncala s hudimi poškodbami ali smrtjo.
""")

st.divider()

#st.latex(r"P(\text{Huda} \mid \text{Okoliscine}) = \frac{P(\text{Okoliscine} \mid \text{Huda}) \cdot P(\text{Huda})}{P(\text{Okoliscine})}")


st.sidebar.header("Okoliscine nesrece")

starost_choice = st.sidebar.selectbox(
    "Starost voznika",
    ['0—24', '25—40', '41—60', '60+']
)

pas_options = encoders['UporabaVarnostnegaPasu'].classes_
pas_choice = st.sidebar.selectbox("Uporaba varnostnega pasu", pas_options)

alkotest_choice = st.sidebar.selectbox(
    "Vrednost alkotesta",
    ['Ni alkohola (0)', 'Nizek (0-0.5)', 'Visok (>0.5)']
)

vreme_options = encoders['VremenskeOkoliscine'].classes_
vreme_choice = st.sidebar.selectbox("Vremenske okoliscine", vreme_options)

vozisce_options = encoders['VrstaVozisca'].classes_
vozisce_choice = st.sidebar.selectbox("Vrsta vozisca", vozisce_options)

cesta_options = encoders['VrstaCesteNaselja'].classes_
cesta_choice = st.sidebar.selectbox("Vrsta ceste / naselja", cesta_options)


def encode_safe(encoder, value):
    classes = list(encoder.classes_)
    if value in classes:
        return encoder.transform([value])[0]
    return 0

inputs = {
    'Starost':                encode_safe(encoders['Starost'], starost_choice),
    'UporabaVarnostnegaPasu': encode_safe(encoders['UporabaVarnostnegaPasu'], pas_choice),
    'VrednostAlkotesta':      encode_safe(encoders['VrednostAlkotesta'], alkotest_choice),
    'VremenskeOkoliscine':    encode_safe(encoders['VremenskeOkoliscine'], vreme_choice),
    'VrstaVozisca':           encode_safe(encoders['VrstaVozisca'], vozisce_choice),
    'VrstaCesteNaselja':      encode_safe(encoders['VrstaCesteNaselja'], cesta_choice),
}

input_array = np.array([list(inputs.values())])
prob = model.predict_proba(input_array)[0][1]
pct  = prob * 100

col_gauge, col_info = st.columns([1.2, 1])

with col_gauge:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pct,
        number={'suffix': ' %', 'font': {'size': 60}},
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Verjetnost hudih posledic", 'font': {'size': 24}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "gray"},
            'bar': {'color': "#222"},
            'bgcolor': "white",       
            'borderwidth': 1,
            'bordercolor': "#ccc",
            'steps': [
                {'range': [0, 15],   'color': "#00CC96"}, 
                {'range': [15, 35],  'color': "#FFA15A"}, 
                {'range': [35, 100], 'color': "#EF553B"}, 
            ],
        }
    ))
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'family': "Arial"},
        height=400,
        margin=dict(t=80, b=20, l=30, r=30)
    )
    st.plotly_chart(fig, use_container_width=True)

with col_info:
    st.subheader("Interpretacija rezultata")
    st.write(f"""
    Glede na izbrane dejavnike je verjetnost, da bo nesreca povzrocila **hude telesne poskodbe ali smrt**,
    znasala **{pct:.1f} %**.
    """)

    if pct > 35:
        st.error("VISOKO TVEGANJE - Izbrana kombinacija dejavnikov je statistično zelo nevarna!")
    elif pct > 15:
        st.warning("SREDNJE TVEGANJE - Tveganje je zmerno.")
    else:
        st.success("NIZKO TVEGANJE - Izbrana kombinacija dejavnikov predstavlja nizko tveganje za hude posledice.")


