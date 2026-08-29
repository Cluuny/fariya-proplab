# H009 — corrida: AMT continuación (aceptación fuera del área de valor)

Auto-suficiente. Cara de CONTINUACIÓN de AMT en BTCUSDT+ETHUSDT perp, in-sample 2022-09-01 → 2024-02-29 (holdout 2024-03→08 INTACTO, no descargado). Ficha congelada `hypotheses/H009_amt_continuation.yaml`; NO se tocó FALSADOR ni resultado_esperado.

## D1. Duty real, T efectiva, listón recalculado (lo primero)

- Embudo (in-sample 2022-09-01→2024-02-29, BTC+ETH): días válidos **1092** → DESEQUILIBRIO previo (>1.5) **170** → extensión fuera del VA **153** → **ACEPTACIÓN (K=3) 101**.
- **Duty real = 0.092** (episodios 101 / 1092 día-instrumento). round-trips/día 0.185.
- **T efectiva = 73** (por coincidencia REAL: 32 fechas con episodio en BTC y ETH a la vez → cuentan 1.11 cada par a ρ0.8; 37 de un solo instrumento cuentan 1. La cota cruda-conservadora 56 asumía todo coincidente; la real es 73 > 60 → RESOLUBLE).
- **Listón recalculado = 0.40/√0.092 + 0.245 = 1.560** (Sharpe ACTIVO requerido; a priori la ficha estimó ~1.28 a duty 0.15).

## D2. Tabla de veredicto

| condición | medido | umbral | ¿dispara? |
|---|---|---|---|
| (1) Δ Sharpe (perfil − simple) | +4.325 [+2.874,+7.334] | ≤0 e IC no cruza 0 | no |
| (1b) ¿IC del Δ cruza 0? | no | — | underpowered no |
| (2) Sharpe activo vs p95 nulo | -1.190 vs -0.484 | activo < p95 (si geometría OK) | no |
| (3) Sharpe activo vs listón | -1.190 vs 1.560 | activo < listón | sí |

**VEREDICTO GLOBAL: NO VIABLE — Sharpe activo -1.190 ≪ listón 1.560 · (2) NO usada: geometría del nulo rota.**

## D3. Integridad del pareado

- episodios rama perfil (con fill): 72
- episodios rama simple (con fill): 100
- episodios COMPARTIDOS (ambos con fill): 72
- El Δ se computa SOBRE LOS COMPARTIDOS; los episodios se definen por el CONTEXTO (desequilibrio+extensión+aceptación), no por los niveles. La rama simple no llena cuando su nivel (banda 1d) no se toca ese día.

## D4. Resultados por rama

| métrica | rama PERFIL | rama SIMPLE |
|---|---|---|
| Sharpe activo (IC95) | -1.190 [-1.49,-0.89] | -3.068 [-3.54,-2.60] |
| Sharpe serie completa | -0.306 | -0.929 |
| retorno total | -26.57% | -148.44% |
| max_dd | 27.21% | 144.74% |
| vol realizada | 20.95% | 32.69% |
| max_dd / vol | 1.298 | 4.428 |
| episodios (fill) | 72 | 100 |
| comisión media/episodio | 6.6 bps | 6.9 bps |
| episodios que cruzaron funding | 60 | 100 |
| turnover (rt/día) | 0.13 | 0.18 |

## D5. Benchmark nulo (con verificación de sanidad ANTES del veredicto)

- **VERIFICACIÓN DE GEOMETRÍA: el nulo alcanza objetivo 9% de las veces** → geometría ROTA (lejos de 50% → la condición 2 NO se usa; se dice, no se maquilla).
- MECANISMO del 9% (honesto, no es el defecto de H008): aquí el objetivo NO está detrás de la entrada (es simétrico ±1×rango_VA); el 9% viene de que ±1×rango_VA es un objetivo LEJANO para una entrada aleatoria a media sesión → el nulo (y también el activo: 14% perfil, D7) time-stopea antes de tocarlo. El nulo es geométricamente JUSTO (mismo objetivo lejano que el activo), pero la sanidad ~50% se calibró para objetivos cercanos → se marca ROTA y (2) NO se usa por conservadurismo. El veredicto NO depende de (2): (3) lo cierra solo.
- media -1.681 · p50 -1.656 · p95 -0.484 · p99 -0.090
- Sharpe activo rama perfil (101 episodios) -1.190 vs p95 -0.484
- p-valor empírico (fracción del nulo ≥ observado): 0.267

## D6. Sensibilidad de fills

- Base = fill al TOQUE. Con cruce ≥5 bps: Δ Sharpe +4.244 (base +4.325); Sharpe activo perfil -1.086 (base -1.190); compartidos 72.
- ¿el veredicto cambia entre supuestos? NO — afecta la MAGNITUD, no el veredicto. El modelo de fills real no se construyó; el resultado lleva el supuesto de fill-al-toque encima.

## D7. Distribución de salidas

| salida | rama perfil | rama simple |
|---|---|---|
| objetivo (continuación) | 10 (14%) | 4 (4%) |
| stop (vuelta al VA) | 8 (11%) | 5 (5%) |
| time-stop 24h | 54 (75%) | 91 (91%) |

## D8. Expectativa comprometida

resultado_esperado (congelado): Sharpe activo entre −0.3 y +0.3; veredicto esperado MUERTA o UNDERPOWERED; probabilidad previa BAJA. Sin interpretar a favor:
→ Sharpe activo medido -1.190 (FUERA del rango −0.3..+0.3); veredicto «NO VIABLE — Sharpe activo -1.190 ≪ listón 1.560 · (2) NO usada: geometría del nulo rota». **PARCIAL/REFUTADA** en dirección.

## D9. Cómputo

- Datos: klines 1m+1d locales + perfiles del resumen (h008). NO se re-descargó nada. Pico RAM ~438 MB.
- Episodios 101; bootstrap pareado 1000; nulo 1000×101 (semilla 20260829).

