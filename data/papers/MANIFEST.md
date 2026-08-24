# MANIFEST — corpus de papers (fuente de verdad; los PDFs NO se versionan)

Una entrada por paper. `estado: presente` = el PDF está en `data/papers/` y su SHA256 cuadra;
`pendiente` = falta el archivo (obtenerlo con la receta de README.md). Verificar con
`python -m scripts.verify_papers`.

## moskowitz2012_tsmom.pdf
- título: Time Series Momentum
- autores: Moskowitz, Ooi & Pedersen
- año: 2012
- publicación: Journal of Financial Economics (Chicago Booth WP 79 / 12-21)
- DOI / arXiv: 10.1016/j.jfineco.2011.11.003 · SSRN 2089463
- obtenido de: https://ssrn.com/abstract=2089463
- fecha de descarga: 2026-08-24
- SHA256: 5675c7db5c17cf61a2286b4a55f7b76708bb09b2415bdee6d1d63d18d44bd9e4
- usado en: H001, H007
- estado: presente

## contkukanov2011_ofi.pdf
- título: The Price Impact of Order Book Events
- autores: Cont, Kukanov & Stoikov
- año: 2011
- publicación: preprint arXiv (publicado en Journal of Financial Econometrics, 2014)
- DOI / arXiv: arXiv:1011.6402 · 10.1093/jjfinec/nbt003
- obtenido de: https://arxiv.org/abs/1011.6402
- fecha de descarga: 2026-08-24
- SHA256: 40d1d5f0baf7944a1b9f4c12d3644038e657acf4a3dfb500b2057c2269edd25f
- usado en: OFI (validación + decaimiento)
- estado: presente

## mcconnell2008_tom.pdf
- título: Equity Returns at the Turn of the Month
- autores: McConnell & Xu
- año: 2008
- publicación: Financial Analysts Journal 64(2) (borrador SSRN de 2006)
- DOI / arXiv: 10.2469/faj.v64.n2.11 · SSRN 917884
- obtenido de: https://ssrn.com/abstract=917884
- fecha de descarga: 2026-08-24
- SHA256: c8ba3e3fde5a0077127608d4e22e9e2d41b3f7f07068dab5156c624627ddde26
- usado en: H003
- estado: presente

## ariel1987_tom.pdf
- título: A Monthly Effect in Stock Returns
- autores: Ariel
- año: 1987
- publicación: Journal of Financial Economics 18(1)
- DOI / arXiv: 10.1016/0304-405X(87)90066-3
- obtenido de: —
- fecha de descarga: —
- SHA256: —
- usado en: H003 (como CITA de origen, no como fuente extraída)
- estado: no_obtenible
- nota: >
    PDF no localizado en fuentes abiertas (búsqueda 2026-08). La CITA se conserva: el paper
    existe y respalda la genealogía del efecto TOM (Ariel 1987 -> McConnell & Xu 2008). Lo que
    falta es el archivo, no la referencia. La extracción de H003 se hizo sobre McConnell & Xu.

## hurst2017_trend.pdf
- título: A Century of Evidence on Trend-Following Investing
- autores: Hurst, Ooi & Pedersen
- año: 2017
- publicación: The Journal of Portfolio Management 44(1) (AQR Capital)
- DOI / arXiv: SSRN 2993026
- obtenido de: https://static.twentyoverten.com/.../A-Century-of-Evidence-on-Trend-Following-Investing.pdf
- fecha de descarga: 2026-08-24
- SHA256: 666f19c81a6932809fa69bb4f8746e531bb71912be7f554ce233eef73eb21d7c
- usado en: test ciego del adversario (sustituto de Ariel; NO es una hipótesis del proyecto)
- estado: presente
- nota: >
    Sustituto para el test ciego. Ooi y Pedersen son 2 de los 3 autores de Moskowitz-Ooi-
    Pedersen (2012): una "confirmación" del trend firmada por los mismos autores del hallazgo
    original NO es independiente. Ése era el eje ciego. Material de gestora (AQR), no arbitrado
    igual que un journal; backtest a un siglo sobre datos reconstruidos (calidad en décadas
    tempranas).
