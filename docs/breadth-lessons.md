# Lecciones de amplitud (universo y datos)

Dos hallazgos que se olvidan y se vuelven a pagar, más la estimación revisada para
la decisión de datos de futuros. Contexto: expansión de universo 9 → 17 (Bloques 1-2,
`data/universe_audit.md`, `data/universe_expansion.md`).

## 1. Los cruces FX son recombinaciones, no información nueva

`log(EURJPY) = log(EURUSD) + log(USDJPY)`. Igual GBPAUD, EURAUD, GBPJPY, AUDJPY: cada
cruce es una suma/resta de dos majors. En espacio de **log-retornos** viven
**exactamente** en el subespacio que ya generaban los majors → **cero bits de
información nueva**. Añadirlos no amplía el espacio de retornos alcanzable; sólo lo
re-parametriza.

De las incorporaciones del 9 → 18, sólo **tres** aportaron información real:
- **EURCHF** (+0.51 N_eff) — CHF es una divisa nueva (no estaba en el span).
- **HK50** (+0.39) — mercado y macro asiáticos nuevos.
- **plata (XAGUSD)** (+0.21) — metal distinto (aunque correlaciona con oro).

El resto (EURJPY/GBPJPY/AUDJPY/EURAUD/GBPAUD) fue recombinar lo que ya teníamos.

**Regla operativa:** antes de añadir un instrumento, preguntar **"¿es esto
construible a partir de lo que ya tengo?"**. Si sí (cruces FX, un índice ~idéntico a
otro como US30 vs SPX500), no aporta información aunque el conteo suba.

## 2. Limitación de N_eff como métrica

`N_eff = (Σλ)²/Σλ²` (participation ratio de los autovalores de la correlación)
**puede SUBIR al añadir combinaciones lineales que no aportan información**: los
autovalores redistribuyen su peso aunque el espacio generado sea idéntico. Es una
medida de *dispersión de la varianza entre ejes*, no de *dimensión informativa*.

Consecuencia: el **+1.6 de N_eff medido (3.73 → 5.32) SOBREESTIMA la ganancia
informativa real**. Buena parte vino de recombinaciones (los cruces FX) que no
amplían el span. La ganancia informativa honesta fueron sólo EURCHF + HK50 + plata.

**Regla operativa:** al evaluar candidatos, aplicar primero el test de
construibilidad del punto 1. Sólo después mirar el aporte a N_eff — y descontarlo
si el candidato es una recombinación.

## 3. Estimación revisada para datos de futuros (decisión pendiente)

La estimación previa (N_eff 7 → 12-13, techo de Sharpe ×1.8) estaba **inflada**: la
predicción de N_eff=7 para el universo ampliado falló contra el **5.32 medido** — un
error optimista de ~35%.

**Revisada, más honesta:** 8-10 instrumentos de **renta fija y energía** llevarían
N_eff de ~5.3 a **~8-9**, techo de Sharpe **×1.25-1.30**. Clave: **no son
recombinaciones** — no puedes construir el Bund con EURUSD y SPX500, así que su aporte
marginal debería parecerse a EURCHF/HK50 (información nueva), **no a AUDJPY**
(recombinación). Sigue siendo:
- la **mayor ganancia de amplitud disponible**, y
- la **única vía a la clase de activo donde la industria atribuye los retornos de
  trend** (renta fija y materias primas), que nuestro universo spot/CFD no tiene.

Pero es un **incremento (~×1.3), no un desbloqueo (×1.8)**. Ajustar el caso de
inversión a esa escala antes de pagar por datos. Recordar además que Dukascopy daily
NO cubre rates de forma usable (`data/universe_audit.md`): pagar datos de futuros es
el único camino real a esa amplitud.
