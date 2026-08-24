# Cerrar Ariel como no obtenible + test ciego del adversario

## Por qué

Ariel (1987) no se localizó en fuentes abiertas — pero el objetivo nunca fue Ariel sino un
EJE que NO le enseñamos al adversario, para probar si detecta un fallo no anticipado. Un
sustituto con conflicto de autoría real permite ese test.

## Qué cambia

- **Ariel → `no_obtenible`** en `data/papers/MANIFEST.md` (la cita se conserva; falta el
  archivo, no la referencia). `verify_papers.py` trata `no_obtenible` como estado VÁLIDO,
  distinto de `pendiente`. Nota en la ficha de H003: la extracción de la familia se hizo sobre
  McConnell & Xu, no sobre Ariel (program_verdict no cita a Ariel → nada que anotar allí).
- **Sustituto:** AQR "A Century of Evidence on Trend-Following Investing" (Hurst, **Ooi &
  Pedersen** 2017, `hurst2017_trend.pdf`, descargado + manifestado). Eje ciego: Ooi y Pedersen
  son 2/3 de MOP (2012) → no es una confirmación independiente.
- **Resultado del test ciego: NO DETECTADO**, sin interpretar a favor. Dos razones: (1) el eje
  ciego se reveló en el mismo prompt/modelo que corría el adversario → no hay detección
  espontánea auto-certificable; (2) límite ESTRUCTURAL: `adversarial.evaluate` sólo acepta las
  claves de `ATTACK_QUESTIONS` — un eje novel no tiene canal, así que aunque se notara no se
  registraría. Con los 8 ejes originales AQR pasaba como KEEP.
- **Remediación (rama "no detectado")** en `docs/extraction_defects.md`: mitigación 20 → **40**
  candidatos leídos íntegros; dos ejes NUEVOS en la estación 5: `autores_independientes` y
  `literatura_previa_posterior`. Registrado como EVIDENCIA del alcance del adversario (caza lo
  que enumeramos), no como aprobado/suspenso.

## Impacto

- `data/papers/MANIFEST.md`, `verify_papers.py`, `adversarial.py` (+2 ejes), `extract`/H003
  nota, `docs/extraction_defects.md`, `scripts/extraction_validation.py` (+ caso AQR), tests.
  NO se cablea la API. Suite 193 verde (+1 skip). Sin delta de spec.
