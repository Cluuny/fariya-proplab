## Context

Ver `proposal.md`. Ficha de pre-registro de H003 (estacionalidad, familia 3 del §2.5). Datos verificados: índices desde 2011-09 (SPX/JPN) y 2013-09 (GER40).

## Decisions (contenido de la ficha)

### D1 — El efecto concreto: turn-of-the-month (TOM) en índices
De la familia "estacionalidad y efectos de calendario", el efecto más documentado, más limpio de testear y con mejor historia económica sobre NUESTRO panel es el **turn-of-the-month**: el retorno de los índices de renta variable se concentra en la ventana [último día hábil del mes, +3 días hábiles]. Fuente: Ariel (1987, JFE), McConnell & Xu (2008, FAJ). Mecanismo (filtro 4): flujos de caja institucionales concentrados a fin/inicio de mes (sueldos, aportes de pensión, rebalanceo por mandato, window dressing) → presión compradora predecible; contraparte = proveedores de liquidez que absorben el flujo.

### D2 — Universo: los 3 índices, no los 9
El efecto es institucional-equity; en FX/oro la historia de flujos de mandato no aplica limpiamente (filtro 4). Universo = SPX500, GER40, JPN225. **Costo honesto**: 3 índices correlacionados 0.5-0.7 → breadth efectiva ~2 → techo de Sharpe bajo (Grinold-Kahn). Se documenta en `resultado_esperado`.

### D3 — Regla: long-only en ventana, flat el resto
`regla_entrada`: largo en cada índice durante [−1, +3] (último día hábil del mes prev. hasta 3er día hábil del mes). `regla_salida`: cerrar al 3er día hábil → flat. Direccionalidad long_only (el efecto es de drift alcista concentrado; shortear fuera de ventana pierde con el drift secular). Turnover ~12 entradas + 12 salidas/año, holding ~4 días → **swap mínimo, spread la única fricción real** (a diferencia de H001, donde el swap dominaba).

### D4 — Sizing ex-ante, misma infra que H001
Vol-inversa (`engine.rolling_vol`) entre los índices activos, escalado ex-ante (escalar rodante) a ~8% de vol de PORTAFOLIO, bruto ≤ MAX_GROSS. **Caveat**: como está flat ~81% del tiempo, apuntar a 8% de vol de período completo exige apalancamiento alto en ventana (probable recorte por max_gross); la vol efectiva puede quedar por debajo de 8%. No afecta al falsador (Sharpe invariante al escalado); sí al diagnóstico del simulador.

### D5 — Holdout RESPETADO (no exento)
A diferencia de H001 (exento por replicación exacta de un paper), H003 tiene libertad de especificación (nuestro universo de 3 índices CFD, nuestro sizing). Y la política del holdout debe empezar a ejercerse. Por tanto:
- **In-sample**: 2011-09 → 2023-08-16 (donde se desarrolla y se juzga el falsador).
- **Holdout sagrado**: 2023-08-17 → 2026 (`config.HOLDOUT_START`), reservado. Se toca UNA vez, sólo si pasa in-sample, para confirmar.
No hay muestra pre-2010 (los índices no existen antes de 2011), así que el enfoque de dos muestras de H001 no aplica; el corte in-sample/holdout es el que corresponde.

### D6 — Veredicto y expectativa
`metrica_exito`: Sharpe neto in-sample > 0.4 → pasa a confirmación en holdout. `FALSADOR`: Sharpe neto in-sample < 0.2 → muerta, sin variantes. Zona [0.2, 0.4]: mismo chequeo único de robustez que H001 (una variante de ventana pre-especificada, [−1, +4], deflated Sharpe, promueve sólo si deflated > 0.4). `resultado_esperado`: central ~0.35, rango [0.15, 0.60] (Grinold-Kahn con breadth ~2; el efecto está documentado como atenuado post-2000 y nuestra muestra es 2011+).

### D7 — Diagnósticos de primera línea (lección de H001)
Obligatorios en el veredicto: `turnover_anual`, `sharpe_zero_cost` (distingue efecto débil de fricción), y **max DD relativo a vol** (el falsador de Sharpe es necesario pero no suficiente).

## Risks / Trade-offs
- **Universo delgado (3 índices)** → techo de Sharpe bajo; se asume y se documenta, no se infla el universo con FX para ganar breadth (sería romper filtro 4).
- **Muestra 2011+**: no se puede ver la decadencia histórica del efecto (documentada ~post-2000); el test es de PERSISTENCIA en régimen moderno, no de existencia histórica. Se anota.

## Open Questions
- Ninguna que bloquee. La construcción exacta del calendario de ventana y del escalar se fija en el change de implementación.
