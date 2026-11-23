"""
motor_inferencia.py
Motor de encadenamiento hacia adelante con factores de certeza.
Autores: Adrian Murcia y Juan Gómez.

No depende de ninguna biblioteca externa ni del dominio: recibe una lista de
reglas (diccionarios con nombre, condiciones, conclusion y certeza) y un
conjunto de hechos iniciales, y devuelve lo que se pudo concluir.
Las funciones de explicación RETORNAN texto (no usan print), para que la
interfaz web decida cómo mostrarlo.
"""

import logging
from typing import NamedTuple

# Logger del módulo. Con NullHandler no imprime nada a menos que quien use el
# motor (por ejemplo app.py) configure logging.
logger = logging.getLogger("sbc.motor")
logger.addHandler(logging.NullHandler())


class CicloInfinitoError(RuntimeError):
    """Se superó el máximo de iteraciones permitido: el motor no terminaba."""


class ResultadoInferencia(NamedTuple):
    """Resultado del encadenamiento. Se puede desempaquetar como una tupla:
        hechos, origen, certeza, reglas_aplicadas = encadenamiento_adelante(...)
    """
    hechos: set              # hechos iniciales + todo lo concluido
    origen: dict             # {hecho: [reglas que lo produjeron]}
    certeza: dict            # {hecho: factor de certeza}
    reglas_aplicadas: list   # reglas en el orden en que se dispararon


# ---------------------------------------------------------------------------
# Utilidades sobre reglas
# ---------------------------------------------------------------------------
def se_cumple(regla, hechos):
    """True si TODAS las condiciones de la regla están en los hechos."""
    for condicion in regla["condiciones"]:
        if condicion not in hechos:
            return False
    return True


def formatear_regla(regla):
    """Devuelve la regla en formato SI-ENTONCES (texto)."""
    condiciones = " Y ".join(regla["condiciones"])
    return (f'{regla["nombre"]}: SI {condiciones} ENTONCES {regla["conclusion"]} '
            f'(certeza {regla["certeza"]:.2f})')


def _validar_base(base_conocimiento):
    """Revisa que las reglas tengan la forma esperada, para fallar con un
    mensaje claro y no con un KeyError en medio de la inferencia."""
    nombres = set()
    for regla in base_conocimiento:
        for clave in ("nombre", "condiciones", "conclusion", "certeza"):
            if clave not in regla:
                raise ValueError(f"A una regla le falta la clave '{clave}': {regla}")
        if regla["nombre"] in nombres:
            raise ValueError(f"Nombre de regla repetido: {regla['nombre']}")
        nombres.add(regla["nombre"])
        if not 0 <= regla["certeza"] <= 1:
            raise ValueError(f"La certeza de {regla['nombre']} debe estar entre 0 y 1")
        if not regla["condiciones"]:
            raise ValueError(f"La regla {regla['nombre']} no tiene condiciones")


# ---------------------------------------------------------------------------
# Detección de ciclos
# ---------------------------------------------------------------------------
def detectar_ciclos(base_conocimiento):
    """Busca ciclos en las dependencias entre reglas (A lleva a B y B lleva a A).

    Construye un grafo con una arista condición -> conclusión por cada regla y
    lo recorre en profundidad. Devuelve una lista de ciclos, cada uno como lista
    de hechos, por ejemplo ['a', 'b', 'a']. Si no hay ciclos devuelve [].
    """
    grafo = {}
    for regla in base_conocimiento:
        for condicion in regla["condiciones"]:
            grafo.setdefault(condicion, set()).add(regla["conclusion"])

    ciclos = []
    estado = {}   # 1 = está en la ruta actual, 2 = ya terminó de visitarse
    ruta = []

    def visitar(nodo):
        estado[nodo] = 1
        ruta.append(nodo)
        for siguiente in sorted(grafo.get(nodo, ())):
            if estado.get(siguiente) == 1:
                ciclos.append(ruta[ruta.index(siguiente):] + [siguiente])
            elif siguiente not in estado:
                visitar(siguiente)
        ruta.pop()
        estado[nodo] = 2

    for nodo in sorted(grafo):
        if nodo not in estado:
            visitar(nodo)
    return ciclos


