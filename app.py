import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(layout='wide', page_title='POMS Pro | Psicología Deportiva', page_icon='🧠')

# --- CSS PERSONALIZADO (Interfaz Premium) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #007bff; color: white; font-weight: bold; }
    .stRadio > div { flex-direction: row; gap: 10px; }
    div[data-testid='stExpander'] { background-color: white; border-radius: 10px; border: 1px solid #ddd; }
    .report-card { 
        background-color: #ffffff; 
        padding: 20px; 
        border-radius: 15px; 
        border-left: 8px solid #007bff; 
        box-shadow: 2px 2px 12px rgba(0,0,0,0.1); 
        margin-bottom: 15px;
        color: #333;
    }
    .factor-title { color: #007bff; font-weight: bold; font-size: 1.2em; }
    </style>
""", unsafe_allow_html=True)

# --- MATRIZ DE INTERVENCIONES ---
MATRIZ_INTERVENCIONES = {
    'Tensión': {'Antes entreno': 'Activación fisiológica y respiración', 'Después entreno': 'Relajación muscular progresiva', 'Antes competición': 'Procesos cognitivos y respiración', 'Después competición': 'Debriefing emocional', 'Descarga': 'Técnicas de visualización', 'Lesión': 'Aceptación y compromiso', 'Otros': 'Atención plena'},
    'Depresión': {'Antes entreno': 'Auto-diálogo positivo', 'Después entreno': 'Refuerzo de logros diarios', 'Antes competición': 'Objetivos de proceso', 'Después competición': 'Análisis no punitivo', 'Descarga': 'Activación conductual', 'Lesión': 'Gestión del dolor', 'Otros': 'Apoyo social'},
    'Cólera': {'Antes entreno': 'Canalización de energía y foco externo', 'Después entreno': 'Tiempo fuera', 'Antes competición': 'Plan de acción', 'Después competición': 'Reestructuración cognitiva', 'Descarga': 'Habilidades de comunicación', 'Lesión': 'Gestión frustración', 'Otros': 'Resolución problemas'},
    'Confusión': {'Antes entreno': 'Clarificación tareas', 'Después entreno': 'Feedback estructurado', 'Antes competición': 'Rutinas rígidas', 'Después competición': 'Orden lógico', 'Descarga': 'Planificación semanal', 'Lesión': 'Educación patología', 'Otros': 'Mapas mentales'},
    'Vigor': {'Antes entreno': 'Anclajes de poder', 'Después entreno': 'Recuperación activa', 'Antes competición': 'Música motivacional y éxito', 'Después competición': 'Celebración esfuerzo', 'Descarga': 'Disfrute lúdico', 'Lesión': 'Mantenimiento identidad', 'Otros': 'Transferencia energía'}
}

FACTORS = {
    'Tensión': [1, 10, 16, 20, 26, 27, 34, 41, 49], 
    'Depresión': [5, 9, 14, 18, 21, 23, 32, 35, 36, 44, 45, 47, 48, 54, 58],
    'Cólera': [2, 11, 12, 17, 24, 31, 33, 39, 42, 43, 52, 53],
    'Vigor': [7, 15, 19, 30, 38, 51, 55, 56],
    'Fatiga': [4, 13, 22, 29, 37, 40, 50],
    'Confusión': [3, 8, 25, 28, 46, 57, 6, 50]
}

ADJETIVOS = ["Tenso", "Enojado", "Agotado", "Infeliz", "Confuso", "Vivaz", "Solitario", "Alerta", "Cansado", "Enojado", "Desanimado", "Malhumorado", "Eficiente", "Indigno", "Lleno de energía", "Indeciso", "Amargado", "Triste", "Alegre", "Ansioso", "Inútil", "Fatigado", "Culpable", "Furioso", "Despistado", "Inquieto", "Nervioso", "Incapaz de concentrarse", "Olvidadizo", "Activo", "Rencoroso", "Aterrado", "Triste", "Optimista", "Desesperado", "Indiferente", "Relajado", "Orgulloso", "Irritado", "Agotado", "Asustado", "Dichoso", "Amable", "Solo", "Inseguro", "Agitado", "Preocupado", "Huraño", "Temeroso", "Agotado", "Vigoroso", "Hostil", "Violento", "Abatido", "Inspirado", "Aturdido", "Tenso", "Infravalorado"]

def get_t_score(raw, factor, gender):
    norms = {'Hombre': {'Tensión': [10, 5], 'Depresión': [12, 7], 'Cólera': [10, 6], 'Vigor': [18, 5], 'Fatiga': [8, 5], 'Confusión': [8, 4]}, 'Mujer': {'Tensión': [11, 5], 'Depresión': [11, 8], 'Cólera': [9, 6], 'Vigor': [17, 5], 'Fatiga': [9, 5], 'Confusión': [9, 4]}}
    m, sd = norms[gender][factor]
    return round(50 + 10 * ((raw - m) / sd), 1)

# --- FRONTEND APP ---
st.title("🧠 POMS Pro Application")
st.markdown("---")

# Fila 1: Datos generales
with st.container():
    c1, c2, c3 = st.columns(3)
    with c1: nombre = st.text_input("Nombre del Deportista", placeholder="Ej. Juan Pérez")
    with c2: genero = st.selectbox("Género", ['Hombre', 'Mujer'])
    with c3: contexto = st.selectbox("Contexto / Momento", ['Antes entreno', 'Después entreno', 'Antes competición', 'Después competición', 'Otros', 'Descarga', 'Lesión'])

st.write("### Cuestionario de Estado de Ánimo")
st.info("Responde según cómo te has sentido en la última semana.")

tabs = st.tabs(["Parte I (1-20)", "Parte II (21-40)", "Parte III (41-58)", "Salud y Estilo de Vida"])
respuestas = []

for i, adj in enumerate(ADJETIVOS):
    target_tab = tabs[0] if i < 20 else tabs[1] if i < 40 else tabs[2]
    with target_tab:
        val = st.radio(f"{i+1}. {adj}", options=[0, 1, 2, 3, 4], 
                       format_func=lambda x: ["Nada", "Un poco", "Moderado", "Bastante", "Muchísimo"][x], 
                       key=f"q_{i}", horizontal=True)
        respuestas.append(val)

with tabs[3]:
    st.write("#### Factores Complementarios")
    sueño = st.select_slider("Calidad de Sueño", options=[0, 1, 2, 3, 4], format_func=lambda x: ["Muy mala", "Mala", "Regular", "Buena", "Excelente"][x])
    dieta = st.select_slider("Calidad de Alimentación", options=[0, 1, 2, 3, 4], format_func=lambda x: ["Muy mala", "Mala", "Regular", "Buena", "Excelente"][x])

if st.button("🚀 FINALIZAR Y ANALIZAR RESULTADOS"):
    if not nombre:
        st.warning("⚠️ Por favor, introduce el nombre para personalizar tu informe.")
    else:
        raw_scores = {f: sum(respuestas[idx-1] for idx in idxs) for f, idxs in FACTORS.items()}
        t_scores = {f: get_t_score(raw_scores[f], f, genero) for f in FACTORS}
        
        st.balloons()
        st.success(f"Informe generado con éxito para {nombre}")

        # Gráfico Profesional
        st.subheader("📊 Perfil Psicológico Actual")
        fig, ax = plt.subplots(figsize=(10, 4))
        colors = ['#007bff' if f != 'Vigor' else '#28a745' for f in t_scores.keys()]
        ax.bar(t_scores.keys(), t_scores.values(), color=colors, alpha=0.7)
        ax.plot(list(t_scores.keys()), list(t_scores.values()), color='#333', marker='o', linewidth=2)
        ax.axhline(50, color='red', linestyle='--', label="Media (T=50)")
        ax.set_ylim(30, 80)
        st.pyplot(fig)

        # Feedback e Informe para descarga
        st.subheader(f"💡 Plan de Acción para {nombre}")
        
        texto_informe = f"INFORME PSICOLÓGICO POMS PRO\n"
        texto_informe += f"Deportista: {nombre}\nFecha: {datetime.date.today()}\nContexto: {contexto}\n\n"
        texto_informe += "--- RESULTADOS (Puntuaciones T) ---\n"
        for f, v in t_scores.items():
            texto_informe += f"{f}: {v}\n"
        
        texto_informe += "\n--- RECOMENDACIONES ---\n"
        
        intervenciones_activas = []
        for f in ['Tensión', 'Depresión', 'Cólera', 'Confusión']:
            if t_scores[f] > 60:
                tecnica = MATRIZ_INTERVENCIONES[f][contexto]
                msg = f"Debido a tu nivel de {f} elevado en la fase de {contexto}, la técnica recomendada es: {tecnica}."
                st.markdown(f"<div class='report-card'><span class='factor-title'>Nivel de {f} elevado</span><br>{msg}</div>", unsafe_allow_html=True)
                texto_informe += f"- {f}: {tecnica}\n"
                intervenciones_activas.append(f)

        if t_scores['Vigor'] < 40:
            tecnica = MATRIZ_INTERVENCIONES['Vigor'][contexto]
            msg = f"Tus niveles de energía están bajos para {contexto}. Estrategia: {tecnica}."
            st.markdown(f"<div class='report-card'><span class='factor-title'>Alerta de Vigor</span><br>{msg}</div>", unsafe_allow_html=True)
            texto_informe += f"- Vigor (Bajo): {tecnica}\n"

        if not intervenciones_activas and t_scores['Vigor'] >= 40:
            st.write(f"✅ ¡Excelente trabajo, {nombre}! Estás en equilibrio.")
            texto_informe += "Perfil en equilibrio psicológico óptimo.\n"

        st.divider()
        
        # BOTÓN DE DESCARGA NATIVO DE STREAMLIT
        st.download_button(
            label="📥 Descargar Informe Clínico (.txt)",
            data=texto_informe,
            file_name=f"Informe_POMS_{nombre}.txt",
            mime="text/plain"
        )

        st.caption("Nota: Este informe es una ayuda automatizada. Para un seguimiento clínico, contacta con tu psicólogo.")
