# Tareas

## 1. Ariel no obtenible
- [x] 1.1 MANIFEST: Ariel `estado: no_obtenible` + nota + usado_en (cita, no fuente extraída).
- [x] 1.2 `verify_papers.py` trata `no_obtenible` como VÁLIDO (no falla), distinto de `pendiente`.
- [x] 1.3 Nota en H003 (extracción sobre McConnell & Xu, no Ariel); program_verdict no cita Ariel.

## 2. Sustituto para el test ciego
- [x] 2.1 AQR "A Century of Evidence on Trend-Following Investing" (Hurst, Ooi & Pedersen 2017)
  descargado a data/papers/ + entrada en MANIFEST (autores compartidos con MOP anotados).

## 3. Correr y reportar sin interpretar a favor
- [x] 3.1 Estaciones 4-5 con el prompt/ejes existentes; resultado del eje ciego reportado tal cual.
- [x] 3.2 Clasificación: **NO DETECTADO** (contaminación del prompt + límite estructural del
  findings dict). Sin afirmar detección espontánea.

## 4. Ajustar mitigación según resultado
- [x] 4.1 Rama "no detectado": mitigación 20 → 40 candidatos leídos íntegros.
- [x] 4.2 Dos ejes nuevos en la estación 5: `autores_independientes`, `literatura_previa_posterior`.
- [x] 4.3 Registrado como EVIDENCIA del alcance del adversario, no aprobado/suspenso.

## 5. Tests
- [x] 5.1 `no_obtenible` estado válido; Ariel en el manifiesto real; ejes nuevos presentes y
  no-críticos. Suite 193 verde.
