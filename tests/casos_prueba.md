# Casos de prueba y validación

Sistema experto para una óptica. Autores: Adrian Murcia y Juan Gómez.

Los resultados esperados se calcularon a mano **antes** de correr el programa (ver "Verificación de los cálculos de certeza"). La columna "Resultado obtenido" es lo que devolvió `encadenamiento_adelante(REGLAS, armar_hechos(ficha))`. Todos los casos se corrieron también con la base de reglas en orden invertido y dieron los mismos hechos y certezas.

Las fichas completas de los casos 1 a 6 están en `src/base_conocimiento.py` (`CASOS_PRUEBA`) y se pueden cargar desde la interfaz con el selector de casos.

## 1. Casos principales

| Caso | Descripción | Hechos iniciales | Reglas esperadas | Conclusión esperada | Resultado obtenido | Estado |
|---|---|---|---|---|---|---|
| 1 | Carlos: 52 años, miope leve con presbicia, 8 h de pantalla con síntomas, conduce de noche | adicion_positiva, conduce_noche, edad_mayor_40, esfera_negativa, pantallas_6h, sintomas_fatiga | R1, R2, R3, R4, R5, R7 | miopia 1.000; presbicia 0.950; fatiga_visual_digital 0.850; rec_progresivo 0.855; rec_progresivo_ocupacional 0.782; rec_antirreflejo 0.900 | Reglas: R1 → R2 → R3 → R4 → R5 → R7. Conclusiones: miopia 1.000; presbicia 0.950; fatiga_visual_digital 0.850; rec_progresivo 0.855; rec_progresivo_ocupacional 0.782; rec_antirreflejo 0.900 | ✓ |
| 2 | Sofía: 9 años, niña miope que juega fútbol | deporte_activo, es_nino, esfera_negativa | R1, R9, R10 | miopia 1.000; rec_policarbonato 0.995 | Reglas: R1 → R9 → R10. Conclusiones: miopia 1.000; rec_policarbonato 0.995 | ✓ |
| 3 | Marta: 35 años, miopía alta, trabaja al sol, examen hace 14 meses | dioptria_alta, esfera_negativa, formula_vencida, trabajo_exterior | R1, R6, R8, R12 | miopia 1.000; rec_alto_indice 0.900; rec_fotocromatico 0.850; rec_examen_previo 0.950 | Reglas: R1 → R6 → R8 → R12. Conclusiones: miopia 1.000; rec_alto_indice 0.900; rec_fotocromatico 0.850; rec_examen_previo 0.950 | ✓ |
| 4 | Jorge: 61 años, présbita con destellos y pérdida súbita de visión, examen hace 20 meses | adicion_positiva, edad_mayor_40, formula_vencida, sintomas_alarma | R2, R4, R11, R12 | presbicia 0.950; rec_progresivo 0.855; rec_remision_urgente 0.980; rec_examen_previo 0.950 | Reglas: R2 → R4 → R11 → R12. Conclusiones: presbicia 0.950; rec_progresivo 0.855; rec_remision_urgente 0.980; rec_examen_previo 0.950 | ✓ |
| 5 | Ana: 28 años, sin nada especial (caso sin conclusión) | ninguno | ninguna | ninguna | Reglas: ninguna. Conclusiones: ninguna | ✓ |
| 6 | Roberto: 58 años, miopía alta con presbicia, 9 h de pantalla con síntomas, conduce de noche, trabaja al sol, hace deporte, tiene síntomas de alarma y el examen fue hace 15 meses (activa 11 de las 12 reglas) | adicion_positiva, conduce_noche, deporte_activo, dioptria_alta, edad_mayor_40, esfera_negativa, formula_vencida, pantallas_6h, sintomas_alarma, sintomas_fatiga, trabajo_exterior | R1, R2, R3, R4, R5, R6, R7, R8, R10, R11, R12 | miopia 1.000; presbicia 0.950; fatiga_visual_digital 0.850; rec_progresivo 0.855; rec_progresivo_ocupacional 0.782; rec_alto_indice 0.900; rec_antirreflejo 0.900; rec_fotocromatico 0.850; rec_policarbonato 0.900; rec_remision_urgente 0.980; rec_examen_previo 0.950 | Reglas: R1 → R2 → R3 → R4 → R5 → R6 → R7 → R8 → R10 → R11 → R12. Conclusiones: miopia 1.000; presbicia 0.950; fatiga_visual_digital 0.850; rec_progresivo 0.855; rec_progresivo_ocupacional 0.782; rec_alto_indice 0.900; rec_antirreflejo 0.900; rec_fotocromatico 0.850; rec_policarbonato 0.900; rec_remision_urgente 0.980; rec_examen_previo 0.950 | ✓ |

