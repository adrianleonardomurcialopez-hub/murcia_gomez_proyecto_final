"""
app.py
Interfaz web (Streamlit) del sistema experto para una óptica.
Branding: THE EMPIRE VISION - Luxury Clinical Optometry
Autores: Adrian Murcia y Juan Gómez.
Proyecto final de Inteligencia Artificial II - Fundación Universitaria Los Libertadores.

Ejecutar desde la carpeta raíz del proyecto:
    streamlit run src/app.py
"""

import base64
import logging
import math
import sys
from pathlib import Path

# Configurar path para imports locales
sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st

from base_conocimiento import (CASOS_PRUEBA, CLAVES_BOOLEANAS, HECHOS_DERIVADOS,
                               PREDICADOS, REGLAS, TEXTOS, armar_hechos)
from motor_inferencia import (CicloInfinitoError, encadenamiento_adelante,
                              explicar_razonamiento, porque)

# Configuración del logger
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger("sbc.app")

# ---------------------------------------------------------------------------
# Valores por defecto del formulario y utilidades
# ---------------------------------------------------------------------------
DEFAULTS = {"edad": 30, "esfera_od": 0.0, "esfera_oi": 0.0, "adicion": 0.0,
            "horas": 0.0, "meses": 0, "sel_caso": 0}
DEFAULTS.update({clave: False for clave in CLAVES_BOOLEANAS})

PERFIL = [
    ("miopia", "Miopía (Visión Lejana)", "👁️"),
    ("presbicia", "Presbicia (Visión Próxima)", "📖"),
    ("fatiga_visual_digital", "Fatiga Visual Digital (SVI)", "💻")
]

ICONOS_RECOMENDACIONES = {
    "rec_progresivo": "👓",
    "rec_progresivo_ocupacional": "🖥️",
    "rec_alto_indice": "💎",
    "rec_policarbonato": "🛡️",
    "rec_fotocromatico": "☀️",
    "rec_antirreflejo": "🚗",
    "rec_remision_urgente": "🚨",
    "rec_examen_previo": "📅",
}

ETIQUETAS_BOOLEANAS = {
    "sintomas_fatiga": "Fatiga visual o cefalea tras jornadas frente a pantallas",
    "conduce_noche": "Conducción nocturna habitual (deslumbramiento por faros)",
    "trabajo_exterior": "Exposición solar continua o trabajo prolongado en exteriores",
    "deporte_activo": "Práctica de deportes o actividades con riesgo de impacto ocular",
    "sintomas_alarma": "Destellos, miodesopsias súbitas, pérdida de campo visual o dolor agudo",
}


def cargar_logo_b64():
    """Carga el logo institucional en base64 para renderizado HTML fluido."""
    logo_path = Path(__file__).resolve().parent / "assets" / "logo.jpg"
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""


def nivel_certeza(valor):
    """Calificación cualitativa del factor de certeza."""
    valor = round(valor, 3)
    if valor >= 0.90:
        return "Certeza Alta"
    if valor >= 0.75:
        return "Certeza Moderada"
    return "Certeza Preliminar"


def es_numero(valor):
    """True si es un número real finito."""
    return isinstance(valor, (int, float)) and not isinstance(valor, bool) and math.isfinite(valor)


