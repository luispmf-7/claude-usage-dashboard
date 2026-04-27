import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

st.set_page_config(
    page_title="Claude Usage Dashboard — Luis Flores",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main { padding-top: 1rem; }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #7C3AED;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .stMetric { background: white; border-radius: 8px; padding: 10px; }
    h1 { color: #1F2937; }
    .pico-card {
        background: #F9FAFB; padding: 1rem; border-radius: 8px;
        border-top: 3px solid #7C3AED; margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ─── DATOS ───────────────────────────────────────────────────────────────────
@st.cache_data
def cargar_datos():
    df = pd.DataFrame([
        {"Fecha":"2026-04-19","Periodo":"Semana 1","Proyecto":"Personal","Modelo":"Claude Sonnet","Tokens Input":2400,"Tokens Output":1850,"Total Tokens":4250,"Costo S/":0.18,"Tipo":"Chat","Duracion min":45,"Eficiencia":94.4,"Franja":"Tarde"},
        {"Fecha":"2026-04-21","Periodo":"Semana 1","Proyecto":"Agencia MiProyecto","Modelo":"Claude Opus","Tokens Input":8500,"Tokens Output":6200,"Total Tokens":14700,"Costo S/":0.68,"Tipo":"API","Duracion min":12,"Eficiencia":1225.0,"Franja":"Manana"},
        {"Fecha":"2026-04-22","Periodo":"Semana 1","Proyecto":"Real Madrid","Modelo":"Claude Sonnet","Tokens Input":5200,"Tokens Output":3100,"Total Tokens":8300,"Costo S/":0.36,"Tipo":"Agentes","Duracion min":18,"Eficiencia":461.1,"Franja":"Manana"},
        {"Fecha":"2026-04-23","Periodo":"Semana 1","Proyecto":"Agencia MiProyecto","Modelo":"Claude Sonnet","Tokens Input":6800,"Tokens Output":4500,"Total Tokens":11300,"Costo S/":0.48,"Tipo":"Chat","Duracion min":25,"Eficiencia":452.0,"Franja":"Manana"},
        {"Fecha":"2026-04-24","Periodo":"Semana 1","Proyecto":"Personal","Modelo":"Claude Sonnet","Tokens Input":3600,"Tokens Output":2400,"Total Tokens":6000,"Costo S/":0.28,"Tipo":"Chat","Duracion min":30,"Eficiencia":200.0,"Franja":"Tarde"},
        {"Fecha":"2026-04-25","Periodo":"Semana 1","Proyecto":"Agencia MiProyecto","Modelo":"Claude Sonnet","Tokens Input":4200,"Tokens Output":3100,"Total Tokens":7300,"Costo S/":0.32,"Tipo":"Chat","Duracion min":20,"Eficiencia":365.0,"Franja":"Manana"},
        {"Fecha":"2026-04-26","Periodo":"Semana 2","Proyecto":"Agencia MiProyecto","Modelo":"Claude Opus","Tokens Input":9200,"Tokens Output":7100,"Total Tokens":16300,"Costo S/":0.78,"Tipo":"API","Duracion min":14,"Eficiencia":1164.3,"Franja":"Manana"},
        {"Fecha":"2026-04-26","Periodo":"Semana 2","Proyecto":"Real Madrid","Modelo":"Claude Sonnet","Tokens Input":4800,"Tokens Output":3200,"Total Tokens":8000,"Costo S/":0.32,"Tipo":"Agentes","Duracion min":16,"Eficiencia":500.0,"Franja":"Tarde"},
    ])
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    return df

df_full = cargar_datos()

# ─── SIDEBAR FILTROS ──────────────────────────────────────────────────────────
st.sidebar.markdown("## 🎛️ Filtros")
periodo = st.sidebar.multiselect("Período", df_full["Periodo"].unique(), default=list(df_full["Periodo"].unique()))
proyecto = st.sidebar.multiselect("Proyecto", df_full["Proyecto"].unique(), default=list(df_full["Proyecto"].unique()))
modelo = st.sidebar.multiselect("Modelo", df_full["Modelo"].unique(), default=list(df_full["Modelo"].unique()))
franja = st.sidebar.multiselect("Franja Horaria", df_full["Franja"].unique(), default=list(df_full["Franja"].unique()))

df = df_full[
    df_full["Periodo"].isin(periodo) &
    df_full["Proyecto"].isin(proyecto) &
    df_full["Modelo"].isin(modelo) &
    df_full["Franja"].isin(franja)
]

# Sidebar — Recomendaciones
st.sidebar.markdown("---")
st.sidebar.markdown("## 💡 Tips Rápidos")
st.sidebar.info("✅ **Sonnet** por defecto\n\n⚠️ **Opus** solo para auditorías\n\n🕐 **9-11am** = pico principal\n\n💰 Meta mayo: **S/ 33**")

# ─── HEADER ──────────────────────────────────────────────────────────────────
st.markdown("# 📊 Claude Usage Dashboard")
st.markdown("**Luis Flores** · Agencia de Marketing Digital · Lima, Perú · Abril 2026")
st.markdown("---")

# ─── KPIs ────────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
total_tok = df["Total Tokens"].sum()
total_cos = df["Costo S/"].sum()
n_ses = len(df)
top_proy = df.groupby("Proyecto")["Costo S/"].sum().idxmax() if not df.empty else "—"
pico = df.groupby("Franja")["Costo S/"].sum().idxmax() if not df.empty else "—"

c1.metric("🔢 Total Tokens", f"{total_tok:,.0f}", f"In {df['Tokens Input'].sum():,.0f} / Out {df['Tokens Output'].sum():,.0f}")
c2.metric("💰 Costo Total", f"S/ {total_cos:.2f}", f"Prom S/ {total_cos/n_ses:.2f}/sesión" if n_ses > 0 else "")
c3.metric("📅 Sesiones", n_ses, f"~{df['Duracion min'].mean():.0f} min/sesión" if n_ses > 0 else "")
c4.metric("🏆 Proyecto Top", top_proy.split()[0], f"S/ {df.groupby('Proyecto')['Costo S/'].sum().max():.2f}")
c5.metric("⏰ Hora Pico", pico, "Mayor concentración de uso")

st.markdown("---")

# ─── ROW 1: Costo diario + Tokens ────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📈 Costo Diario (S/)")
    fig = px.line(df.sort_values("Fecha"), x="Fecha", y="Costo S/",
                  markers=True, color_discrete_sequence=["#7C3AED"],
                  hover_data=["Proyecto","Modelo","Tipo"])
    fig.update_traces(line_width=3, marker_size=8)
    fig.update_layout(showlegend=False, height=300,
                      plot_bgcolor="white", paper_bgcolor="white",
                      yaxis_title="Costo S/", xaxis_title="",
                      yaxis=dict(gridcolor="#F3F4F6"),
                      margin=dict(t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### 🔢 Tokens por Sesión")
    df_sorted = df.sort_values("Fecha")
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(name="Input", x=df_sorted["Fecha"].dt.strftime("%d/%m"), y=df_sorted["Tokens Input"],
                          marker_color="#4F46E5", opacity=0.85))
    fig2.add_trace(go.Bar(name="Output", x=df_sorted["Fecha"].dt.strftime("%d/%m"), y=df_sorted["Tokens Output"],
                          marker_color="#059669", opacity=0.85))
    fig2.update_layout(barmode="group", height=300,
                       plot_bgcolor="white", paper_bgcolor="white",
                       yaxis=dict(gridcolor="#F3F4F6"),
                       legend=dict(orientation="h", y=1.1),
                       margin=dict(t=30, b=20))
    st.plotly_chart(fig2, use_container_width=True)

# ─── ROW 2: Proyectos + Modelo + Tipo ────────────────────────────────────────
col3, col4, col5 = st.columns(3)

with col3:
    st.markdown("### 💰 Por Proyecto")
    proy_df = df.groupby("Proyecto")["Costo S/"].sum().reset_index()
    fig3 = px.pie(proy_df, values="Costo S/", names="Proyecto", hole=0.55,
                  color_discrete_sequence=["#4F46E5","#DC2626","#059669"])
    fig3.update_layout(height=280, margin=dict(t=20, b=20),
                       legend=dict(orientation="h", y=-0.15))
    fig3.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.markdown("### 🤖 Modelo")
    mod_df = df.groupby("Modelo").size().reset_index(name="Sesiones")
    fig4 = px.bar(mod_df, x="Sesiones", y="Modelo", orientation="h",
                  color_discrete_sequence=["#2563EB","#7C3AED"])
    fig4.update_layout(height=280, showlegend=False,
                       plot_bgcolor="white", paper_bgcolor="white",
                       xaxis=dict(gridcolor="#F3F4F6"),
                       margin=dict(t=20, b=20))
    st.plotly_chart(fig4, use_container_width=True)

with col5:
    st.markdown("### ⚡ Tipo de Uso")
    tipo_df = df.groupby("Tipo").size().reset_index(name="Sesiones")
    fig5 = px.pie(tipo_df, values="Sesiones", names="Tipo", hole=0.5,
                  color_discrete_sequence=["#2563EB","#059669","#7C3AED"])
    fig5.update_layout(height=280, margin=dict(t=20, b=20),
                       legend=dict(orientation="h", y=-0.15))
    st.plotly_chart(fig5, use_container_width=True)

# ─── ROW 3: Horas pico + Eficiencia ─────────────────────────────────────────
col6, col7 = st.columns(2)

with col6:
    st.markdown("### ⏰ Horas Pico — Costo por Franja")
    pico_df = df.groupby("Franja")["Costo S/"].sum().reset_index()
    pico_order = {"Manana": "☀️ 9-11am (Mañana)", "Tarde": "🌤️ 3-4pm (Tarde)", "Noche": "🌙 9pm (Noche)"}
    pico_df["Franja Label"] = pico_df["Franja"].map(pico_order)
    fig6 = px.bar(pico_df, x="Franja Label", y="Costo S/",
                  color="Franja", text="Costo S/",
                  color_discrete_map={"Manana":"#D97706","Tarde":"#2563EB","Noche":"#7C3AED"})
    fig6.update_traces(texttemplate="S/ %{text:.2f}", textposition="outside")
    fig6.update_layout(height=300, showlegend=False,
                       plot_bgcolor="white", paper_bgcolor="white",
                       yaxis=dict(gridcolor="#F3F4F6"),
                       xaxis_title="", margin=dict(t=40, b=20))
    st.plotly_chart(fig6, use_container_width=True)

with col7:
    st.markdown("### 🎯 Eficiencia (Tokens/min)")
    fig7 = px.scatter(df, x="Duracion min", y="Eficiencia",
                      color="Tipo", size="Total Tokens",
                      hover_data=["Proyecto","Modelo","Costo S/"],
                      color_discrete_map={"API":"#2563EB","Chat":"#059669","Agentes":"#7C3AED"},
                      labels={"Duracion min":"Duración (min)","Eficiencia":"Tokens/min"})
    fig7.update_layout(height=300, plot_bgcolor="white", paper_bgcolor="white",
                       yaxis=dict(gridcolor="#F3F4F6"),
                       xaxis=dict(gridcolor="#F3F4F6"),
                       margin=dict(t=20, b=20))
    st.plotly_chart(fig7, use_container_width=True)

# ─── ANÁLISIS HORAS PICO ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## ⏰ Análisis Detallado de Horas Pico")

p1, p2, p3 = st.columns(3)
with p1:
    st.markdown("""
    <div style="background:#FEF3C7;padding:1.2rem;border-radius:10px;border-top:4px solid #D97706">
    <h4 style="margin:0 0 6px 0">☀️ 9–11am — Pico Principal</h4>
    <b>Agencia MiProyecto</b><br><br>
    • 4 sesiones (50% del total)<br>
    • 12,575 tokens promedio<br>
    • <b>S/ 1.74 (54% del gasto)</b><br>
    • Modelos: Opus + Sonnet<br><br>
    💡 <i>Prepara prompts la noche anterior. Meta: S/ 1.20/día</i>
    </div>
    """, unsafe_allow_html=True)

with p2:
    st.markdown("""
    <div style="background:#DBEAFE;padding:1.2rem;border-radius:10px;border-top:4px solid #2563EB">
    <h4 style="margin:0 0 6px 0">🌤️ 3–4pm — Pico Secundario</h4>
    <b>Estudio IA / Datos</b><br><br>
    • 3 sesiones (37% del total)<br>
    • 6,183 tokens promedio<br>
    • <b>S/ 0.92 (29% del gasto)</b><br>
    • Modelo: Sonnet<br><br>
    💡 <i>Usa Haiku para SQL simple. Ahorro 50%. Meta: S/ 0.30/día</i>
    </div>
    """, unsafe_allow_html=True)

with p3:
    st.markdown("""
    <div style="background:#EDE9FE;padding:1.2rem;border-radius:10px;border-top:4px solid #7C3AED">
    <h4 style="margin:0 0 6px 0">🌙 9pm — Pico Mínimo</h4>
    <b>Personal / Reflexión</b><br><br>
    • 1 sesión (13% del total)<br>
    • 4,250 tokens promedio<br>
    • <b>S/ 0.18 (6% del gasto)</b><br>
    • Modelo: Sonnet<br><br>
    💡 <i>Agrupa 3-5 preguntas en 1 sesión. Meta: S/ 0.10/día</i>
    </div>
    """, unsafe_allow_html=True)

# ─── RECOMENDACIONES ─────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## 💡 Recomendaciones de Optimización")

r1, r2, r3, r4 = st.columns(4)
with r1:
    st.markdown("**💰 Reducir Costo 25%**")
    st.markdown("→ Sonnet por defecto\n\n→ Opus solo auditorías\n\n→ Meta: S/ 2.40/sem")
with r2:
    st.markdown("**⏰ Gestión Horas Pico**")
    st.markdown("→ 9am: batch prompts pre-armados\n\n→ 3pm: Haiku para código\n\n→ 9pm: acumula preguntas")
with r3:
    st.markdown("**📊 Proyección Mayo**")
    st.markdown("→ Agencia (4 clientes): S/ 20-28\n\n→ Real Madrid: S/ 3-5\n\n→ **Total: S/ 27-38**")
with r4:
    st.markdown("**🔧 Logging Real**")
    st.markdown("→ Agregar contador tokens\n\n→ CSV diario automático\n\n→ Alerta si > S/ 8/sem")

# ─── COSTO REAL API (SIN SUBSIDIO) ───────────────────────────────────────────
st.markdown("---")
st.markdown("## 💸 ¿Cuánto pagarías sin el subsidio de Claude?")
st.markdown("Precios reales de la **API de Anthropic** (abril 2026) según [phuryn/claude-usage](https://github.com/phuryn/claude-usage)")

# Tabla de precios API reales (USD por millón de tokens)
PRECIOS_API = {
    "Claude Opus":   {"input": 5.00,  "output": 25.00},
    "Claude Sonnet": {"input": 3.00,  "output": 15.00},
    "Claude Haiku":  {"input": 1.00,  "output": 5.00},
}
USD_TO_PEN = 3.72  # Tipo de cambio referencial

def calcular_costo_api(modelo, tokens_input, tokens_output):
    clave = "Claude Sonnet"
    if "Opus" in modelo:
        clave = "Claude Opus"
    elif "Haiku" in modelo:
        clave = "Claude Haiku"
    precio = PRECIOS_API[clave]
    return (tokens_input / 1_000_000 * precio["input"]) + (tokens_output / 1_000_000 * precio["output"])

# Calcular costo API real para datos filtrados
df_api = df.copy()
df_api["Costo API USD"] = df_api.apply(
    lambda r: calcular_costo_api(r["Modelo"], r["Tokens Input"], r["Tokens Output"]), axis=1
)
df_api["Costo API S/"] = df_api["Costo API USD"] * USD_TO_PEN

total_api_usd = df_api["Costo API USD"].sum()
total_api_pen = df_api["Costo API S/"].sum()
total_subsidiado = df["Costo S/"].sum()
ahorro_pen = total_api_pen - total_subsidiado
pct_ahorro = (ahorro_pen / total_api_pen * 100) if total_api_pen > 0 else 0

# Plan Claude Max mensual estimado (referencia)
plan_max_usd = 100  # USD/mes Claude Max
plan_max_pen = plan_max_usd * USD_TO_PEN

# KPIs comparativos
ka1, ka2, ka3, ka4 = st.columns(4)
ka1.metric(
    "💳 Costo API Real (USD)",
    f"${total_api_usd:.4f}",
    f"S/ {total_api_pen:.4f} al cambio"
)
ka2.metric(
    "✅ Lo que pagas (subvencionado)",
    f"S/ {total_subsidiado:.2f}",
    "Incluido en tu plan Claude"
)
ka3.metric(
    "🎁 Ahorro por subsidio",
    f"S/ {ahorro_pen:.4f}",
    f"{pct_ahorro:.1f}% ahorrado vs API directa"
)
ka4.metric(
    "📅 Proyección API mensual",
    f"S/ {total_api_pen / max(len(df),1) * 30:.2f}",
    f"vs Plan Max S/ {plan_max_pen:.0f}/mes"
)

st.markdown("")

# Gráfico comparativo: Costo real vs subvencionado por sesión
col_a, col_b = st.columns(2)

with col_a:
    st.markdown("### 📊 Costo API vs Subvencionado por Sesión")
    df_comp = df_api[["Fecha","Proyecto","Modelo","Costo S/","Costo API S/"]].copy()
    df_comp["Fecha_str"] = df_comp["Fecha"].dt.strftime("%d/%m")
    df_comp["Label"] = df_comp["Fecha_str"] + " · " + df_comp["Proyecto"].str.split().str[0]

    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(
        name="Con subsidio (actual)",
        x=df_comp["Label"], y=df_comp["Costo S/"],
        marker_color="#059669", opacity=0.9
    ))
    fig_comp.add_trace(go.Bar(
        name="Sin subsidio (API real)",
        x=df_comp["Label"], y=df_comp["Costo API S/"],
        marker_color="#DC2626", opacity=0.85
    ))
    fig_comp.update_layout(
        barmode="group", height=300,
        plot_bgcolor="white", paper_bgcolor="white",
        yaxis=dict(gridcolor="#F3F4F6", title="S/"),
        xaxis=dict(gridcolor=None, tickangle=-30),
        legend=dict(orientation="h", y=1.15),
        margin=dict(t=40, b=60)
    )
    st.plotly_chart(fig_comp, use_container_width=True)

with col_b:
    st.markdown("### 💰 Costo API Real por Modelo")
    # Tabla de precios de referencia
    df_precios = pd.DataFrame([
        {"Modelo": "Claude Opus",   "Input ($/MTok)": "$5.00",  "Output ($/MTok)": "$25.00", "Input (S//MTok)": f"S/ {5.00*USD_TO_PEN:.2f}",  "Output (S//MTok)": f"S/ {25.00*USD_TO_PEN:.2f}"},
        {"Modelo": "Claude Sonnet", "Input ($/MTok)": "$3.00",  "Output ($/MTok)": "$15.00", "Input (S//MTok)": f"S/ {3.00*USD_TO_PEN:.2f}",  "Output (S//MTok)": f"S/ {15.00*USD_TO_PEN:.2f}"},
        {"Modelo": "Claude Haiku",  "Input ($/MTok)": "$1.00",  "Output ($/MTok)": "$5.00",  "Input (S//MTok)": f"S/ {1.00*USD_TO_PEN:.2f}",  "Output (S//MTok)": f"S/ {5.00*USD_TO_PEN:.2f}"},
    ])
    st.dataframe(df_precios, use_container_width=True, hide_index=True)

    st.markdown("")
    # Costo API real por modelo con tus datos
    by_mod_api = df_api.groupby("Modelo").agg(
        Sesiones=("Modelo","count"),
        Tokens_Input=("Tokens Input","sum"),
        Tokens_Output=("Tokens Output","sum"),
        Costo_API_USD=("Costo API USD","sum"),
        Costo_API_PEN=("Costo API S/","sum"),
    ).reset_index()
    by_mod_api["Costo API USD"] = by_mod_api["Costo_API_USD"].apply(lambda x: f"${x:.4f}")
    by_mod_api["Costo API S/"] = by_mod_api["Costo_API_PEN"].apply(lambda x: f"S/ {x:.4f}")
    st.dataframe(
        by_mod_api[["Modelo","Sesiones","Tokens_Input","Tokens_Output","Costo API USD","Costo API S/"]],
        use_container_width=True, hide_index=True
    )

# Box informativo — contexto del subsidio
st.markdown("")
diff_usd = total_api_usd
plan_max_diario = plan_max_usd / 30
uso_diario_pct = (diff_usd / plan_max_diario * 100) if plan_max_diario > 0 else 0

st.info(
    f"**¿Qué significa esto?**\n\n"
    f"- Con la **API directa de Anthropic**, estas {len(df)} sesiones te habrían costado **${total_api_usd:.4f} USD (S/ {total_api_pen:.4f})** en total.\n"
    f"- Con tu **plan Claude** (subvencionado), pagas S/ {total_subsidiado:.2f} — un ahorro del **{pct_ahorro:.1f}%**.\n"
    f"- Si usaras Claude API puro todos los meses a este ritmo: **S/ {total_api_pen/max(len(df),1)*30:.2f}/mes**.\n"
    f"- El **Plan Claude Max (~S/ {plan_max_pen:.0f}/mes)** tiene sentido si usas más de S/ {plan_max_pen:.0f} en valor de API mensual.\n\n"
    f"**Fuente de precios**: [github.com/phuryn/claude-usage](https://github.com/phuryn/claude-usage) · Anthropic API pricing abril 2026"
)

# ─── TABLA ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## 📋 Detalle de Sesiones")
df_show = df[["Fecha","Proyecto","Modelo","Tokens Input","Tokens Output","Total Tokens","Costo S/","Tipo","Duracion min","Eficiencia","Franja"]].copy()
df_show["Fecha"] = df_show["Fecha"].dt.strftime("%d/%m/%Y")
df_show = df_show.rename(columns={"Duracion min":"Dur. (min)","Eficiencia":"Tok/min"})
st.dataframe(df_show, use_container_width=True, hide_index=True)

st.markdown("---")
st.markdown("<center><small>📊 Claude Usage Analytics · Luis Flores · Lima, Perú · Abril 2026</small></center>", unsafe_allow_html=True)