**Qué ejercita cada caso**

* **Caso 1 (Carlos):** encadenamiento de dos niveles (R2 y R3 alimentan a R4 y R5), `min` de certezas en R5 y conducción nocturna (R7).
* **Caso 2 (Sofía):** combinación de certezas, porque R9 y R10 llegan a la misma conclusión.
* **Caso 3 (Marta):** R6 necesita el hecho intermedio `miopia`; además fotocromático y fórmula vencida.
* **Caso 4 (Jorge):** alerta de seguridad (R11). Esfera positiva, así que no se activa nada de miopía.
* **Caso 5 (Ana):** caso **sin conclusión**: no se dispara ninguna regla y el motor termina sin errores.
* **Caso 6 (Roberto):** caso que **activa la mayoría de las reglas**: 11 de 12 (todas menos R9, porque un cliente de 58 años no puede ser niño).

### Cobertura de reglas

| Regla | Categoría | Casos principales que la activan |
|---|---|---|
| R1 | clasificación | 1, 2, 3, 6 |
| R2 | clasificación | 1, 4, 6 |
| R3 | clasificación | 1, 6 |
| R4 | lentes y tratamientos | 1, 4, 6 |
| R5 | lentes y tratamientos | 1, 6 |
| R6 | lentes y tratamientos | 3, 6 |
| R7 | lentes y tratamientos | 1, 6 |
| R8 | lentes y tratamientos | 3, 6 |
| R9 | lentes y tratamientos | 2 |
| R10 | lentes y tratamientos | 2, 6 |
| R11 | seguridad | 4, 6 |
| R12 | seguridad | 3, 4, 6 |

Las 12 reglas se activan al menos en un caso principal.

## 2. Casos de borde

Valores justo en el umbral y justo al lado. Salvo lo indicado, la ficha base es: edad 30, esfera OD 0.00 y OI 0.00, adición 0.00, 0 horas de pantalla, 0 meses desde el examen y ningún síntoma.

| Caso | Descripción | Hechos iniciales | Reglas esperadas | Conclusión esperada | Resultado obtenido | Estado |
|---|---|---|---|---|---|---|
| B1 | Edad = 40 (límite incluido), adición 2.00 | adicion_positiva, edad_mayor_40 | R2, R4 | presbicia 0.950; rec_progresivo 0.855 | Reglas: R2 → R4. Conclusiones: presbicia 0.950; rec_progresivo 0.855 | ✓ |
| B2 | Edad = 39 (justo debajo), adición 2.00 | adicion_positiva | ninguna | ninguna | Reglas: ninguna. Conclusiones: ninguna | ✓ |
| B3 | Edad = 12 (límite incluido) | es_nino | R9 | rec_policarbonato 0.950 | Reglas: R9. Conclusiones: rec_policarbonato 0.950 | ✓ |
| B4 | Edad = 13 (justo encima) | ninguno | ninguna | ninguna | Reglas: ninguna. Conclusiones: ninguna | ✓ |
| B5 | Esfera OD = -0.50 (límite incluido), OI = 0.00 | esfera_negativa | R1 | miopia 1.000 | Reglas: R1. Conclusiones: miopia 1.000 | ✓ |
| B6 | Esfera OD = -0.25 (justo debajo), OI = 0.00 | ninguno | ninguna | ninguna | Reglas: ninguna. Conclusiones: ninguna | ✓ |
| B7 | Solo un ojo miope (∃): OD = +2.00, OI = -0.50 | esfera_negativa | R1 | miopia 1.000 | Reglas: R1. Conclusiones: miopia 1.000 | ✓ |
| B8 | \|Esfera\| = 4.00 (límite incluido): OD = -4.00, OI = -1.00 | dioptria_alta, esfera_negativa | R1, R6 | miopia 1.000; rec_alto_indice 0.900 | Reglas: R1 → R6. Conclusiones: miopia 1.000; rec_alto_indice 0.900 | ✓ |
| B9 | \|Esfera\| = 3.75 (justo debajo): OD = -3.75, OI = -1.00 | esfera_negativa | R1 | miopia 1.000 | Reglas: R1. Conclusiones: miopia 1.000 | ✓ |
| B10 | Dioptría alta sin miopía: OD = +4.00, OI = +4.00 (R6 exige miopía) | dioptria_alta | ninguna | ninguna | Reglas: ninguna. Conclusiones: ninguna | ✓ |
| B11 | Adición = 0.75 (límite incluido), edad 50 | adicion_positiva, edad_mayor_40 | R2, R4 | presbicia 0.950; rec_progresivo 0.855 | Reglas: R2 → R4. Conclusiones: presbicia 0.950; rec_progresivo 0.855 | ✓ |
| B12 | Adición = 0.50 (justo debajo), edad 50 | edad_mayor_40 | ninguna | ninguna | Reglas: ninguna. Conclusiones: ninguna | ✓ |
| B13 | Horas de pantalla = 6 (límite incluido) con síntomas de fatiga | pantallas_6h, sintomas_fatiga | R3 | fatiga_visual_digital 0.850 | Reglas: R3. Conclusiones: fatiga_visual_digital 0.850 | ✓ |
| B14 | Horas de pantalla = 5.5 (justo debajo) con síntomas de fatiga | sintomas_fatiga | ninguna | ninguna | Reglas: ninguna. Conclusiones: ninguna | ✓ |
| B15 | Meses desde el examen = 12 (todavía vigente) | ninguno | ninguna | ninguna | Reglas: ninguna. Conclusiones: ninguna | ✓ |
| B16 | Meses desde el examen = 13 (vencida) | formula_vencida | R12 | rec_examen_previo 0.950 | Reglas: R12. Conclusiones: rec_examen_previo 0.950 | ✓ |

