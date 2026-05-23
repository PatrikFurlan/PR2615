import streamlit as st
import pandas as pd
import hdbscan
import pydeck as pdk
from pyproj import Transformer
import numpy as np
import matplotlib.cm as cm

st.set_page_config(layout="wide", page_title="Analiza prometnih žarišč SLO")

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("merged_clean.csv")
        df = df.dropna(subset=['GeoKoordinataX', 'GeoKoordinataY'])
        df['Starost'] = pd.to_numeric(df['Starost'], errors='coerce').fillna(0)
        df['UraPN'] = pd.to_numeric(df['UraPN'], errors='coerce').fillna(0)
        return df
    except Exception as e:
        st.error(f"Napaka pri nalaganju datoteke: {e}")
        return pd.DataFrame()

master_df = load_data()

MESTA_CENTRI = {
    "LJUBLJANA": {"lat": 46.0569, "lon": 14.5058, "zoom": 12},
    "MARIBOR":   {"lat": 46.5547, "lon": 15.6459, "zoom": 13},
    "CELJE":     {"lat": 46.2397, "lon": 15.2677, "zoom": 13},
    "KRANJ":     {"lat": 46.2428, "lon": 14.3555, "zoom": 13},
    "KOPER":     {"lat": 45.5481, "lon": 13.7301, "zoom": 13}
}

VRSTE_UDELEZENCEV = [
    "VOZNIK OSEBNEGA AVTOMOBILA",
    "VOZNIK TOVORNEGA VOZILA",
    "OSTALO",
    "POTNIK",
    "KOLESAR",
    "VOZNIK MOTORNEGA KOLESA",
    "PEŠEC",
    "VOZNIK MOPEDA",
    "VOZNIK AVTOBUSA",
    "VOZNIK TRAKTORJA",
    "VOZNIK MOPEDA DO 25 KM/H",
    "VOZNIK LAHKEGA MOTORNEGA VOZILA",
]

st.sidebar.header("Nastavitve filtrov")

izbrano_ue = st.sidebar.selectbox("Izberi upravno enoto", list(MESTA_CENTRI.keys()))

atributi = {
    "Vzrok nesreče":       "VzrokNesrece",
    "Klasifikacija":       "KlasifikacijaNesrece",
    "Vreme":               "VremenskeOkoliscine",
    "Poškodba udeleženca": "PoskodbaUdelezenca",
    "Varnostni pas":       "UporabaVarnostnegaPasu",
    "Tip nesreče":         "TipNesrece",
    "Stanje vozišča":      "StanjeVozisca",
    "Vrsta udeleženca":    "VrstaUdelezenca",
    "Državljanstvo":       "Drzavljanstvo",
}
izbran_prikaz_ime = st.sidebar.selectbox("Glavni atribut analize", list(atributi.keys()))
izbran_stolpec = atributi[izbran_prikaz_ime]

if izbran_stolpec == "VrstaUdelezenca":
    vse_vrednosti = VRSTE_UDELEZENCEV
else:
    vse_vrednosti = sorted(master_df[izbran_stolpec].unique().astype(str))
izbrana_vrednost = st.sidebar.selectbox(f"Izberi vrednost za {izbran_prikaz_ime}", vse_vrednosti)

st.sidebar.subheader("Dodatni filtri")
starost_range = st.sidebar.slider("Razpon starosti", 0, 100, (0, 100))
ura_range = st.sidebar.slider("Ura nesreče (od-do)", 0, 23, (0, 23))

st.sidebar.subheader("HDBSCAN Parametri")
min_c_size = st.sidebar.slider("Minimalna velikost gruče", 2, 100, 15)
min_samples = st.sidebar.slider("Minimalno število sosedov (gostota)", 1, 20, 5)

FIXED_OFFSET_X = 415
FIXED_OFFSET_Y = -445

mask = (
    (master_df['UpravnaEnotaStoritve'].str.contains(izbrano_ue, na=False, case=False)) &
    (master_df[izbran_stolpec] == izbrana_vrednost) &
    (master_df['Starost'] >= starost_range[0]) &
    (master_df['Starost'] <= starost_range[1]) &
    (master_df['UraPN'] >= ura_range[0]) &
    (master_df['UraPN'] <= ura_range[1])
)

df_filtered = master_df[mask].drop_duplicates('ID').copy()

if len(df_filtered) >= 2:
    transformer = Transformer.from_crs("epsg:3912", "epsg:4326", always_xy=True)
    df_filtered['lon'], df_filtered['lat'] = transformer.transform(
        df_filtered['GeoKoordinataY'].values + FIXED_OFFSET_X,
        df_filtered['GeoKoordinataX'].values + FIXED_OFFSET_Y
    )

    clusterer = hdbscan.HDBSCAN(min_cluster_size=min_c_size, min_samples=min_samples)
    df_filtered['Cluster'] = clusterer.fit_predict(df_filtered[['lon', 'lat']])

    cluster_counts = df_filtered['Cluster'].value_counts().to_dict()
    valid_counts = [count for cid, count in cluster_counts.items() if cid != -1]
    max_size = max(valid_counts) if valid_counts else 1
    min_size = min(valid_counts) if valid_counts else 0

    def get_style(cluster_id):
        if cluster_id == -1:
            return [200, 200, 200, 40], 8
        if max_size == min_size:
            return [200, 200, 200, 120], 20
        size = cluster_counts.get(cluster_id, 0)
        norm_val = (size - min_size) / (max_size - min_size)
        cmap = cm.get_cmap('YlOrRd')
        color = cmap(0.3 + norm_val * 0.6)
        rgb = [int(x * 255) for x in color[:3]]
        return rgb + [220], 35

    df_filtered['style']  = df_filtered['Cluster'].apply(get_style)
    df_filtered['color']  = df_filtered['style'].apply(lambda x: x[0])
    df_filtered['radius'] = df_filtered['style'].apply(lambda x: x[1])

    st.title(f"Analiza žarišč: {izbrano_ue}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Število prikazanih nesreč", len(df_filtered))

    st.sidebar.subheader("Legenda")
    st.sidebar.markdown("- 🔴 **Rdeča**: Močno žarišče\n- 🟠 **Oranžna**: Srednje žarišče\n- 🟡 **Rumena**: Šibko žarišče")

    view_state = pdk.ViewState(
        latitude=MESTA_CENTRI[izbrano_ue]["lat"],
        longitude=MESTA_CENTRI[izbrano_ue]["lon"],
        zoom=MESTA_CENTRI[izbrano_ue]["zoom"],
        pitch=40,
        bearing=0
    )

    layer = pdk.Layer(
        "ScatterplotLayer",
        df_filtered,
        get_position='[lon, lat]',
        get_color='color',
        get_radius='radius',
        pickable=True,
        stroked=True,
        line_width_min_pixels=1,
        get_line_color=[255, 255, 255, 100]
    )

    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style=None,
        tooltip={"text": "Vzrok: {VzrokNesrece}\nStarost: {Starost}\nUra: {UraPN}\nŠt. v gruči: {Cluster}"}
    ), use_container_width=True)

else:
    st.title(f"Analiza žarišč: {izbrano_ue}")
    st.warning(f"Ni najdenih podatkov za vrednost: {izbrana_vrednost}. Poskusite spremeniti razpon starosti ali ure.")
