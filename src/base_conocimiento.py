"""
base_conocimiento.py
Sistema experto para una óptica - Proyecto final de Inteligencia Artificial II.
Autores: Adrian Murcia y Juan Gómez.

Aquí vive TODO el conocimiento del sistema (predicados, reglas, textos y casos
de prueba). El motor de inferencia (motor_inferencia.py) no sabe nada de óptica:
si se quiere cambiar o agregar una regla, solo se toca este archivo.

Convención: los hechos se escriben en minúscula con guion bajo y siempre hablan
del cliente que se está evaluando (el "x" de la lógica de predicados).
Solo usa la biblioteca estándar de Python (3.8+).
"""

# ---------------------------------------------------------------------------
# 1. PREDICADOS
# ---------------------------------------------------------------------------
# Todos tienen rango {verdadero, falso}. En el código, un hecho presente en el
# conjunto de hechos significa "verdadero".
# Los 16 predicados de la formalización son: 12 observables + 3 derivados
# unarios (miopia, presbicia, fatiga_visual_digital) + el binario
# Recomendar(x, p), que en el código aparece como un hecho rec_* por cada
# producto p (8 productos).
PREDICADOS = {
    # --- Observables (se leen de la ficha del cliente) ---
    "esfera_negativa":   "Algún ojo del cliente tiene esfera <= -0.50 D",
    "dioptria_alta":     "Algún ojo del cliente tiene |esfera| >= 4.00 D",
    "adicion_positiva":  "La fórmula trae adición para cerca >= +0.75 D",
    "edad_mayor_40":     "El cliente tiene 40 años o más",
    "es_nino":           "El cliente tiene 12 años o menos",
    "pantallas_6h":      "El cliente usa pantallas 6 horas o más al día",
    "sintomas_fatiga":   "Siente ardor, dolor de cabeza o borrosidad al final del día",
    "conduce_noche":     "Conduce de noche con frecuencia",
    "trabajo_exterior":  "Pasa buena parte del día al sol",
    "deporte_activo":    "Practica deporte con riesgo de golpes",
    "sintomas_alarma":   "Ve destellos o una 'cortina', perdió visión de golpe o tiene dolor ocular fuerte",
    "formula_vencida":   "El último examen visual fue hace más de 12 meses",
    # --- Derivados (los concluye el sistema) ---
    "miopia":                "El cliente es miope",
    "presbicia":             "El cliente tiene vista cansada (presbicia)",
    "fatiga_visual_digital": "El cliente tiene fatiga visual por uso de pantallas",
    # Recomendar(x, p): un hecho por cada producto p
    "rec_progresivo":             "Recomendar(x, Progresivo)",
    "rec_progresivo_ocupacional": "Recomendar(x, ProgresivoOcupacional)",
    "rec_alto_indice":            "Recomendar(x, AltoIndice)",
    "rec_policarbonato":          "Recomendar(x, Policarbonato)",
    "rec_fotocromatico":          "Recomendar(x, Fotocromatico)",
    "rec_antirreflejo":           "Recomendar(x, Antirreflejo)",
    "rec_remision_urgente":       "Recomendar(x, RemisionUrgente)",
    "rec_examen_previo":          "Recomendar(x, ExamenPrevio)",
}

# Hechos que el sistema puede concluir (sirve para la interfaz y las pruebas)
HECHOS_DERIVADOS = [
    "miopia", "presbicia", "fatiga_visual_digital",
    "rec_progresivo", "rec_progresivo_ocupacional", "rec_alto_indice",
    "rec_policarbonato", "rec_fotocromatico", "rec_antirreflejo",
    "rec_remision_urgente", "rec_examen_previo",
]

# ---------------------------------------------------------------------------
# 2. TEXTOS: descripción legible de cada recomendación
# ---------------------------------------------------------------------------
TEXTOS = {
    "rec_progresivo":             "Lente progresivo (se ve bien de lejos, a media distancia y de cerca)",
    "rec_progresivo_ocupacional": "Lente ocupacional como segundo par, para trabajo en pantalla",
    "rec_alto_indice":            "Lente de alto índice (más delgado y liviano)",
    "rec_policarbonato":          "Lente de policarbonato (resiste golpes, con filtro UV)",
    "rec_fotocromatico":          "Lente fotocromático (se oscurece con el sol)",
    "rec_antirreflejo":           "Antirreflejo (menos deslumbramiento al conducir de noche)",
    "rec_remision_urgente":       "REMISIÓN URGENTE al oftalmólogo, no fabricar lentes todavía",
    "rec_examen_previo":          "Agendar nuevo examen visual, la fórmula está vencida",
}

