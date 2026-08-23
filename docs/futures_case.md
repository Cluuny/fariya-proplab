# ¿Migrar a futuros? — el caso, con aritmética y datos gratis

La opción A (migrar a futuros) es atractiva pero cuesta dinero que no hay. Antes de
gastar: ¿el cambio de vehículo baja el suelo de costes lo suficiente para que un bruto
realista sobreviva? La pregunta NO es "¿funciona trend en futuros?" (la industria dio
~0.14 en nuestra ventana). Es sobre el SUELO y la AMPLITUD.

## Criterio de decisión — COMPROMETIDO antes del análisis

La suscripción se justifica SÓLO si se cumplen **LAS DOS**:
1. **Suelo recalculado deja el bruto requerido < 0.50.**
2. **N_eff estimada del universo de futuros > 7.5.**

Si no se cumplen, la opción A queda **CERRADA POR EVIDENCIA**, no por falta de dinero.

---

## Bloque 1 — Coste de mantener en futuros

**Hecho estructural (la clave):** los futuros NO cobran el margen diario de
financiación que domina el suelo del CFD (0.42 bp/día ≈ **1.96%/año**). El carry va
embebido en el precio del futuro (no se cuenta dos veces: la señal lo captura vía
precio). El coste de mantener futuros es: **roll** (spread del calendar spread × ~4
rolls/año) + **comisión** + **spread bid/ask** del front. Sin margen diario.

**Fuentes públicas** (consultadas 2026-08-23):
- Especificaciones de contrato CME (notional, tick value): cmegroup.com.
- Comisión IBKR: **$0.85/contrato/lado**, ~**$4.20 round-trip** all-in
  (interactivebrokers.com/en/pricing, vía búsqueda 2026-01).
- Modelo: roll = 4 × (1 tick de calendar spread); spread front = turnover(~9×) × 1
  tick/lado; comisión = round-trips × $4.20. Turnover como el trend actual.

### Coste de mantener por mercado (%/año)

| clase | mercados baratos (%/año) | mercados caros por ROLL (marcar: NO valen) |
|---|---|---|
| Índices | ES 0.06, NQ 0.02, YM 0.04, RTY 0.07 | — |
| Rates | ZT 0.05, ZF 0.10, ZN 0.19 | ZB 30Y 0.34 (largo, tick grande) |
| FX | 6E 0.07, 6J 0.08, 6B 0.12 | 6A/6C 0.21 |
| Energía | RB 0.10, HO 0.10, CL 0.21 | **NG gas 0.50** |
| Metales | GC 0.03, HG 0.16, SI 0.23 | — |
| Agrícolas | ZS soja 0.28, KC 0.24 | **ZC maíz 0.91, ZW trigo 0.67, SB azúcar 0.82** |

El coste de roll varía MUCHO: índices/rates/FX/oro son baratísimos (0.02-0.19%);
agrícolas y gas natural son caros (0.5-0.9%) — **no valdrían la pena por coste de roll**
y se excluyen del libro operable.

### Suelo recalculado (libro líquido diversificado, `costs_model`)

| | CFD (medido) | Futuros (estimado, libro líquido) |
|---|---|---|
| coste de mantener | **1.96%/año** (margen diario) | **0.19%/año** (roll+spread+comisión, sin margen) |
| coste total | 2.09%/año | 0.19%/año |
| suelo bruto (break-even) | 0.26 | **0.024** |
| **bruto requerido (net > 0.40)** | **0.66** | **0.424** |

**El vehículo baja el bruto requerido de 0.66 a ~0.42 (11× menos coste de mantener).**
→ **Criterio (1) SE CUMPLE** (0.424 < 0.50).

### Contraste contra la mejor evidencia PROPIA

H007 muestra A dio **bruto 0.370** (FX+metales, con 2008). Contra el nuevo listón
(0.424): sigue **corto por −0.054**. Pero la distancia se redujo mucho: en CFD era
0.370 vs 0.66 = **−0.29**; en futuros 0.370 vs 0.424 = **−0.054**. No pasa, pero de
"estructuralmente imposible" pasa a "al borde". (Y la industria reporta ~0.14 para
trend en nuestra ventana — muy por debajo de ambos; el bruto realista de trend es el
problema de fondo, no sólo el vehículo.)

**Parcial Bloque 1: criterio (1) cumplido. Falta el criterio (2) — amplitud (Bloque 2).**
