# Sensibilidad del ciclo de fondeo a la volatilidad objetivo

**Fecha:** 2026-08-26. **Modo:** aritmética sobre `src/challenge.py`. Fuente:
`scripts/funded_vol_sensitivity.py`. NO requiere datos nuevos ni suscripción.

**LA RESPUESTA EN UNA LÍNEA:** **NO.** No existe una vol objetivo a la que un Sharpe 0.37 —lo que
el programa SÍ produjo— genere payouts materialmente mayores sin que la barrera muerda. El modelo
normal ingenuo lo sugiere (EV sube con la vol), pero al **levantar los tres caveats** (colas reales
+ límite diario intradía + supervivencia acumulativa) la barrera muerde por encima de ~12% de vol
y el valor esperado **CAE**; el óptimo sigue siendo **~8%**. La restricción de vol de §2.1 queda
**vindicada, no invalidada**.

## Por qué se hizo — y la reconciliación

`funded_sharpe_requirement` halló P(quemar)≈0 y concluyó «el cuello es PASAR, no sobrevivir». Eso
puso en duda la restricción de vol al 8% (§2.1). **Pero ese P(quemar)≈0 era un ARTEFACTO DOBLE:**
(1) sólo se barrió vol 6-10%, y (2) se usó el modelo de supervivencia INDEPENDIENTE (p_survive^12,
optimista). Al barrer hasta 25% y con supervivencia ACUMULATIVA, la barrera SÍ muerde. La premisa
de §2.1 (vol baja para que la barrera no muerda) era correcta; sólo estaba lejos a 8%.

## Caveats levantados (los tres empujan a PEOR, como se predijo)

- **(a) Supervivencia ACUMULATIVA, no independiente:** camino continuo de N×21 días con drawdown
  estático −10% acumulado desde el inicio (antes: p_survive^12, ciclos independientes = optimista).
  Sólo esto sube el burn a 8% de ~0 a ~0.15.
- **(b) Retornos REALES, no normales:** forma de una cartera CFD riesgo-igual (curtosis en exceso
  ~3.2, skew −0.27), estandarizada al objetivo y bootstrapeada en bloques → colas y autocorrelación
  reales.
- **(c) Límite diario INTRADÍA:** el −5% diario se evalúa intradía en la realidad; factor 1.8 sobre
  la magnitud del movimiento diario. **Es el efecto DOMINANTE a vol alta** (las colas intradía
  golpean el límite diario constantemente).

## D1. Barrido de vol (sintético normal — el modelo INGENUO)

Sharpe 0.37: la barrera empieza a morder ya a vol media, pero el payout crece más rápido → el EV
NORMAL sube con la vol (la conclusión seductora y FALSA):

| S | vol | P(pass) | días | burn4 | burn8 | burn12 | ret neto % | P(éxito) | EV/año (300k) |
|---|---|---|---|---|---|---|---|---|---|
| 0.37 | 8% | 0.49 | nan | 0.02 | 0.09 | 0.16 | 1.9 | 0.41 | $3597 |
| 0.37 | 12% | 0.47 | 523 | 0.10 | 0.22 | 0.29 | 3.4 | 0.33 | $5639 |
| 0.37 | 15% | 0.44 | 360 | 0.18 | 0.32 | 0.39 | 4.5 | 0.27 | $6437 |
| 0.37 | 20% | 0.40 | 235 | 0.30 | 0.42 | 0.51 | 6.3 | 0.19 | $7160 |
| 0.37 | 25% | 0.41 | 169 | 0.38 | 0.51 | 0.58 | 8.2 | 0.17 | $7928 |

(Sharpe 0.3 y 0.5 en el script; mismo patrón. P(pass) baja con la vol —hacia la moneda al aire—,
días bajan —absorbe más rápido—, burn sube.)

## D2. ¿A qué vol EMPIEZA a morder la barrera? (P(burn 12), Sharpe 0.37)

| vol | normal | **real** | **real + intradía 1.8** |
|---|---|---|---|
| 8% | 0.14 | 0.15 | **0.22** |
| 12% | 0.32 | 0.34 | **0.59** |
| 15% | 0.36 | 0.41 | **0.83** |
| 20% | 0.49 | 0.66 | **0.97** |
| 25% | 0.70 | 0.84 | **1.00** |

