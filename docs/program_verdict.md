# Veredicto del programa — cierre del ciclo del universo CFD

El ciclo del universo CFD (17 instrumentos spot/CFD, EOD, Dukascopy) terminó. Ninguna
hipótesis sobrevivió. Esto NO es un fracaso: es lo que un programa con falsadores
honestos, suelo de costes medido y veredictos sin adornos produce cuando el vehículo y
los datos no dan un edge que supere el suelo. El cierre merece documentarse
independientemente de lo que se decida sobre futuros (`docs/futures_case.md`).

## Las hipótesis, con veredictos y números

| # | hipótesis | familia | veredicto | números clave |
|---|---|---|---|---|
| H001 | TSMOM (9 instrumentos) | trend | **muerta** (falsada) | neto A 0.078 / B 0.135; bruto ~0.24-0.31; el swap diario lo hundió |
| H003 | Turn-of-the-month | seasonality | **muerta** (falsada) | el efecto NO existe en índices 2011-2023 (concentración pooled −3.0 bps/día); Sharpe 0.26 = media del nulo |
| H007 | TSMOM (17, ampliado) | trend | **muerta** (falsada) | neto A 0.184 / B 0.040; **bruto A 0.370** (el mejor de trend); calibración del marco UNDERPOWERED |
| H002 | Carry (diferencial de tasas) | carry | **rechazada** (concentración) | **neto 0.282 — el mejor del proyecto**, muere por umbral no por falsador; N_eff FX 3.41, casi todo short-JPY (prima de crash) |
| H005 | Reversión a la media (índice) | mean-rev | **rechazada-por-coste** | turnover 50-100× → bruto requerido ~0.78; plausible 0.3-0.5 |
| H006 | Intermarket / macro | intermarket | **rechazada-por-coste** | price-based, duty 100% → requerido 0.64; sin evidencia de bruto alto |
| — | COT (posicionamiento, no-precio) | mean-rev | **cribada-fuera** | Sharpe activo del fade ≈ 0 (agrupado −0.02, IC cruza 0); signo del mecanismo roto en 5/8 |
| H004 | Volatility risk premium | vol-premium | **fuera por datos** | necesita opciones/vol implícita |

Tres testeadas hasta el veredicto (H001/H003/H007), tres+COT cribadas por
coste/concentración/evidencia, una fuera por datos. **Cero supervivientes.**

## Las cuatro conclusiones MEDIDAS del programa

1. **Suelo de costes (CFD): break-even 0.24, bruto requerido 0.64** (net > 0.4). Dominado
   por el margen diario (0.42 bp/día ≈ 1.96%/año, ~92% del coste). `docs/cost_floor.md`.
2. **El duty cycle bajo NO ayuda.** El requerido de serie completa baja con el duty, pero
   el alcanzable se diluye igual (`Sharpe_whole ≈ Sharpe_activo·√duty`) → el **Sharpe
   activo requerido SUBE**: 0.40/√duty + 0.245 = **1.14 a duty 20%**, 1.51 a 10%. Ser
   selectivo no baja el coste efectivo del edge. `docs/queue_triage.md`.
3. **Ninguna familia accesible produce 0.64 de bruto.** Los mejores: carry 0.495 (bruto),
   trend 0.370 (H007-A) — ambos cortos. La industria da 0.14 para trend en nuestra
   ventana, pero eso es NETO de comisiones de gestión (~2%, "2 y 20"); **bruto de
   comisiones ≈ 0.32** — comparable a nuestra H007-A 0.370, no 3× por debajo. El edge no
   está en lo que podemos operar hoy, pero el hueco realista es de magnitud, no estructural
   (ver `docs/futures_case.md`, corrección de comparabilidad del Sharpe). Nota metodológica:
   nuestros Sharpes YA son de exceso (P&L de precio, sin interés sobre colateral en cuenta
   fondeada), así que son directamente comparables al Sharpe de exceso de la industria.
4. **Las restricciones son de DATOS y VEHÍCULO, no de MÉTODO.** El método funcionó: los
   falsadores mataron lo que tenían que matar, el suelo de costes cribó el resto, los
   veredictos fueron honestos (incluidas expectativas comprometidas refutadas). Lo que
   falta es acceso a clases de activo y a un vehículo con edge real, no un método mejor.

## Restricciones identificadas (el mapa de lo que falta)

- **Sin rates** — la clase donde la industria atribuye buena parte del trend; Dukascopy
  no tiene CFDs de bonos usables (`data/universe_audit.md`).
- **Sin energía** — CFDs esparsos (Brent y WTI ~25% faltante).
- **Sin opciones** — mata H004 (volatility risk premium) por datos.
- **Sin intradía con volumen real** — mata AMT/volume profile.
- **Margen del CFD 0.42 bp/día** — el suelo estructural; los futuros lo eliminan
  (Bloque de futuros: bruto requerido 0.66 → 0.42), pero el edge sigue sin resolver.

## Cierre

El universo CFD dio un NO limpio y medido en cada frente. El programa hizo su trabajo:
convirtió "¿funciona X?" en números falsables y mató cada idea por la razón correcta,
antes de arriesgar capital. La pregunta abierta ya no es de método sino de acceso:
rates/energía/opciones/intradía, y un vehículo (futuros) sin el margen diario. Ese es el
tema del `docs/futures_case.md` — con veredicto GO frágil, verificable con 1 mes de datos.