# ---------------------------------------------------------------------------
# Encadenamiento hacia adelante
# ---------------------------------------------------------------------------
def encadenamiento_adelante(base_conocimiento, hechos_iniciales, max_iteraciones=None):
    """Motor de encadenamiento hacia adelante con factores de certeza.

    Repite pasadas por las reglas mientras se dispare alguna regla nueva.

    Certeza:
      1. Al disparar una regla: certeza = certeza_regla * min(certeza de las condiciones).
         Los hechos que vienen del cliente valen 1.0.
      2. Si otra regla llega a un hecho que ya existe, se combinan:
         nueva = actual + aplicada * (1 - actual)

    Protección contra ciclos infinitos (dos controles):
      * Cada regla se dispara a lo sumo UNA vez (conjunto 'disparadas').
      * Tope de pasadas: como cada pasada que avanza dispara al menos una regla,
        con N reglas hacen falta a lo sumo N pasadas con cambios + 1 final sin
        cambios. Si se supera ese tope se lanza CicloInfinitoError.

    Caso sin conclusión: si no se dispara ninguna regla, retorna normalmente con
    'origen' vacío y 'reglas_aplicadas' vacía (no es un error).

    Retorna un ResultadoInferencia (hechos, origen, certeza, reglas_aplicadas).
    """
    _validar_base(base_conocimiento)

    hechos = set(hechos_iniciales)
    certeza = {h: 1.0 for h in hechos}
    origen = {}
    reglas_aplicadas = []
    disparadas = set()

    limite = max_iteraciones if max_iteraciones is not None else len(base_conocimiento) + 1

    ciclos = detectar_ciclos(base_conocimiento)
    if ciclos:
        logger.warning("La base de conocimiento tiene ciclos entre reglas: %s "
                       "(el motor termina igual porque cada regla se dispara una sola vez)", ciclos)

    logger.info("Inicio de inferencia: %d reglas, hechos iniciales = %s",
                len(base_conocimiento), sorted(hechos))

    iteracion = 0
    hubo_cambios = True
    while hubo_cambios:
        iteracion += 1
        if iteracion > limite:
            logger.error("Se superó el máximo de %d iteraciones", limite)
            raise CicloInfinitoError(
                f"Se superó el máximo de {limite} iteraciones: posible ciclo infinito.")
        hubo_cambios = False
        logger.debug("Pasada %d", iteracion)

        for regla in base_conocimiento:
            if regla["nombre"] in disparadas:
                continue
            if not se_cumple(regla, hechos):
                continue

            hecho = regla["conclusion"]
            minima = min(certeza[c] for c in regla["condiciones"])
            nueva = regla["certeza"] * minima
            if hecho in hechos:
                combinada = certeza[hecho] + nueva * (1 - certeza[hecho])
                logger.info("Pasada %d: se dispara %s -> %s ya existía (%.3f), se combina con %.3f = %.3f",
                            iteracion, regla["nombre"], hecho, certeza[hecho], nueva, combinada)
                certeza[hecho] = combinada
            else:
                certeza[hecho] = nueva
                hechos.add(hecho)
                logger.info("Pasada %d: se dispara %s -> nuevo hecho %s (certeza %.3f = %.2f x %.3f)",
                            iteracion, regla["nombre"], hecho, nueva, regla["certeza"], minima)
            origen.setdefault(hecho, []).append(regla)
            reglas_aplicadas.append(regla)
            disparadas.add(regla["nombre"])
            hubo_cambios = True

    if not reglas_aplicadas:
        logger.info("Fin de inferencia en %d pasada(s): no se disparó ninguna regla, "
                    "no se pudo derivar ninguna conclusión", iteracion)
    else:
        logger.info("Fin de inferencia en %d pasada(s): %d regla(s) aplicadas: %s",
                    iteracion, len(reglas_aplicadas), [r["nombre"] for r in reglas_aplicadas])

    return ResultadoInferencia(hechos, origen, certeza, reglas_aplicadas)