### Independencia del orden de las reglas

Se corrió cada caso principal con `REGLAS` normal y con `REGLAS[::-1]` (también con `verificar_independencia_orden`). Cambia el orden de disparo, pero no los hechos ni las certezas:

| Caso | Cliente | Orden de disparo (base normal) | Orden de disparo (base invertida) | Mismos hechos y certezas |
|---|---|---|---|---|
| 1 | Carlos | R1 → R2 → R3 → R4 → R5 → R7 | R7 → R3 → R2 → R1 → R5 → R4 | Sí |
| 2 | Sofía | R1 → R9 → R10 | R10 → R9 → R1 | Sí |
| 3 | Marta | R1 → R6 → R8 → R12 | R12 → R8 → R1 → R6 | Sí |
| 4 | Jorge | R2 → R4 → R11 → R12 | R12 → R11 → R2 → R4 | Sí |
| 5 | Ana | ninguna | ninguna | Sí |
| 6 | Roberto | R1 → R2 → R3 → R4 → R5 → R6 → R7 → R8 → R10 → R11 → R12 | R12 → R11 → R10 → R8 → R7 → R3 → R2 → R1 → R6 → R5 → R4 | Sí |

## 3. Verificación de los cálculos de certeza

Fórmulas: al disparar, `certeza = certeza_regla × min(certeza de las condiciones)`; si el hecho ya existía, `nueva = actual + aplicada × (1 − actual)`. Los datos del cliente valen 1.0.

* Carlos: miopía 1.00 × 1.0 = 1.000; presbicia 0.95 × 1.0 = 0.950; fatiga 0.85 × 1.0 = 0.850; progresivo 0.90 × 0.95 = 0.855; ocupacional 0.92 × min(0.95, 0.85) = 0.92 × 0.85 = 0.782; antirreflejo 0.90.
* Sofía: miopía 1.000; policarbonato: R9 da 0.95 y R10 da 0.90, combinado 0.95 + 0.90 × (1 − 0.95) = 0.95 + 0.045 = 0.995.
* Marta: miopía 1.000; alto índice 0.90 × min(1.0, 1.0) = 0.900; fotocromático 0.850; examen previo 0.950.
* Jorge: presbicia 0.950; progresivo 0.855; remisión urgente 0.980; examen previo 0.950.
* Ana: ninguna regla, sin conclusiones.
* Roberto: igual que Carlos para miopía, presbicia, fatiga, progresivo (0.855), ocupacional (0.782) y antirreflejo (0.900); alto índice 0.90 × min(1.0, 1.0) = 0.900; fotocromático 0.850; policarbonato solo por R10 = 0.900 (R9 no se activa); remisión urgente 0.980; examen previo 0.950.
* Casos de borde: cada uno dispara reglas de una sola condición o de condiciones con certeza 1.0, así que los valores son directamente la certeza de la regla (R1 1.00, R2 0.95, R3 0.85, R9 0.95, R12 0.95, R6 0.90) o el producto con la regla previa (R4: 0.90 × 0.95 = 0.855).

## 4. Resumen

* Casos principales: 6 de 6 correctos.
* Casos de borde: 16 de 16 correctos.
* Independencia del orden: 6 de 6 casos principales iguales con la base invertida (los casos de borde también pasan `verificar_independencia_orden`).
* Caso sin conclusión (Caso 5 y casos de borde sin reglas): el motor termina sin errores y la interfaz muestra "Sin recomendaciones especiales".
