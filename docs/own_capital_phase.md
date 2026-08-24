# Fase de capital propio — DISEÑO (no se opera todavía)

**SOLO DISEÑO.** No se opera, no se deposita, no se conecta a ningún exchange. Este
documento se escribe, se deja reposar, y se decide después con la cabeza fría.

## 1. El objetivo real (escrito primero, para que no se distorsione)

Esta fase **NO genera ingreso.** Con $200 al 20% de vol y Sharpe 0.5 (que sería el MEJOR
resultado del proyecto), el retorno esperado es **~$20/año**, con probabilidad no trivial de
**−$60** en algún momento. No es un negocio; es un instrumento de medición.

El objetivo es **MEDIR LA DEGRADACIÓN entre backtest y vivo**: slippage real, latencia real,
calidad de fills, y comportamiento del sistema bajo operación continua. Esa información NO la
da ningún dato histórico y es el prerrequisito de cualquier escalado futuro.

**CRITERIO DE ÉXITO DE LA FASE:** sobrevivir **12 meses** con el sistema corriendo y un
**factor de degradación medido**. NO es un retorno objetivo. Un año que termine plano o con
una pérdida pequeña pero con un factor de degradación fiable es un ÉXITO; un año rentable por
suerte sin instrumentación es un fracaso disfrazado.

**RIESGO NUEVO, dicho sin adornos:** con capital propio, perder es perder. Hasta ahora el
peor resultado del programa era una cuota de challenge no gastada (I+D con expectativa
negativa presupuestada). Ahora el downside es capital real. El tamaño ($200) está elegido
para que la LECCIÓN sea barata, no para que el resultado importe.

## 2. Qué cambia en el modelo de costes (2.2)

Sin barrera absorbente, el vol objetivo puede subir de 8% a 15-20%. Recalculado el bruto
requerido (net > 0.40), suelo CFD (coste ~2.0%/año):

| vol objetivo | break-even | bruto requerido (net>0.40) |
|---|---|---|
| 8% (con barrera) | 0.25 | **0.65** |
| 15% | 0.13 | **0.53** |
| 20% | 0.10 | **0.50** |

Baja el listón de **0.65 → 0.50** frente al 0.65 de cripto y el 0.64 del CFD.

**PERO — advertencia que corrige una trampa (verificada numéricamente):** subir la vol
**baja el listón SÓLO si la vol extra viene de instrumentos MÁS VOLÁTILES al mismo notional**
(coste fijo en $, más riesgo → coste/riesgo baja). Si la vol extra viene de **apalancamiento**
(más notional del mismo instrumento), **el listón NO baja**: el coste (comisión, spread,
funding, margen) escala con el notional igual que la vol → `coste/vol` es INVARIANTE. Es el
mismo resultado que ya mató la idea de "el bruto es una palanca" en el ciclo CFD (Sharpe es
invariante al apalancamiento). Verificado: gross×1 vs gross×2 → coste/vol = 0.251 en ambos,
requerido 0.65 sin cambio. **La palanca real es el coste-por-unidad-de-riesgo (elegir un
mercado con más vol por unidad de comisión), no el apalancamiento.**

**Esto baja el LISTÓN, no crea EDGE.** Verificación explícita de cuáles de las ocho
sobrevivirían al listón nuevo:

- Mejor bruto del proyecto: **H002 carry 0.495**. Contra el listón a 20% de vol (**0.50**):
  **NO cruza** (0.495 < 0.50, corto por 0.005) — y aunque rozara, **muere por concentración**
  (short-JPY, N_eff 3.41, prima de crash), no por el listón.
- Trend (H007 0.370, H001 0.24-0.31), H005 (0.3-0.5 plausible): **por debajo de 0.50** en
  todos los casos.
- Order flow: cerrado por el RATIO señal/coste (25-100× el coste), invariante a la vol.

**Conclusión: incluso al listón más bajo (0.50 a 20% de vol), NINGUNA de las ocho
sobrevive.** Bajar el listón por quitar la barrera NO resucita a ninguna. Las ocho siguen
muertas. (Si el umbral se relajara de "net 0.40" a mero break-even —no perder mientras se
mide— H001/H002/H007 tienen neto marginalmente positivo, pero eso es "no sangrar", no un edge
viable, y la concentración de H002 sigue descalificándola.)

## 3. La pregunta abierta (2.3) — documentada, NO respondida

¿Qué se opera? **No hay estrategia viva.** Las opciones, sin elegir todavía:

1. **Reevaluar las 8 contra el listón de capital propio** (aritmética pura, gratis). Ya hecho
   arriba: ninguna cruza el 0.50. Un no barato y ya pagado.
2. **Buscar en el pipeline de investigación con el filtro de costes nuevo** (`src/pipeline/`).
   El filtro #6 con el listón a 15-20% de vol admite candidatos que a 8% se rechazaban; es la
   vía legítima para una novena idea.
3. **Una novena familia por corazonada → PROHIBIDO** por la condición de parada
   (`docs/program_verdict.md`), salvo que salga del pipeline y pase el filtro #6. No de una
   intuición.

Las tres quedan documentadas. **No se elige ahora.**

## 4. Infraestructura mínima para operar en vivo (2.4) — sólo listada

No se construye nada todavía; se lista lo que haría falta ANTES de arriesgar un peso:

- **Gestión de claves API** — nunca en el repo; variables de entorno / almacén de secretos;
  claves con permisos mínimos (trading sí, retiro NO).
- **Límites de posición duros en CÓDIGO** — no en configuración editable; tope de notional y
  de apalancamiento que el sistema no pueda exceder aunque la señal lo pida.
- **Kill-switch** — un comando/condición que aplana todo y desconecta.
- **Log de todas las órdenes** — intención, envío, fill, rechazo; inmutable, con timestamps.
- **Reconciliación diaria backtest-vs-vivo** — comparar el fill real con el que el backtest
  habría asumido; es la MEDICIÓN que justifica la fase.
- **Alerta si la degradación supera un umbral** — si el vivo se aparta del backtest más de X,
  avisar y (opcional) pausar.

## Estado

Documento de diseño. **NO se decide qué operar. NO se conecta nada. NO se deposita.** Se deja
reposar y se decide después. El ciclo de descubrimiento está cerrado (ocho familias, cero
supervivientes, `docs/program_verdict.md`); esta fase es de INSTRUMENTACIÓN, no de ingreso.
