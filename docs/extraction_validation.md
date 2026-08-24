# Validación de la extracción del pipeline (estaciones 4-5) — corrida en sesión

Validación manual asistida: el LLM (esta sesión) leyó los PDFs de `data/papers/` y produjo
fichas, respetando las dos reglas anti-alucinación ya implementadas. El objetivo es la CALIDAD
de la extracción, no la automatización. Reproducible: `python -m scripts.extraction_validation`.

Diagnóstico del seam: estación 4 en `src/pipeline/extract.py:70` (`extract_from_pdf(llm=…)`,
levanta NotImplementedError sin `llm`); estación 5 en `src/pipeline/adversarial.py:37`
(`evaluate(findings)`; el adversario LLM rellena `findings`). Los tests no usaban LLM ni mocks
de respuestas reales — sólo verificaban la lógica de validación/compuerta con dicts a mano.

## Resultado de las estaciones (reales)

| paper | est. 4 extracción | est. 5 adversaria |
|---|---|---|
| moskowitz2012_tsmom | ACEPTADA | **KEEP** (flag no crítico: degradación post-pub) |
| mcconnell2008_tom | ACEPTADA | **REJECT** (crítico: benchmark = beta de mercado) |
| contkukanov2011_ofi | ACEPTADA | **REJECT** (crítico: R² CONTEMPORÁNEO, no predictivo) |

El adversario rechaza independientemente TOM (beta) y OFI (contemporáneo) — las dos familias
que murieron en el proyecto por EXACTAMENTE esas razones. Señal fuerte de que la estación 5
funciona.

## Campo por campo — Moskowitz, Ooi & Pedersen (2012) vs H001/H007

| campo | ficha manual (H001/H007) | ficha extraída | ¿coincide? | comentario |
|---|---|---|---|---|
| n_instrumentos | 9 / 17 (adaptado) | 58 (Abstract, §1) | parcial | el paper es 58; nuestras fichas documentan la adaptación a spot/CFD |
| regla_entrada | long si ret_12m>0, short si <0 | sign(ret_12m), k=12 h=1 (eq.5) | **SÍ** | exacto |
| sizing | vol-inversa a 8% de PORTAFOLIO | vol-inversa a 40% por posición (§4.1) | método SÍ, objetivo NO | 8% = adaptación a cuenta prop |
| periodo_original | **1965-2009** | **1985-2009** (§2.3 p.15; §4.1 p.16) | **NO** | DEFECTO: el paper reporta post-1985; 1965 es sólo robustez de datos extendidos |
| sharpe/bruto | **1.2** | **null** (en Figure 2, no en texto) | **NO** | DEFECTO: la ficha manual afirmó 1.2 sin cita de ubicación verificable |
| falsador | Sharpe neto < 0.2 → muere | Sharpe neto < 0.2 → muere | SÍ | firable en ambas |

## Campo por campo — McConnell & Xu (2008) vs H003

| campo | H003 manual | ficha extraída | ¿coincide? | comentario |
|---|---|---|---|---|
| universo | 3 índices (SPX/GER40/JPN225) | CRSP mercado US (VW/EW) | parcial | H003 adapta a 3 índices |
| ventana | [-1,+3] (4 días) | [-1,+3] (4 días) (Abstract) | **SÍ** | exacto |
| periodo_original | (H003 testeó 2011-2023) | 1987-2005 primario; 1926-2005 | — | nuestro test es OOS post-publicación |
| efecto | −3.0 bps/día, AUSENTE | VW +0.14%/día TOM vs −0.01% (p.2) | — | hallado 1987-2005; ausente en 2011-2023 → degradación |
| benchmark | nulo aleatorio (4 días) | — | — | el adversario marca beta de mercado (long-only en la ventana) |
| falsador | exceso sobre nulo | exceso sobre nulo | SÍ | firable |

## Campo por campo — Cont, Kukanov & Stoikov (no hay ficha manual → contra el paper)

