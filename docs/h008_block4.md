# H008 — Bloque 4: estrategia condicional, Δ Sharpe y benchmark nulo

Auto-suficiente. AMT/Volume Profile en BTCUSDT+ETHUSDT perp, in-sample 2022-09-01 → 2024-02-29 (holdout 2024-03→08 INTACTO, no descargado). Listón vigente: Sharpe ACTIVO requerido **0.961** (duty real 0.31), suelo de coste 0.476. El binding es el activo.

## D1. Tabla de veredicto

| condición | medido | umbral | ¿dispara? |
|---|---|---|---|
| (1) Δ Sharpe (perfil − simple) | -0.966 [-2.542,+0.533] | ≤0 e IC no cruza 0 | no |
| (1b) ¿IC del Δ cruza 0? | sí | — | underpowered sí |
| (2) coincidencia | 26% [23,28] | >80% | no (ya evaluada) |
| (3) Sharpe activo vs p95 nulo | -0.067 vs -2.041 | activo < p95 | ~~no~~ RETIRADA — nulo defectuoso (D4), no discrimina |

**VEREDICTO GLOBAL: MUERTA — Sharpe ACTIVO -0.067 ≪ listón 0.961 (no viable); con fills realistas (cruce ≥5 bps) EMPEORA a -0.986. No viable bajo ningún supuesto.** (listón activo 0.961; Sharpe activo perfil -0.067, sobre 341 episodios.)

> **Nota de registro (change h008-verdict).** H008 NO murió por REDUNDANCIA (la coincidencia del 26% descartó esa vía) — murió porque la **regla de fade de subasta pierde dinero**, con niveles de perfil o sin ellos. La condición (3) "supera al nulo" queda RETIRADA del veredicto: el nulo está mal construido (ver D4) y no discrimina. La dimensión incremental (1) es underpowered (IC del Δ cruza 0), pero el veredicto no depende de ella: el activo por sí solo mata la hipótesis.

## D2. Integridad del pareado

- episodios rama perfil (con fill): 341
- episodios rama simple (con fill): 268
- episodios COMPARTIDOS (ambos con fill): 268
- ¿pareado válido? sí — el Δ se computa SOBRE LOS COMPARTIDOS. Los episodios se definen por el CONTEXTO (balance+extensión+rechazo, vía VA del perfil); la rama simple no llena cuando su nivel (banda 1d) no se toca ese día. Se reporta el Δ sólo sobre los compartidos; los no compartidos se excluyen del Δ (no se comparan peras con manzanas).
- **SESGO DE EXCLUSIÓN (nota h008-verdict).** Los 73 episodios excluidos (341→268) NO son una muestra aleatoria: son los días donde la banda de 1 día quedó MÁS LEJOS que el borde del VA, o sea sesgados hacia RANGO AMPLIO. El pareado sobre los compartidos es válido, pero la submuestra está sesgada. Diseño correcto futuro: definir los episodios de forma que AMBOS niveles sean alcanzables por construcción.

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
- **TEST DEFECTUOSO (nota h008-verdict).** Esta distribución es catastróficamente negativa en TODOS los percentiles; ningún remuestreo de 1000 se acerca a cero. **Causa mecánica:** la salida es objetivo=POC y stop=1× rango del VA; con entrada en un nivel ALEATORIO dentro del rango del día, el POC puede quedar DETRÁS de la entrada → la posición nace con el objetivo del lado equivocado y sólo puede terminar en stop o time-stop. El nulo no mide "sin información", mide **geometría rota** (la rama perfil alcanza objetivo el 68% en D6; un nulo bien construido rondaría el 50%, no Sharpe -3.4). **Consecuencia:** la condición (3) NO discrimina — superar el p95 significa "mejor que niveles absurdos", no "hay efecto". La afirmación "los niveles de perfil llevan información vs fading aleatorio" queda RETIRADA del veredicto. **Diseño correcto futuro** (no se re-corre): el nulo debe PRESERVAR LA GEOMETRÍA — entrada aleatoria pero objetivo y stop reposicionados coherentemente, con la misma distancia objetivo/stop que la rama real.

## D5. Supuesto de fills

- Supuesto base: fill GARANTIZADO al TOQUE del nivel (fill_bps=0). Con klines 1m no se sabe si la orden límite se habría llenado, sólo si el precio tocó el nivel.
- % de episodios donde se asumió fill (rama perfil): 341/341 = 100%
- SENSIBILIDAD (fill sólo si el precio cruza ≥5 bps): Δ Sharpe -1.382 (base -0.966); Sharpe activo perfil -0.986 (base -0.067); compartidos 259.
- ¿el veredicto cambia entre supuestos? **NO** — es no-viable bajo AMBOS (activo -0.067 al toque y -0.986 con cruce ≥5 bps): el supuesto de fills sólo EMPEORA el resultado, afecta la MAGNITUD, no el veredicto. La estrategia no supera el listón bajo ninguna hipótesis de fills.
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
→ **CUMPLIDA** en dirección: el veredicto es «MUERTA — Sharpe activo -0.067 ≪ listón 0.961 (no viable bajo ningún supuesto de fills)», no una promoción. La coincidencia baja ya había refutado la parte de 'redundancia'; el edge tampoco supera el listón. H008 murió por la regla de subasta, no por redundancia.

## D9. Cómputo

- Datos: klines 1m+1d ya locales (~63 MB); perfiles del resumen (ya calculado). NO se re-descargó aggTrades. Pico de RAM ~443 MB. Pico de disco: sin cambio (nada nuevo grande).
- Episodios evaluados: 341; bootstrap pareado 1000; nulo 1000×341.

