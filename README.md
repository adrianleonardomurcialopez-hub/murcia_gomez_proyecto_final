# The Empire Vision — Sistema Experto de Asesoría Óptica

Proyecto final de **Inteligencia Artificial II** — Fundación Universitaria Los Libertadores.  
**Autores:** Adrian Murcia y Juan Gómez.

---

## Descripción

**The Empire Vision** es un sistema basado en conocimiento (SBC) con interfaz web interactiva que apoya la asesoría clínica inicial en una óptica. A partir de la fórmula refractiva del paciente (esfera de ojo derecho e izquierdo, adición de cerca), su edad, uso de pantallas, antigüedad del examen y factores de riesgo, el sistema infiere su perfil visual, emite alertas prioritarias de seguridad clínica y sugiere lentes y tratamientos con su respectivo nivel de certeza.

El proyecto separa por completo el conocimiento del dominio, el motor de inferencia y la interfaz de usuario:

- **Base de conocimiento (`src/base_conocimiento.py`):** 16 predicados formalizados en lógica de predicados, 12 reglas de producción (`R1`–`R12`) en tres categorías (clasificación, lentes/tratamientos y seguridad), conversor de fichas a hechos (`armar_hechos`) y 12 expedientes clínicos precargados.
- **Motor de inferencia (`src/motor_inferencia.py`):** encadenamiento hacia adelante agnóstico al dominio con propagación y combinación de factores de certeza, detección de ciclos mediante DFS, validación de reglas, registro de logs, explicación secuencial (`explicar_razonamiento`) y trazabilidad causal hacia atrás (`porque`).
- **Interfaz web (`src/app.py`):** aplicación desarrollada en Streamlit con validación clínica de formularios, carga instantánea de casos de prueba, alertas prioritarias, visualización del perfil visual y módulo interactivo de explicabilidad.

---

## Estructura del proyecto

```text
murcia-gomez-sbc/
├── README.md
├── requirements.txt
├── .gitignore
├── src/
│   ├── base_conocimiento.py     # Predicados, 12 reglas SI-ENTONCES y 12 casos de prueba
│   ├── motor_inferencia.py      # Motor forward chaining, certezas, ciclos y explicaciones
│   ├── app.py                   # Interfaz web en Streamlit (The Empire Vision)
│   └── assets/
│       └── logo.jpg             # Logo institucional usado en el encabezado web
├── docs/
│   ├── documentacion_tecnica.pdf
│   └── manual_usuario.pdf
└── tests/
    └── casos_prueba.md          # Tabla de validación (12 casos + casos de borde)
```

---

## Requisitos previos

- Python **3.8** o superior.
- `pip` actualizado.
- Navegador web moderno (Chrome, Edge, Firefox o Safari).

---

## Instalación

1. Clona el repositorio o descomprime el archivo del proyecto y entra a la carpeta raíz:

```bash
git clone https://github.com/<tu-usuario>/murcia-gomez-sbc.git
cd murcia-gomez-sbc
```

2. Crea y activa un entorno virtual:

```bash
# Crear entorno virtual
python -m venv venv

# Activar en Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Activar en Windows (CMD)
venv\Scripts\activate.bat

# Activar en macOS / Linux
source venv/bin/activate
```

3. Instala las dependencias:

```bash
pip install -r requirements.txt
```

---

## Cómo ejecutar la aplicación

Desde la carpeta raíz del proyecto, ejecuta:

```bash
streamlit run src/app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`.

---

## Casos de prueba y validación

La aplicación trae **12 expedientes precargados** accesibles desde el selector superior de la interfaz (cubriendo desde casos simples como miopía leve hasta alertas urgentes de remisión oftalmológica, un caso sin conclusión y un caso integral de 11 reglas activas).

El detalle completo de cada caso, sus certezas verificadas y los casos de borde se encuentra en [`tests/casos_prueba.md`](tests/casos_prueba.md).

---

## Documentación incluida

- **Documentación técnica:** [`docs/documentacion_tecnica.pdf`](docs/documentacion_tecnica.pdf)
- **Manual de usuario:** [`docs/manual_usuario.pdf`](docs/manual_usuario.pdf)

---

## Video demostrativo

- Enlace al video de demo (opcional / respaldo de sustentación): `[Agregar enlace aquí si aplica]`