| campo | paper | ficha extraída | ¿coincide? |
|---|---|---|---|
| R² | ~0.65 (§3.2) | 0.65 (marcado como R², no Sharpe) | **SÍ** |
| n acciones | 50 (§3.1) | 50 | **SÍ** |
| período | abril 2010 (§3.1) | abril 2010 | **SÍ** |
| λ (impacto ∝ 1/profundidad) | ≈1 (§2.3, Fig 4) | ≈1 | **SÍ** |
| contemporáneo vs predictivo | CONTEMPORÁNEO | contemporáneo (marcado) | **SÍ** |

Coincide con el paper en todo, y con nuestra propia validación del OFI en cripto (R² 0.638,
λ −1.17). El extractor marcó correctamente que el 0.65 es R² (no Sharpe) y contemporáneo.

## Atención especial (lo pedido)

- **bruto_reportado + cita:** en los tres, los numéricos que se emitieron apuntan a un sitio
  que SÍ los contiene (n=58 §1; R²=0.65 §3.2; períodos citados). El Sharpe de MOP NO se emitió
  porque está en una figura → la regla (a) hizo su trabajo (no se inventó 1.2).
- **FALSADOR firable:** los tres falsadores extraídos PUEDEN dispararse (cortes de Sharpe/R²/
  exceso-sobre-nulo). Un falsador tipo "si no funciona se descarta" pasaría el esquema y sería
  inútil — es el defecto que la validación automática NO atrapa; por eso este paso lo revisa
  un humano/adversario, no sólo el esquema.
- **MOP degradación:** el adversario marcó `degradacion_post_pub` (documentada post-2010).
- **OFI contemporáneo:** el adversario marcó `contemporaneo_vs_predictivo` como CRÍTICO → reject.

## Criterio de aceptación (comprometido antes de correr)

**La extracción FUNCIONA en lo sustancial** (estructura, regla, mecanismo, ventana, n, λ, R²,
período-en-paper correctos; disciplina anti-alucinación operativa; adversario detecta beta y
contemporáneo). Se procede a cablear el seam para la corrida real sobre arXiv (change
siguiente, con API key). **Las discrepancias encontradas son DEFECTOS de nuestras fichas
MANUALES** (período 1965 vs 1985-2009; Sharpe 1.2 sin cita), documentados en
`docs/extraction_defects.md` y a corregir antes de procesar candidatos nuevos.

## Coste estimado (item 6)

Por paper que llega a extracción: texto del PDF ~10-16k tokens de entrada + prompt ~1k;
salida ficha ~1k. La estación 5 (adversario) re-lee → otros ~12-16k in + ~1k out. **≈ 30k in +
2k out por paper.** Pero la extracción SÓLO corre sobre candidatos que pasan las estaciones
2-3 (triaje sobre abstract, ~0.6k tokens c/u). De 200 procesados, ~15-30 llegan a extracción.

Coste de vida del pipeline (200 candidatos):
`200 × 0.6k (triaje) + ~25 × 32k (extracción+adversario) ≈ 0.9M in + 60k out.`

| modelo | $/M in · out | coste total (200 candidatos) |
|---|---|---|
| Haiku-class | ~$1 · $5 | **~$1.2** |
| Sonnet-class | ~$3 · $15 | ~$3.6 |
| Opus-class | ~$15 · $75 | ~$18 |

Mensual (cron mensual, ~10-20 candidatos/mes, 2-3 extracciones): **céntimos a ~$2/mes**.
**El coste del LLM es despreciable frente al presupuesto de datos de $125/mes.** La condición
de parada (200 candidatos) es holgadamente alcanzable dentro del presupuesto: el cuello es el
DATO, no el modelo.

## Cómo activar la automatización (seam)

`src/pipeline/llm_client.py`: exportar la credencial en `PIPELINE_LLM_API_KEY` (NUNCA en el
repo), opcional `PIPELINE_LLM_MODEL`. `extract_with_retry(llm_call, id, pdf_text)` valida
contra el esquema, reintenta con backoff y falla VISIBLEMENTE si no valida; loguea cada
llamada (prompt/respuesta/tokens) en `results/pipeline/llm_logs/`. `make_api_extractor()` es
el adaptador a cablear en el change siguiente (structured output obligatorio).