**Con los caveats reales, la barrera muerde CATASTRÓFICAMENTE por encima de ~12% de vol:** a 15%
quemas el 83% de las veces en 12 ciclos, a 20% el 97%. El límite diario intradía (c) sobre colas
reales (b) es lo que la dispara.

## D3. Valor esperado neto de cuotas por AÑO — ¿mejora con vol? (Sharpe 0.37)

| vol | modelo | ret neto % | payout/año | P(éxito) | EV/año (50k) | EV/año (300k) |
|---|---|---|---|---|---|---|
| 8% | normal | 1.9 | $856 | 0.38 | −$80 | $3387 |
| 8% | **real+intra1.8** | 1.9 | $856 | 0.39 | −$79 | **$3313** |
| 12% | normal | 3.4 | $1522 | 0.33 | $222 | $5666 |
| 12% | **real+intra1.8** | 3.4 | $1522 | 0.19 | −$612 | **$2538** |
| 15% | normal | 4.5 | $2022 | 0.28 | $307 | $6674 |
| 15% | **real+intra1.8** | 4.5 | $2022 | 0.08 | −$1460 | **$309** |
| 20% | normal | 6.3 | $2854 | 0.23 | $419 | $8134 |
| 20% | **real+intra1.8** | 6.3 | $2854 | 0.01 | −$3321 | **−$2907** |
| 25% | normal | 8.2 | $3687 | 0.17 | $232 | $8282 |
| 25% | **real+intra1.8** | 8.2 | $3687 | 0.00 | −$5665 | **−$5654** |

**El modelo normal dice que subir la vol MEJORA el EV (de $3.4k a $8.3k sobre 300k). El modelo
realista lo INVIERTE: el EV CAE de $3.3k (8%) a NEGATIVO (20-25%).** Los tres caveats —que empujan
a peor, como se predijo— reversan por completo la conclusión ingenua.

## D4. La respuesta

Bajo el caso PESIMISTA (real + intradía 1.8), Sharpe 0.37, EV/año sobre la cuenta escalada de 300k:

    8%→$3289 · 12%→$2377 · 15%→$320 · 20%→−$3047 · 25%→−$6153

**La mejor vol es 8%; toda vol mayor destruye valor.** No hay una vol alta que mejore el payout sin
que la barrera muerda — la premisa que motivó el barrido queda REFUTADA. Y aun el óptimo ($3.3k/año
sobre una cuenta de 300k que hay que ALCANZAR primero, con P(éxito) ~0.4) no es un negocio frente
al objetivo de §1.2 ($2500/mes). El techo de vol de §2.1 estaba bien calibrado.

## D5. Decisión Norgate — NO contratar, con el cálculo

Para cerrar el hueco 0.37→listón por AMPLITUD sola (Sharpe ∝ √N_eff, misma habilidad por apuesta),
anclando en el universo de futuros (el más ancho accesible, N_eff medido 8.15, donde trend ~0.37):

| objetivo | N_eff necesario = 8.15·(target/0.37)² |
|---|---|
| 0.37 → **0.50** | **≈ 15** |
| 0.37 → **0.80** | **≈ 38** |

La expectativa comprometida de amplitud de futuros era **9-12** (`docs/futures_case.md`); el N_eff
**medido** por proxies es **8.15**. **Los $50/mes de Norgate compran N_eff ~8, no 15 ni 38 → no
cierran el hueco.** Comprarían un número que ya conocemos y que no alcanza. **Decisión: NO se
contrata Norgate.** (Consistente con `docs/reopening_conditions.md` C1: reabrir exige N_eff medido
≥ 14, que ningún universo accesible da.)

## Conclusión

La vol alta NO rescata a un Sharpe 0.37: parece hacerlo en el modelo normal, pero las colas reales
y el límite diario intradía hacen que la barrera muerda por encima de ~12% de vol, y el valor
esperado cae a negativo. El techo de vol de §2.1 queda vindicado. Y la amplitud que cerraría el
hueco (N_eff 15-38) no está a la venta por $50. Cuarta confirmación del cierre, desde el eje de la
volatilidad objetivo.