def validar_ficha(ficha):
    """Validación exhaustiva de los parámetros de entrada del paciente."""
    errores = []

    edad = ficha["edad"]
    if not es_numero(edad) or edad != int(edad):
        errores.append("Edad: Ingrese un valor numérico entero.")
    elif not 0 <= edad <= 120:
        errores.append("Edad: El rango clínico admitido es de 0 a 120 años.")

    for nombre, valor in (("Esfera Ojo Derecho (OD)", ficha["esfera"][0]), 
                          ("Esfera Ojo Izquierdo (OI)", ficha["esfera"][1])):
        if not es_numero(valor):
            errores.append(f"{nombre}: Ingrese un valor refractivo válido (ej. -2.00).")
        elif not -20.0 <= valor <= 20.0:
            errores.append(f"{nombre}: Debe ubicarse en el intervalo clínico [-20.00, +20.00] D.")

    adicion = ficha["adicion"]
    if not es_numero(adicion):
        errores.append("Adición de cerca: Ingrese un valor numérico (0.00 si no aplica).")
    elif not 0.0 <= adicion <= 4.0:
        errores.append("Adición de cerca: El rango estándar es de 0.00 a +4.00 D.")

    horas = ficha["horas_pantalla"]
    if not es_numero(horas):
        errores.append("Horas de pantalla: Ingrese un número válido de horas diarias.")
    elif not 0 <= horas <= 24:
        errores.append("Horas de pantalla: Debe situarse entre 0 y 24 horas al día.")

    meses = ficha["meses_examen"]
    if not es_numero(meses) or meses != int(meses):
        errores.append("Meses desde el último examen: Ingrese un número entero de meses.")
    elif meses < 0:
        errores.append("Meses desde el último examen: No puede ser un valor negativo.")

    return errores


def ficha_desde_estado():
    """Genera el diccionario de la ficha a partir del estado de la sesión."""
    estado = st.session_state
    edad, meses = estado["edad"], estado["meses"]
    ficha = {
        "edad": int(edad) if es_numero(edad) and edad == int(edad) else edad,
        "esfera": (estado["esfera_od"], estado["esfera_oi"]),
        "adicion": estado["adicion"],
        "horas_pantalla": estado["horas"],
        "meses_examen": int(meses) if es_numero(meses) and meses == int(meses) else meses,
    }
    for clave in CLAVES_BOOLEANAS:
        ficha[clave] = bool(estado.get(clave, False))
    return ficha


# ---------------------------------------------------------------------------
# Callbacks del ciclo de vida
# ---------------------------------------------------------------------------
def borrar_resultados():
    st.session_state.pop("resultado", None)
    st.session_state.pop("porque_hecho", None)


def cargar_caso():
    """Carga de forma instantánea el caso clínico seleccionado y efectúa el diagnóstico."""
    id_caso = st.session_state.get("sel_caso", 0)
    if id_caso == 0:
        st.session_state["aviso"] = ("warning", "Por favor, seleccione un expediente clínico de la lista.")
        return

    caso = next((c for c in CASOS_PRUEBA if c["id"] == id_caso), None)
    if not caso:
        return

    ficha = caso["ficha"]
    st.session_state["edad"] = int(ficha["edad"])
    st.session_state["esfera_od"] = float(ficha["esfera"][0])
    st.session_state["esfera_oi"] = float(ficha["esfera"][1])
    st.session_state["adicion"] = float(ficha["adicion"])
    st.session_state["horas"] = float(ficha["horas_pantalla"])
    st.session_state["meses"] = int(ficha["meses_examen"])
    for clave in CLAVES_BOOLEANAS:
        st.session_state[clave] = bool(ficha.get(clave, False))

    # Diagnóstico automático inmediato
    try:
        inicial = armar_hechos(ficha)
        resultado = encadenamiento_adelante(REGLAS, inicial)
        st.session_state["resultado"] = {"inicial": inicial, "resultado": resultado}
        st.session_state.pop("porque_hecho", None)
        st.session_state["aviso"] = (
            "success",
            f"Expediente #{caso['id']} ({caso['nombre']}) cargado con éxito. Diagnóstico procesado."
        )
    except Exception as error:
        logger.exception("Error al evaluar el caso clínico")
        borrar_resultados()
        st.session_state["aviso"] = ("error", f"Error en la inferencia clínica: {error}")


def limpiar_formulario():
    """Restablece los campos a sus valores de inicio."""
    for clave, valor in DEFAULTS.items():
        st.session_state[clave] = valor
    borrar_resultados()
    st.session_state["aviso"] = ("info", "Expediente restablecido a parámetros iniciales.")


