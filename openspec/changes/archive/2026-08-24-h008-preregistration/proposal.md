# Pre-registro H008 — AMT / Volume Profile en cripto

## Por qué

AMT/volume profile quedó `rechazada_por_datos` porque no había volumen consolidado (FX es OTC;
el "volumen" de Dukascopy es conteo de ticks de un broker). **Esa restricción cambió:** hay
libro de órdenes de cripto gratis, ya ingerido y validado (bookTicker + aggTrades, volumen real
por nivel de precio). Es el mismo tipo de argumento externo que reabrió H007 tras la ampliación
de universo — no "a ver si esta vez sí". Entra como **H008 (novena familia), FUERA de la
condición de parada**, con esa justificación explícita en la ficha.

## Qué cambia

- **`hypotheses/H008_amt_volume_profile.yaml`** (SÓLO la ficha), esquema H003/H007:
  - **Reapertura** documentada primero; fuera de la condición de parada.
  - **Hipótesis INCREMENTAL** (innegociable): ¿el VAH/VAL/POC aporta sobre niveles simples?
    Δ Sharpe (perfil − simple) por bootstrap pareado; % de coincidencia VAH≈máx-N (tol 10 bps);
    coincidencia > 80% = redundancia = hallazgo.
  - **Condicional**: contexto de balance determinista ex-ante (rango previo/ATR < 1.0 + toque de
    borde del VA), duty 20% por diseño.
  - **Trampa de duty bajo registrada**: Sharpe activo requerido 0.40/√duty+0.245 = **1.14** a
    duty 20%. Ser selectivo no es gratis.
  - **Benchmark nulo** (lección H003): misma exposición, niveles al azar, 1000 remuestreos,
    semilla fija, p95; falsador relativo al p95.
  - **Suelo de costes** cripto: 0.5 rt/día maker funding-evitado → **0.52 bruto**; sin literatura
    arbitrada (se dice explícitamente).
  - **Poder**: SE(Ŝ)≈√((1+S²/2)/T); T≥150 exige ≥2 años; estado `underpowered` disponible.
  - **Expectativa comprometida** con derivación (redundancia esperada; qué sería "el VAH es
    redundante"); **falsador congelado y disparable** con un único chequeo de robustez contado.
  - **Datos** fijados: BTCUSDT, aggTrades+bookTicker (ya ingeridos), perfil diario rodante 24 h,
    bucket $10. Holdout = últimos 6 meses.
- **`hypotheses/QUEUE.md`**: fila H008 = pre_registrado.

## Impacto

- Sólo fichas/docs. **Cero código, cero corridas, cero acceso a datos.** Suite 193 verde
  (sin cambios de código). Sin delta de spec. La ficha se revisa antes de implementar.
