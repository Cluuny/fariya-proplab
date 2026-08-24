# Veredicto de programa final — ambos ciclos (CFD y cripto)

## Por qué

`docs/program_verdict.md` sólo cubría el ciclo CFD. Con el order flow cerrado, el programa
tiene DOS ciclos completos y ocho familias con veredicto. Este es el documento que se
consultará dentro de un año; debe estar completo, con números, y sin adornos.

## Qué cambia

Reescribe `docs/program_verdict.md` para cubrir ambos ciclos:
- **(1.1)** Las OCHO familias con veredicto y números (H001/H003/H007 trend+seasonality,
  H002 carry, H005 mean-rev, H006 intermarket, COT, OFI).
- **(1.2)** Conclusiones medidas de ambos ciclos: suelo CFD 0.24/0.64; duty bajo no ayuda;
  ninguna familia produce el bruto requerido; cripto coste/riesgo favorable (0.013-0.032 vs
  0.063 MES) pero listón absoluto 0.65 idéntico al CFD; market making imposible a VIP0;
  motor validado externamente (H001 0.08-0.14 vs SG CTA Trend 0.14).
- **(1.3)** Los dos hallazgos empíricos PROPIOS como resultados: (a) ĉ≈2.5-3.0 vs 0.45 del
  paper (book display sobreestima ~5-6× la profundidad efectiva; estable a través de escalas);
  (b) el trade imbalance no queda subsumido en cripto (precios más impulsados por trades).
- **(1.4)** Corrección metodológica: los "Sharpe implícito" del decaimiento no son creíbles
  como NIVELES (BR inflado con autocorrelación); el RATIO señal/coste sí (0.009-0.039);
  consistencia 1/√BR verificada (×42 ≈ √(86400/48)). En adelante usar el ratio.
- **(1.5)** La condición de parada, textual, declarada cumplida (8 de 8); registrado que NO
  se buscó una novena familia.

## Impacto

- Sólo `docs/program_verdict.md`. Sin código, sin datos, sin delta de spec.
