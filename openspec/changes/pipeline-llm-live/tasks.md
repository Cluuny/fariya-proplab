# Tareas

## 1. Diagnóstico
- [x] 1.1 Localizar el seam: extract.py:70 (`extract_from_pdf(llm=…)`), adversarial.py:37
  (`evaluate(findings)`); tests no usaban LLM ni mocks de respuestas reales.
- [x] 1.2 Correr verify_papers: 3 presentes (OFI, McConnell&Xu, Moskowitz), Ariel pendiente.

## 2. Extracción en sesión (validación manual asistida)
- [x] 2.1 Leer los 3 papers presentes y producir fichas con cita por cada numérico; regla (a)
  (numérico sin cita → null) y (b) (sin falsador → rechazo) respetadas.
- [x] 2.2 `scripts/extraction_validation.py` corre las fichas por las estaciones 4-5 REALES.

## 3. Validación contra casos conocidos
- [x] 3.1 Tabla campo por campo vs H001/H007 (Moskowitz), vs H003 (McConnell&Xu), vs el paper (OFI).
- [x] 3.2 Adversario detecta: MOP degradación post-2010; TOM = beta (crítico); OFI contemporáneo
  (crítico). Rechaza TOM y OFI, mantiene MOP con flag.

## 4. Criterio de aceptación + defectos
- [x] 4.1 Veredicto: la extracción FUNCIONA; se procede a cablear (change siguiente).
- [x] 4.2 `docs/extraction_defects.md`: D1 período 1965 vs 1985-2009; D2 Sharpe 1.2 sin cita;
  D3 falsador-inútil; D4 benchmark TOM = beta.

## 5. Seam listo para automatizar (sin conectar)
- [x] 5.1 `llm_client.py`: firma clara, credencial por env `PIPELINE_LLM_API_KEY`, structured
  output obligatorio, log por llamada, reintento con backoff, fallo visible.
- [x] 5.2 Tests con fakes + test de integración skip-si-no-hay-credencial. Suite 188 verde.

## 6. Coste estimado
- [x] 6.1 ~30k in + 2k out por paper; ~200 candidatos → ~$1-18 total; despreciable vs $125/mes
  de datos → condición de parada alcanzable.