# ---------------------------------------------------------------------------
# 3. REGLAS (12 reglas, organizadas por categoría)
# ---------------------------------------------------------------------------
CAT_CLASIFICACION = "clasificación"
CAT_LENTES = "lentes y tratamientos"
CAT_SEGURIDAD = "seguridad"


def crear_regla(nombre, categoria, descripcion, condiciones, conclusion, certeza):
    """Arma una regla SI-ENTONCES como diccionario, con su factor de certeza.

    condiciones: lista de hechos que deben cumplirse TODOS (la Y lógica).
    conclusion : el hecho que se agrega cuando la regla se dispara.
    certeza    : factor de certeza de la regla, entre 0 y 1.
    """
    return {
        "nombre": nombre,
        "categoria": categoria,
        "descripcion": descripcion,
        "condiciones": condiciones,
        "conclusion": conclusion,
        "certeza": certeza,
    }


REGLAS = [
    # --- Clasificación (R1 a R3) ---
    crear_regla("R1", CAT_CLASIFICACION, "Esfera negativa indica miopía",
                ["esfera_negativa"], "miopia", 1.00),
    crear_regla("R2", CAT_CLASIFICACION, "Mayor de 40 con adición positiva indica presbicia",
                ["edad_mayor_40", "adicion_positiva"], "presbicia", 0.95),
    crear_regla("R3", CAT_CLASIFICACION, "Muchas horas de pantalla con síntomas indica fatiga visual digital",
                ["pantallas_6h", "sintomas_fatiga"], "fatiga_visual_digital", 0.85),

    # --- Lentes y tratamientos (R4 a R10) ---
    crear_regla("R4", CAT_LENTES, "La presbicia se corrige con lente progresivo",
                ["presbicia"], "rec_progresivo", 0.90),
    crear_regla("R5", CAT_LENTES, "Presbicia con fatiga digital: segundo par ocupacional",
                ["presbicia", "fatiga_visual_digital"], "rec_progresivo_ocupacional", 0.92),
    crear_regla("R6", CAT_LENTES, "Miopía alta: lente de alto índice",
                ["miopia", "dioptria_alta"], "rec_alto_indice", 0.90),
    crear_regla("R7", CAT_LENTES, "Conducción nocturna: antirreflejo",
                ["conduce_noche"], "rec_antirreflejo", 0.90),
    crear_regla("R8", CAT_LENTES, "Trabajo al sol: fotocromático",
                ["trabajo_exterior"], "rec_fotocromatico", 0.85),
    crear_regla("R9", CAT_LENTES, "Niños: policarbonato por resistencia a golpes",
                ["es_nino"], "rec_policarbonato", 0.95),
    crear_regla("R10", CAT_LENTES, "Deporte con riesgo de golpes: policarbonato",
                ["deporte_activo"], "rec_policarbonato", 0.90),

    # --- Seguridad (R11 y R12) ---
    crear_regla("R11", CAT_SEGURIDAD, "Síntomas de alarma: remitir al oftalmólogo antes de vender",
                ["sintomas_alarma"], "rec_remision_urgente", 0.98),
    crear_regla("R12", CAT_SEGURIDAD, "Fórmula de más de 12 meses: nuevo examen antes de fabricar",
                ["formula_vencida"], "rec_examen_previo", 0.95),
]


# ---------------------------------------------------------------------------
# 4. De la ficha del cliente a los hechos iniciales
# ---------------------------------------------------------------------------
# Claves booleanas de la ficha que pasan directo a hechos
CLAVES_BOOLEANAS = ["sintomas_fatiga", "conduce_noche", "trabajo_exterior",
                    "deporte_activo", "sintomas_alarma"]


def armar_hechos(ficha):
    """Pasa la ficha del cliente a un conjunto de hechos.

    ficha = {"edad": int, "esfera": (OD, OI), "adicion": float,
             "horas_pantalla": float, "meses_examen": int,
             "sintomas_fatiga": bool, ... (las claves booleanas son opcionales)}

    Para la esfera basta con que un ojo cumpla (el existe de la formalización):
        EsferaNegativa(x) <=> existe o en {OD, OI}: Esfera(x, o) <= -0.50
        DioptriaAlta(x)   <=> existe o en {OD, OI}: |Esfera(x, o)| >= 4.00
    """
    hechos = set()
    if min(ficha["esfera"]) <= -0.50:
        hechos.add("esfera_negativa")
    if max(abs(e) for e in ficha["esfera"]) >= 4.00:
        hechos.add("dioptria_alta")
    if ficha["adicion"] >= 0.75:
        hechos.add("adicion_positiva")
    if ficha["edad"] >= 40:
        hechos.add("edad_mayor_40")
    if ficha["edad"] <= 12:
        hechos.add("es_nino")
    if ficha["horas_pantalla"] >= 6:
        hechos.add("pantallas_6h")
    if ficha["meses_examen"] > 12:
        hechos.add("formula_vencida")

    for clave in CLAVES_BOOLEANAS:
        if ficha.get(clave, False):
            hechos.add(clave)
    return hechos


