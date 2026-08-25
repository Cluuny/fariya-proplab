# H008 — Bloque 4: estrategia condicional, Δ Sharpe y benchmark nulo

Auto-suficiente. AMT/Volume Profile en BTCUSDT+ETHUSDT perp, in-sample 2022-09-01 → 2024-02-29 (holdout 2024-03→08 INTACTO, no descargado). Listón vigente: Sharpe ACTIVO requerido **0.961** (duty real 0.31), suelo de coste 0.476. El binding es el activo.

## D1. Tabla de veredicto

| condición | medido | umbral | ¿dispara? |
|---|---|---|---|
| (1) Δ Sharpe (perfil − simple) | -0.966 [-2.542,+0.533] | ≤0 e IC no cruza 0 | no |
| (1b) ¿IC del Δ cruza 0? | sí | — | underpowered sí |
| (2) coincidencia | 26% [23,28] | >80% | no (ya evaluada) |
| (3) Sharpe activo vs p95 nulo | -0.067 vs -2.041 | activo < p95 | no |

**VEREDICTO GLOBAL: NO PROMUEVE — Sharpe activo -0.067 ≪ listón 0.961 (no viable); supera al nulo (los niveles de perfil llevan información vs fading aleatorio) · dimensión incremental (1) UNDERPOWERED (IC del Δ cruza 0).** (listón activo 0.961; Sharpe activo perfil -0.067, sobre 341 episodios)

## D2. Integridad del pareado

- episodios rama perfil (con fill): 341
- episodios rama simple (con fill): 268
- episodios COMPARTIDOS (ambos con fill): 268
- ¿pareado válido? sí — el Δ se computa SOBRE LOS COMPARTIDOS. Los episodios se definen por el CONTEXTO (balance+extensión+rechazo, vía VA del perfil); la rama simple no llena cuando su nivel (banda 1d) no se toca ese día. Se reporta el Δ sólo sobre los compartidos; los no compartidos se excluyen del Δ (no se comparan peras con manzanas).

## D3. Resultados por rama

| métrica | rama PERFIL | rama SIMPLE |
|---|---|---|
| Sharpe activo | -0.067 | -1.598 |
| Sharpe serie completa | -0.037 | -0.792 |
| retorno total | -1.56% | -39.54% |
| max_dd | 29.01% | 45.84% |
| vol realizada | 15.59% | 21.06% |
| max_dd / vol | 1.861 | 2.177 |
| episodios (fill) | 341 | 268 |
| comisión media/episodio | 5.0 bps | 5.5 bps |
| episodios que cruzaron corte funding | 153 | 141 |
| turnover (rt/día) | 0.62 | 0.49 |

## D4. Benchmark nulo

- media -3.439 · p50 -3.429 · p95 -2.041 · p99 -1.492
- Sharpe activo rama perfil (341 episodios) -0.067 vs p95 -2.041
- p-valor empírico (fracción del nulo que supera al observado): 0.000
- percentiles del nulo (Sharpe activo): p5=-4.85 · p25=-3.98 · p50=-3.43 · p75=-2.88 · p95=-2.04 · p99=-1.49

## D5. Supuesto de fills

- Supuesto base: fill GARANTIZADO al TOQUE del nivel (fill_bps=0). Con klines 1m no se sabe si la orden límite se habría llenado, sólo si el precio tocó el nivel.
- % de episodios donde se asumió fill (rama perfil): 341/341 = 100%
- SENSIBILIDAD (fill sólo si el precio cruza ≥5 bps): Δ Sharpe -1.382 (base -0.966); Sharpe activo perfil -0.986 (base -0.067); compartidos 259.
- ¿el veredicto cambia entre supuestos? SÍ — el veredicto sería sobre el supuesto de fills, no sobre la estrategia.
- **ADVERTENCIA:** asumir fill al toque INFLA el resultado. El modelo de fills nunca se construyó (docs/crypto_pivot.md lo declara prerrequisito: 'modelo de fills, va después'). Este resultado lleva ese supuesto encima.

## D6. Distribución de salidas

| salida | rama perfil | rama simple |
|---|---|---|
| objetivo alcanzado | 232 (68%) | 136 (51%) |
| stop | 89 (26%) | 82 (31%) |
| time-stop 24h | 20 (6%) | 50 (19%) |

## D7. Poder estadístico

- T efectiva usada (episodios compartidos): 268 (× ~179/año)
- SE(Ŝ) del Sharpe activo: 0.120
- SE del Δ pareado (bootstrap): 0.791
- ¿el IC distingue el falsador del umbral 0.961? sí

## D8. Expectativa comprometida

resultado_esperado (congelado) decía: Δ ≈ 0 o negativo; veredicto esperado muerta por redundancia o underpowered.
→ **CUMPLIDA** en dirección: el veredicto es «NO PROMUEVE — Sharpe activo -0.067 ≪ listón 0.961 (no viable); supera al nulo (los niveles de perfil llevan información vs fading aleatorio) · dimensión incremental (1) UNDERPOWERED (IC del Δ cruza 0)», no una promoción. (La coincidencia baja ya había refutado la parte de 'redundancia'; el edge tampoco supera el listón.)

## D9. Cómputo

- Datos: klines 1m+1d ya locales (~63 MB); perfiles del resumen (ya calculado). NO se re-descargó aggTrades. Pico de RAM ~443 MB. Pico de disco: sin cambio (nada nuevo grande).
- Episodios evaluados: 341; bootstrap pareado 1000; nulo 1000×341.

