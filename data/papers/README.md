# data/papers/ — corpus de papers para la extracción del pipeline

## Por qué los PDFs NO están en el repo

Este repositorio es **PÚBLICO** (`Cluuny/fariya-proplab`) y los papers son material con
**copyright**. Redistribuirlos sería una infracción real. Por eso `.gitignore` excluye
`data/papers/*.pdf` y sólo versiona este `README.md` y `MANIFEST.md`. **Nunca** se commitea
un PDF aquí.

`MANIFEST.md` es la **fuente de verdad** de qué papers se usaron: título, autores, DOI/arXiv,
de dónde se obtuvo, fecha, SHA256 y en qué hipótesis se usó. El binario es reproducible desde
esa procedencia; el manifiesto es lo que se versiona.

## Cómo obtener los PDFs

- **Papers publicados:** Google Scholar con el título EXACTO entre comillas + `filetype:pdf`.
- **Moskowitz / Pedersen (AQR):** la biblioteca de investigación pública de AQR
  (aqr.com/Insights/Research) publica muchos de sus papers.
- **Preprints:** arXiv (p. ej. Cont-Kukanov-Stoikov = arXiv:1011.6402).
- **SSRN:** la página de abstract (ssrn.com/abstract=<id>) enlaza el PDF descargable.

## Dónde colocarlos y con qué nombre

Colocar el PDF en `data/papers/` con la convención FIJA (para que el pipeline lo referencie
sin ambigüedad):

    {primer_autor}{año}_{palabra_clave}.pdf

Ejemplos:

    moskowitz2012_tsmom.pdf
    contkukanov2011_ofi.pdf
    mcconnell2008_tom.pdf

El `año` es el de PUBLICACIÓN (no el del borrador SSRN). Después de colocarlo, correr
`python -m scripts.verify_papers` para comprobar el SHA256 contra el manifiesto (o para que
lo calcule si es la primera vez y falta registrarlo).

## Verificación

`scripts/verify_papers.py` — mismo patrón que `data/raw` y `data/raw_crypto`: el manifiesto se
versiona, los binarios no. Lista presentes/ausentes, verifica SHA256, y FALLA si un checksum
no cuadra o si detecta un PDF trackeado en git.