def pedir_porque():
    st.session_state["porque_hecho"] = st.session_state["sel_conclusion"]


def borrar_porque():
    st.session_state.pop("porque_hecho", None)


# ---------------------------------------------------------------------------
# Estilos CSS - Tema THE EMPIRE VISION (Navy & Imperial Gold)
# ---------------------------------------------------------------------------
def inyectar_estilos():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

    /* Variables de diseño Imperial */
    :root {
        --empire-navy-dark: #050e18;
        --empire-navy: #091b2c;
        --empire-navy-light: #0f273e;
        --empire-gold: #d4af37;
        --empire-gold-light: #f5df88;
        --empire-gold-dark: #aa841c;
        --empire-text: #f1f5f9;
        --empire-muted: #94a3b8;
    }

    /* Fondo principal y tipografía general */
    .stApp {
        background: radial-gradient(circle at top right, #0d263f 0%, #061320 60%, #030a11 100%);
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: var(--empire-text);
    }

    /* Hero Header */
    .empire-header {
        display: flex;
        align-items: center;
        gap: 24px;
        padding: 24px 30px;
        background: linear-gradient(135deg, rgba(15, 39, 62, 0.75) 0%, rgba(9, 27, 44, 0.90) 100%);
        border: 1px solid rgba(212, 175, 55, 0.35);
        border-radius: 16px;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5), 0 0 25px -5px rgba(212, 175, 55, 0.15);
        margin-bottom: 28px;
    }

    .empire-logo-img {
        width: 105px;
        height: 105px;
        object-fit: contain;
        border-radius: 14px;
        border: 2px solid rgba(212, 175, 55, 0.6);
        box-shadow: 0 0 20px rgba(212, 175, 55, 0.25);
    }

    .empire-title {
        font-family: 'Cinzel', serif;
        font-size: 2.3rem;
        font-weight: 800;
        letter-spacing: 2px;
        background: linear-gradient(135deg, #f9e79f 0%, #d4af37 50%, #aa841c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        line-height: 1.1;
    }

    .empire-subtitle {
        color: #cbd5e1;
        font-size: 0.95rem;
        font-weight: 400;
        letter-spacing: 0.5px;
        margin-top: 6px;
        margin-bottom: 8px;
    }

    .empire-badge {
        display: inline-block;
        background: rgba(212, 175, 55, 0.12);
        color: var(--empire-gold-light);
        border: 1px solid rgba(212, 175, 55, 0.35);
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    /* Tarjetas generales de la interfaz */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(11, 29, 47, 0.65) !important;
        border: 1px solid rgba(212, 175, 55, 0.22) !important;
        border-radius: 14px !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3) !important;
        backdrop-filter: blur(8px) !important;
    }

    /* Títulos de sección */
    h2, h3, .stSubheader {
        font-family: 'Cinzel', serif !important;
        color: #fce79a !important;
        letter-spacing: 0.8px !important;
        font-weight: 700 !important;
    }

    /* Botón Principal (Ejecutar diagnóstico) */
    button[kind="primary"] {
        background: linear-gradient(135deg, #d4af37 0%, #aa841c 100%) !important;
        color: #071523 !important;
        font-weight: 700 !important;
        font-size: 0.98rem !important;
        border: none !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.35) !important;
        transition: all 0.3s ease !important;
        letter-spacing: 0.5px !important;
    }

    button[kind="primary"]:hover {
        background: linear-gradient(135deg, #f5df88 0%, #c49925 100%) !important;
        box-shadow: 0 6px 20px rgba(212, 175, 55, 0.55) !important;
        transform: translateY(-1px);
    }

    /* Botón Secundario (Limpiar / Cargar) */
    button[kind="secondary"] {
        background: rgba(15, 39, 62, 0.6) !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(212, 175, 55, 0.4) !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }

    button[kind="secondary"]:hover {
        background: rgba(212, 175, 55, 0.15) !important;
        border-color: var(--empire-gold) !important;
        color: #ffffff !important;
    }

    /* Tarjetas de Perfil Visual */
    .profile-card {
        padding: 16px;
        border-radius: 12px;
        background: rgba(15, 35, 56, 0.55);
        border: 1px solid rgba(212, 175, 55, 0.2);
        margin-bottom: 12px;
        text-align: center;
    }

    .profile-title {
        font-size: 0.92rem;
        font-weight: 600;
        color: #cbd5e1;
        margin-bottom: 8px;
    }

    .status-pill-ok {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.4);
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.8rem;
        display: inline-block;
    }

    .status-pill-none {
        background: rgba(148, 163, 184, 0.1);
        color: #94a3b8;
        border: 1px solid rgba(148, 163, 184, 0.25);
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 500;
        font-size: 0.8rem;
        display: inline-block;
    }

    /* Barras de progreso doradas */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #aa841c 0%, #d4af37 100%) !important;
    }

    /* Cajas de código y explicaciones */
    .stCodeBlock, pre {
        background: #040c14 !important;
        border: 1px solid rgba(212, 175, 55, 0.25) !important;
        border-radius: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Encabezado Institucional
# ---------------------------------------------------------------------------
def render_header():
    logo_b64 = cargar_logo_b64()
    if logo_b64:
        img_html = f'<img src="data:image/jpeg;base64,{logo_b64}" class="empire-logo-img" alt="The Empire Vision">'
    else:
        img_html = '<div style="font-size: 3rem;">🦁</div>'

    st.markdown(f"""
    <div class="empire-header">
        {img_html}
        <div style="flex-grow: 1;">
            <div class="empire-title">THE EMPIRE VISION</div>
            <div class="empire-subtitle">Sistema Clínico Experto de Prescripción Óptica & Asesoría Oftálmica</div>
            <span class="empire-badge">🏛️ Fundación Universitaria Los Libertadores</span>
            <span class="empire-badge" style="margin-left: 6px;">IA II • Adrian Murcia & Juan Gómez</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Sección 1: Expediente Clínico y Datos del Paciente
# ---------------------------------------------------------------------------
def seccion_entrada():
    st.subheader("1. Expediente Clínico del Paciente")
    st.caption("Seleccione un expediente precargado o introduzca los datos refractivos y sintomatológicos de forma manual.")

    # Selector de casos clínicos
    col_caso, col_boton = st.columns([3, 1])
    with col_caso:
        _casos_por_id = {c["id"]: c for c in CASOS_PRUEBA}
        st.selectbox(
            "Expediente clínico precargado (banco de pruebas)",
            [0] + [c["id"] for c in CASOS_PRUEBA],
            key="sel_caso",
            format_func=lambda i, _m=_casos_por_id: "— Seleccionar expediente de prueba —" if i == 0 else
            f"Expediente #{_m[i]['id']}: {_m[i]['nombre']} ({_m[i]['descripcion'][:60]}...)",
            on_change=cargar_caso,
            help="Al seleccionar un caso, se carga y se evalúa el diagnóstico de forma automática."
        )
    with col_boton:
        st.write("")
        st.button("⚡ Cargar Expediente", key="btn_cargar", on_click=cargar_caso, use_container_width=True)

    if st.session_state["sel_caso"] != 0:
        caso_actual = _casos_por_id[st.session_state["sel_caso"]]
        st.info(f"📋 **Resumen del caso seleccionado:** {caso_actual['descripcion']}")

    # Formulario de parámetros clínicos
    with st.container(border=True):
        st.markdown("##### 🔬 Parámetros de Refracción y Consulta")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.number_input("Edad del paciente (años)", key="edad", step=1,
                            help="Edad cronológica. Clínicamente define infancia (<=12) y presbicia (>=40).")
            st.number_input("Meses desde la última refracción", key="meses", step=1,
                            help="Tiempo transcurrido. Fórmulas con más de 12 meses se consideran vencidas.")
        with col2:
            st.number_input("Esfera Ojo Derecho (OD) [Dioptrías]", key="esfera_od", step=0.25, format="%.2f",
                            help="Potencia esférica del ojo derecho. Valores negativos indican miopía.")
            st.number_input("Esfera Ojo Izquierdo (OI) [Dioptrías]", key="esfera_oi", step=0.25, format="%.2f",
                            help="Potencia esférica del ojo izquierdo. Valores negativos indican miopía.")
        with col3:
            st.number_input("Adición para cerca (ADD) [Dioptrías]", key="adicion", step=0.25, format="%.2f",
                            help="Potencia adicional para lectura/visión próxima. 0.00 si no aplica.")
            st.number_input("Exposición a pantallas (horas/día)", key="horas", step=0.5, format="%.1f",
                            help="Promedio diario de uso de dispositivos electrónicos.")

        st.markdown("##### 🩺 Antecedentes, Hábitos y Factores de Riesgo")
        izq, der = st.columns(2)
        for idx, clave in enumerate(CLAVES_BOOLEANAS):
            etiqueta = ETIQUETAS_BOOLEANAS.get(clave, PREDICADOS[clave])
            with (izq if idx % 2 == 0 else der):
                st.checkbox(etiqueta, key=clave)

    # Botonera de acciones
    col_ejecutar, col_limpiar, _ = st.columns([1.5, 1, 2])
    with col_ejecutar:
        ejecutar = st.button("🔮 Ejecutar Diagnóstico Clínico", key="btn_ejecutar", type="primary", use_container_width=True)
    with col_limpiar:
        st.button("🧹 Restablecer", key="btn_limpiar", on_click=limpiar_formulario, use_container_width=True)

    if ejecutar:
        ejecutar_diagnostico()


# ---------------------------------------------------------------------------
# Ejecución del Motor de Inferencia
# ---------------------------------------------------------------------------
def ejecutar_diagnostico():
    """Valida los parámetros de entrada y activa el motor de encadenamiento hacia adelante."""
    ficha = ficha_desde_estado()
    errores = validar_ficha(ficha)
    if errores:
        borrar_resultados()
        st.error("⚠️ Parámetros no válidos detectados. Por favor revise los siguientes campos:")
        for err in errores:
            st.markdown(f"- {err}")
        return

    with st.spinner("Procesando inferencia experta con encadenamiento hacia adelante..."):
        try:
            inicial = armar_hechos(ficha)
            resultado = encadenamiento_adelante(REGLAS, inicial)
        except (CicloInfinitoError, ValueError) as error:
            logger.exception("Fallo en la inferencia")
            borrar_resultados()
            st.error(f"Error crítico en el motor de inferencia: {error}")
            return

    st.session_state["resultado"] = {"inicial": inicial, "resultado": resultado}
    st.session_state.pop("porque_hecho", None)


# ---------------------------------------------------------------------------
# Sección 2: Resultados y Recomendaciones Oftálmicas
# ---------------------------------------------------------------------------
def seccion_resultados(datos):
    inicial, res = datos["inicial"], datos["resultado"]
    hechos, certeza = res.hechos, res.certeza

    st.subheader("2. Conclusiones y Recomendaciones Especializadas")

    # Banner de resumen de diagnóstico
    if res.reglas_aplicadas:
        st.success(
            f"🎯 **Diagnóstico Clínico Completado:** Se dedujeron con éxito los parámetros del paciente aplicando "
            f"**{len(res.reglas_aplicadas)} regla(s) clínicas** con propagación de factores de certeza."
        )
    else:
        st.info(
            "✅ **Evaluación Visual Estándar:** No se identificaron anomalías refractivas complejas, patologías "
            "ni condiciones de riesgo que ameriten tratamientos especializados."
        )

    # Alertas Médicas Prioritarias (Seguridad del Paciente)
    if "rec_remision_urgente" in hechos:
        st.error(
            f"🚨 **ALERTA CLÍNICA MÁXIMA — REMISIÓN URGENTE AL OFTALMÓLOGO** (Certeza: {certeza['rec_remision_urgente']:.1%})\n\n"
            "El paciente refiere síntomas de alarma visual compatibles con compromiso retiniano o neurológico. "
            "**Se suspende de inmediato la manufactura de lentes correctivos** hasta contar con valoración médica integral."
        )

    if "rec_examen_previo" in hechos:
        st.warning(
            f"⚠️ **REVALIDACIÓN REQUERIDA — FÓRMULA ÓPTICA VENCIDA** (Certeza: {certeza['rec_examen_previo']:.1%})\n\n"
            "El último examen visual supera los 12 meses de antigüedad. Se recomienda realizar una refracción "
            "actualizada antes de autorizar la confección definitiva de los cristales."
        )

    # Perfil Refractivo Detectado
    st.markdown("#### 👁️ Perfil Visual Diagnosticado")
    cols = st.columns(3)
    for col, (hecho, nombre, icono) in zip(cols, PERFIL):
        with col, st.container(border=True):
            st.markdown(f"**{icono} {nombre}**")
            if hecho in hechos:
                cert = certeza[hecho]
                st.markdown(f"<span class='status-pill-ok'>✓ Detectada ({cert:.1%})</span>", unsafe_allow_html=True)
                st.progress(min(float(cert), 1.0), text=f"{nivel_certeza(cert)}")
            else:
                st.markdown("<span class='status-pill-none'>— No detectada</span>", unsafe_allow_html=True)
                st.caption("Condición no identificada con los datos actuales.")

    # Recomendación de Lentes y Tratamientos
    st.markdown("#### 💎 Prescripción de Lentes y Tratamientos Sugeridos")
    recomendaciones = sorted((h for h in hechos if h.startswith("rec_") and h not in ("rec_remision_urgente", "rec_examen_previo")),
                             key=lambda h: -certeza[h])

    if not recomendaciones:
        with st.container(border=True):
            st.markdown("👓 **Lente Monofocal Convencional**")
            st.caption("La fórmula del paciente es estándar. Se aconseja un lente monofocal básico de corrección o descanso.")
    else:
        for hecho in recomendaciones:
            icono = ICONOS_RECOMENDACIONES.get(hecho, "✨")
            texto_desc = TEXTOS.get(hecho, hecho)
            cert = certeza[hecho]
            with st.container(border=True):
                col_icon, col_text = st.columns([1, 11])
                with col_icon:
                    st.markdown(f"<div style='font-size: 2.2rem; text-align: center; padding-top: 5px;'>{icono}</div>", unsafe_allow_html=True)
                with col_text:
                    st.markdown(f"**{texto_desc}**")
                    st.progress(min(float(cert), 1.0),
                                text=f"Factor de Certeza: {cert:.1%} ({nivel_certeza(cert)})")

    # Módulo de explicabilidad
    seccion_explicacion(inicial, res)


# ---------------------------------------------------------------------------
# Sección 3: Auditoría y Explicabilidad del Razonamiento
# ---------------------------------------------------------------------------
NOMBRES_HECHOS = {
    "miopia": "👁️ Miopía",
    "presbicia": "📖 Presbicia (visión cercana)",
    "fatiga_visual_digital": "💻 Fatiga visual digital (SVI)",
    "rec_progresivo": "👓 Lente progresivo",
    "rec_progresivo_ocupacional": "🖥️ Lente ocupacional (pantallas)",
    "rec_alto_indice": "💎 Lente de alto índice",
    "rec_policarbonato": "🛡️ Lente de policarbonato",
    "rec_fotocromatico": "☀️ Lente fotocromático",
    "rec_antirreflejo": "🚗 Filtro antirreflejo",
    "rec_remision_urgente": "🚨 Remisión urgente al oftalmólogo",
    "rec_examen_previo": "📅 Nuevo examen visual (fórmula vencida)",
}


def seccion_explicacion(inicial, res):
    st.subheader("3. Trazabilidad y Explicabilidad del Razonamiento")
    st.caption("Verificación paso a paso del proceso de inferencia y justificación clínica de las decisiones.")

    with st.expander("🔍 Ver hechos clínicos iniciales y reglas aplicadas", expanded=True):
        st.markdown("**1. Hechos Clínicos Extraídos de la Ficha del Paciente:**")
        if inicial:
            tags = " &nbsp;|&nbsp; ".join([f"`{h}`" for h in sorted(inicial)])
            st.markdown(f"🩺 {tags}")
        else:
            st.caption("Ningún hecho clínico inicial derivado (parámetros neutros).")

        st.markdown("**2. Cadena de Deducción en Orden de Disparo:**")
        st.code(explicar_razonamiento(res.reglas_aplicadas, res.certeza), language=None)

    st.markdown("#### ❓ Justificación Causal Dinámica: ¿Por qué se llegó a esta conclusión?")
    st.caption("Este árbol de justificación se actualiza automáticamente según las conclusiones derivadas para este paciente:")

    # Clasificar y ordenar: primero las conclusiones obtenidas para este paciente (por mayor certeza)
    concluidos = [h for h in HECHOS_DERIVADOS if h in res.origen]
    concluidos.sort(key=lambda h: -res.certeza.get(h, 0.0))
    no_concluidos = [h for h in HECHOS_DERIVADOS if h not in res.origen]

    opciones = concluidos + no_concluidos if concluidos else HECHOS_DERIVADOS

    def formatear_opcion(h):
        nombre_legible = NOMBRES_HECHOS.get(h, h)
        if h in res.origen:
            return f"✓ {nombre_legible} — CONCLUIDO (Certeza: {res.certeza[h]:.1%})"
        return f"✗ {nombre_legible} — No derivado"

    # Clave dinámica para reiniciar el selector automáticamente al cambiar de paciente
    clave_selector = f"sel_conclusion_p_{st.session_state.get('sel_caso', 0)}_{len(res.reglas_aplicadas)}"

    hecho_seleccionado = st.selectbox(
        "Seleccione cualquier conclusión o diagnóstico para auditar su árbol causal hacia atrás:",
        opciones,
        index=0,
        key=clave_selector,
        format_func=formatear_opcion,
        help="Muestra la cadena causal hacia atrás (backward) que justifica por qué se recomendó o descartó."
    )

    if hecho_seleccionado:
        if hecho_seleccionado in res.origen:
            st.success(
                f"📌 **Árbol Causal para «{NOMBRES_HECHOS.get(hecho_seleccionado, hecho_seleccionado)}»** "
                f"— Certeza Final: **{res.certeza[hecho_seleccionado]:.1%}**"
            )
        else:
            st.warning(
                f"ℹ️ El hecho **«{NOMBRES_HECHOS.get(hecho_seleccionado, hecho_seleccionado)}»** "
                "no fue derivado porque no se cumplieron las condiciones de sus reglas para este paciente."
            )
        st.code(porque(hecho_seleccionado, inicial, res.reglas_aplicadas, res.origen, res.certeza), language=None)


# ---------------------------------------------------------------------------
# Punto de Entrada Principal
# ---------------------------------------------------------------------------
def main():
    st.set_page_config(
        page_title="THE EMPIRE VISION | Sistema Clínico Experto",
        page_icon="🦁",
        layout="wide"
    )

    inyectar_estilos()

    for clave, valor in DEFAULTS.items():
        st.session_state.setdefault(clave, valor)

    render_header()

    # Aviso flotante de interacción previa
    aviso = st.session_state.pop("aviso", None)
    if aviso:
        getattr(st, aviso[0])(aviso[1])

    seccion_entrada()

    datos = st.session_state.get("resultado")
    if datos:
        seccion_resultados(datos)


main()
