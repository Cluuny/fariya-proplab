# Ajustes finales a H008 antes de descargar datos

## Por qué

La ficha de H008 está bien construida; tres ajustes la dejan aprobada. SÓLO la ficha — cero
código, cero descargas.

## Qué cambia (en `hypotheses/H008_amt_volume_profile.yaml`)

1. **Falsador (1) corregido** — se disparaba casi por CONSTRUCCIÓN: con T~150 y S~0.5,
   SE(Ŝ)≈0.087 → el IC del Δ sólo no cruza 0 si |Δ|≳0.17, una diferencia enorme entre dos ramas
   que sólo cambian los niveles. Se separa: **(1)** Δ≤0 con IC que NO cruza 0 → MUERTA redundante;
   **(1b)** IC cruza 0 → UNDERPOWERED en la dimensión incremental (NO muerta). **(2)**
   coincidencia>80% y **(3)** activo<p95 se quedan y son INDEPENDIENTES: el veredicto global puede
   ser MUERTA por (2)/(3) aunque (1) quede underpowered. Mismo defecto ya corregido en H003 y en la
   calibración de H007.
2. **Probabilidad previa registrada** (`resultado_esperado.probabilidad_previa`): BAJA por la
   MAGNITUD del listón (Sharpe activo ~1.14 = >2× el mejor del proyecto 0.495), sin literatura
   arbitrada. Se corre para CERRAR la duda de la familia, no esperando que pase — para que el
   resultado no sorprenda.
3. **Datos**: ETHUSDT desde el inicio (T raw 73→146/año, EFECTIVA ~81 tras ρ≈0.8; ~162 sobre 2
   años, marginalmente > umbral 150; concesión documentada, aceptable para test de redundancia).
   Verificar si bookTicker hace falta o basta aggTrades (~10× más ligero). MEDIR 1 día
   (GB/tiempo/RAM — el cuello es RAM) antes de bajar 2 años. HOLDOUT separado FÍSICAMENTE al
   descargar (`data/raw_crypto_holdout/`), corte **2024-03-01** registrado ahora. Muestra planeada
   2022-09 → 2024-08.

Todo como enmienda `pre_ejecucion` (intentos_realizados=0, fecha_test=null). QUEUE.md actualizado.

## Impacto

- Sólo fichas/docs. Cero código, cero descargas. Suite 193 verde (sin cambios de código). Sin
  delta de spec. Tras esto: proceder a la descarga (medir 1 día primero). No se re-revisa la ficha.