# ---------------------------------------------------------------------------
# 5. Casos de prueba precargados
#    Diseñados para cubrir cada regla de forma individual y en combinación.
#    Reglas: R1–R3 (clasificación), R4–R10 (lentes), R11–R12 (seguridad).
# ---------------------------------------------------------------------------
CASOS_PRUEBA = [
    # -----------------------------------------------------------------------
    # Caso 1 — R1: solo miopía leve
    # Activa: R1 → miopia
    # No activa: ninguna recomendación de producto (ni presbicia, ni alto índice)
    # -----------------------------------------------------------------------
    {"id": 1, "nombre": "Luis",
     "descripcion": "25 años, miopía leve en ambos ojos, sin factores adicionales "
                    "(solo debe concluir miopía, sin recomendación de producto)",
     "ficha": {"edad": 25, "esfera": (-1.00, -0.75), "adicion": 0,
               "horas_pantalla": 2, "meses_examen": 4}},

    # -----------------------------------------------------------------------
    # Caso 2 — R2 + R4: presbicia sola → progresivo
    # Activa: R2 → presbicia, R4 → rec_progresivo
    # No activa: R1 (esfera positiva), R3, R5–R12
    # -----------------------------------------------------------------------
    {"id": 2, "nombre": "Elena",
     "descripcion": "48 años, présbita sin miopía ni factores adicionales "
                    "(debe recomendar solo lente progresivo)",
     "ficha": {"edad": 48, "esfera": (0.50, 0.25), "adicion": 1.25,
               "horas_pantalla": 3, "meses_examen": 7}},

    # -----------------------------------------------------------------------
    # Caso 3 — R1 + R2 + R3 + R4 + R5: miopía + presbicia + fatiga digital
    # Activa: R1 → miopia, R2 → presbicia, R3 → fatiga_visual_digital,
    #         R4 → rec_progresivo, R5 → rec_progresivo_ocupacional
    # -----------------------------------------------------------------------
    {"id": 3, "nombre": "Diego",
     "descripcion": "55 años, miope con presbicia, 7 h de pantalla con síntomas de fatiga "
                    "(debe recomendar progresivo + ocupacional como segundo par)",
     "ficha": {"edad": 55, "esfera": (-1.25, -1.00), "adicion": 1.75,
               "horas_pantalla": 7, "meses_examen": 9,
               "sintomas_fatiga": True}},

    # -----------------------------------------------------------------------
    # Caso 4 — R1 + R6: miopía alta → alto índice
    # Activa: R1 → miopia, R6 → rec_alto_indice
    # No activa: presbicia (joven), fatiga, ni otras reglas de seguridad
    # -----------------------------------------------------------------------
    {"id": 4, "nombre": "Clara",
     "descripcion": "30 años, miopía alta en ambos ojos, sin factores adicionales "
                    "(debe recomendar lente de alto índice)",
     "ficha": {"edad": 30, "esfera": (-5.50, -4.75), "adicion": 0,
               "horas_pantalla": 4, "meses_examen": 10}},

    # -----------------------------------------------------------------------
    # Caso 5 — R7: solo conducción nocturna → antirreflejo
    # Activa: R7 → rec_antirreflejo
    # No activa: ninguna de clasificación (esfera casi nula, sin adición)
    # -----------------------------------------------------------------------
    {"id": 5, "nombre": "Tomás",
     "descripcion": "40 años, visión casi perfecta, conduce de noche frecuentemente "
                    "(debe recomendar solo antirreflejo)",
     "ficha": {"edad": 40, "esfera": (-0.25, 0.00), "adicion": 0,
               "horas_pantalla": 2, "meses_examen": 6,
               "conduce_noche": True}},

    # -----------------------------------------------------------------------
    # Caso 6 — R8: solo trabajo exterior → fotocromático
    # Activa: R8 → rec_fotocromatico
    # No activa: ninguna de clasificación
    # -----------------------------------------------------------------------
    {"id": 6, "nombre": "Valentina",
     "descripcion": "33 años, visión normal, trabaja todo el día al sol "
                    "(debe recomendar solo lente fotocromático)",
     "ficha": {"edad": 33, "esfera": (0.00, -0.25), "adicion": 0,
               "horas_pantalla": 1, "meses_examen": 8,
               "trabajo_exterior": True}},

    # -----------------------------------------------------------------------
    # Caso 7 — R9: niño (≤12) → policarbonato por ser niño
    # Activa: R1 → miopia, R9 → rec_policarbonato
    # No activa: R10 (sin deporte), R2 (no tiene adición)
    # -----------------------------------------------------------------------
    {"id": 7, "nombre": "Mateo",
     "descripcion": "10 años, niño con miopía leve, no practica deporte de contacto "
                    "(debe recomendar policarbonato por ser niño)",
     "ficha": {"edad": 10, "esfera": (-1.50, -1.25), "adicion": 0,
               "horas_pantalla": 2, "meses_examen": 5}},

    # -----------------------------------------------------------------------
    # Caso 8 — R10: deporte activo (adulto) → policarbonato
    # Activa: R10 → rec_policarbonato
    # No activa: R9 (es adulta), ni clasificación (sin miopía ni presbicia)
    # -----------------------------------------------------------------------
    {"id": 8, "nombre": "Lucía",
     "descripcion": "27 años, visión normal, practica baloncesto con riesgo de golpes "
                    "(debe recomendar policarbonato por deporte, no por ser niña)",
     "ficha": {"edad": 27, "esfera": (0.00, 0.00), "adicion": 0,
               "horas_pantalla": 2, "meses_examen": 11,
               "deporte_activo": True}},

    # -----------------------------------------------------------------------
    # Caso 9 — R11: síntomas de alarma → remisión urgente
    # Activa: R11 → rec_remision_urgente
    # Verifica que el sistema prioriza la seguridad antes que cualquier producto
    # -----------------------------------------------------------------------
    {"id": 9, "nombre": "Ramón",
     "descripcion": "50 años, ve destellos y perdió visión de un ojo súbitamente "
                    "(debe derivar al oftalmólogo de forma urgente, sin fabricar lentes)",
     "ficha": {"edad": 50, "esfera": (-1.00, -0.75), "adicion": 0,
               "horas_pantalla": 3, "meses_examen": 9,
               "sintomas_alarma": True}},

    # -----------------------------------------------------------------------
    # Caso 10 — R12: fórmula vencida (> 12 meses) → examen previo
    # Activa: R12 → rec_examen_previo
    # No activa: ninguna de alarma ni clasificación especial
    # -----------------------------------------------------------------------
    {"id": 10, "nombre": "Pilar",
     "descripcion": "38 años, miopía leve, último examen hace 15 meses "
                    "(debe pedir nuevo examen antes de fabricar los lentes)",
     "ficha": {"edad": 38, "esfera": (-0.75, -1.00), "adicion": 0,
               "horas_pantalla": 3, "meses_examen": 15}},

    # -----------------------------------------------------------------------
    # Caso 11 — Sin conclusión (caso límite mínimo)
    # No activa: ninguna regla (ni clasificación ni recomendaciones)
    # -----------------------------------------------------------------------
    {"id": 11, "nombre": "Andrea",
     "descripcion": "22 años, visión perfecta, sin factores de riesgo ni síntomas "
                    "(el sistema no debe generar ninguna recomendación)",
     "ficha": {"edad": 22, "esfera": (0.00, 0.00), "adicion": 0,
               "horas_pantalla": 1, "meses_examen": 3}},

    # -----------------------------------------------------------------------
    # Caso 12 — Todas las reglas activas (R1–R12)
    # Activa: R1 → miopia, R2 → presbicia, R3 → fatiga_visual_digital,
    #         R4 → rec_progresivo, R5 → rec_progresivo_ocupacional,
    #         R6 → rec_alto_indice, R7 → rec_antirreflejo,
    #         R8 → rec_fotocromatico, R9/R10 → rec_policarbonato (R9 no aplica),
    #         R10 → rec_policarbonato, R11 → rec_remision_urgente,
    #         R12 → rec_examen_previo
    # -----------------------------------------------------------------------
    {"id": 12, "nombre": "Francisco",
     "descripcion": "60 años, miopía alta con presbicia, 8 h de pantalla con síntomas, "
                    "conduce de noche, trabaja al sol, hace deporte, síntomas de alarma "
                    "y examen hace 16 meses (activa las 12 reglas)",
     "ficha": {"edad": 60, "esfera": (-4.50, -5.00), "adicion": 2.00,
               "horas_pantalla": 8, "meses_examen": 16,
               "sintomas_fatiga": True, "conduce_noche": True, "trabajo_exterior": True,
               "deporte_activo": True, "sintomas_alarma": True}},
]
