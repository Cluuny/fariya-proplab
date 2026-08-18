# Política de holdout (§3.5 del documento maestro)

> "Holdout sagrado. Los últimos 3 años apartados. No los tocas. Ni una vez."

El holdout protege contra el sobreajuste que surge de **buscar, seleccionar o
tunear** sobre los propios datos. La regla: apartar los **últimos 3 años** y no
mirarlos hasta la validación final de una hipótesis.

Ventana de holdout: **2023-08-17 → 2026-08-17** (últimos 3 años; ver
`config.HOLDOUT_START`).

## Decisión explícita para H001 — EXENTA del holdout

H001 (Time-Series Momentum) **NO aparta holdout**; corre sobre la muestra completa.

**Por qué:** H001 es un **test de calibración contra un resultado publicado**
(Moskowitz, Ooi & Pedersen 2012, sobre 1965-2009). No hay búsqueda ni tuneo sobre
nuestros datos: se implementa una regla **pre-registrada fija** (signo del retorno
a 12 meses, sizing por vol inversa) y se comprueba si reproduce el resultado del
paper. Además, **todo nuestro período (2011-2026) es out-of-sample respecto al
paper** (que termina en 2009), así que no hay muestra in-sample que proteger. El
holdout no aplica a una replicación externa sin grados de libertad.

## Desde cuándo RIGE el holdout

El holdout **rige a partir de la primera hipótesis de descubrimiento/optimización**
— cualquiera donde elijamos parámetros, universo, reglas de entrada/salida o
cualquier grado de libertad **con base en nuestros propios backtests**, en vez de
reproducir un resultado externo pre-registrado.

En la práctica: **desde H002 en adelante**, salvo que H002 también sea una
replicación externa pura sin tuneo (en cuyo caso se aplica el mismo argumento de
exención, explícitamente, en su ficha). En cuanto una ficha introduzca selección
sobre nuestros datos, el holdout 2023-08 → 2026-08 queda **sagrado**: no se mira
hasta la validación final de esa hipótesis.

## Regla operativa

- Cada ficha de hipótesis (`Hxxx_*.yaml`) declara explícitamente si aplica holdout
  y, si no, por qué (como aquí para H001).
- No se relitiga por omisión: si una ficha no lo declara, se asume que SÍ aplica.