def verificar_independencia_orden(base_conocimiento, hechos_iniciales, tolerancia=1e-9):
    """Comprueba que el resultado no depende del orden en que están escritas las
    reglas: corre el motor con la base normal y con la base al revés y compara
    hechos y certezas. Devuelve True si coinciden."""
    normal = encadenamiento_adelante(base_conocimiento, hechos_iniciales)
    al_reves = encadenamiento_adelante(list(base_conocimiento)[::-1], hechos_iniciales)
    iguales = normal.hechos == al_reves.hechos and all(
        abs(normal.certeza[h] - al_reves.certeza[h]) <= tolerancia for h in normal.hechos)
    if not iguales:
        logger.warning("El resultado cambia con el orden de las reglas")
    return iguales


# ---------------------------------------------------------------------------
# Explicaciones (retornan texto, no imprimen)
# ---------------------------------------------------------------------------
def explicar_razonamiento(reglas_aplicadas, certeza):
    """Lista ordenada de las reglas que se dispararon, con la certeza final de
    cada conclusión. Retorna un texto."""
    if not reglas_aplicadas:
        return ("No se disparó ninguna regla: con los datos ingresados no se puede "
                "derivar ninguna conclusión.")
    lineas = ["Reglas aplicadas, en el orden en que se dispararon:"]
    for numero, regla in enumerate(reglas_aplicadas, start=1):
        condiciones = " Y ".join(regla["condiciones"])
        lineas.append(f'  {numero}. {regla["nombre"]}: SI {condiciones} ENTONCES {regla["conclusion"]}'
                      f' (certeza final {certeza[regla["conclusion"]]:.3f})')
    return "\n".join(lineas)


def _explicar_hecho(hecho, nivel, camino, iniciales, pasos, origen, certeza, lineas):
    """Parte recursiva de porque(): agrega líneas explicando un hecho."""
    sangria = "    " * nivel
    if hecho in origen:
        if hecho in camino:   # protección: no seguir si la cadena da una vuelta
            lineas.append(f"{sangria}{hecho} <- (ciclo detectado, no se sigue explicando)")
            return
        lineas.append(f"{sangria}{hecho} (certeza {certeza[hecho]:.3f})")
        for regla in origen[hecho]:
            condiciones = " Y ".join(regla["condiciones"])
            paso = pasos.get(regla["nombre"], "?")
            lineas.append(f'{sangria}  <- {regla["nombre"]} (paso {paso}, certeza de la regla '
                          f'{regla["certeza"]:.2f}): SI {condiciones} ENTONCES {hecho}')
            for condicion in regla["condiciones"]:
                _explicar_hecho(condicion, nivel + 1, camino | {hecho},
                                iniciales, pasos, origen, certeza, lineas)
    elif hecho in iniciales:
        lineas.append(f"{sangria}{hecho} <- dato del cliente")
    else:
        lineas.append(f"{sangria}{hecho} <- no se pudo concluir "
                      f"(no es un dato del cliente y ninguna regla aplicada lo derivó)")


def porque(conclusion, hechos_iniciales, reglas_aplicadas, origen, certeza):
    """Explica por qué se llegó (o no) a una conclusión.

    Sigue la cadena hacia atrás hasta los datos del cliente. Maneja los tres casos:
      * hecho derivado          -> muestra la(s) regla(s) que lo produjeron y explica sus condiciones
      * hecho inicial           -> "dato del cliente"
      * hecho no concluido      -> "no se pudo concluir"
    Retorna un texto.
    """
    pasos = {regla["nombre"]: n for n, regla in enumerate(reglas_aplicadas, start=1)}
    lineas = []
    _explicar_hecho(conclusion, 0, frozenset(), set(hechos_iniciales),
                    pasos, origen, certeza, lineas)
    return "\n".join(lineas)
