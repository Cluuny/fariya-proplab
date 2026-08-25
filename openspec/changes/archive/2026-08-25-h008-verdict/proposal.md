# H008 — cierre y correcciones de registro

## Why

El Bloque 4 de H008 (change `h008-block4`) dejó el veredicto como "NO PROMUEVE" con
una frase — "supera al nulo (los niveles de perfil llevan información vs fading
aleatorio)" — que NO está soportada: el benchmark nulo está construido de forma
defectuosa. Al aleatorizar el punto de entrada dentro del rango del día sin
reposicionar objetivo/stop, el POC puede quedar detrás de la entrada y la posición
nace con el objetivo del lado equivocado. El nulo no mide "sin información", mide
"geometría rota" (Sharpe -3.4 en todos los percentiles; imposible de acercarse a
cero). Por tanto la condición (3) del falsador NO discrimina, y la afirmación de
que el perfil "lleva información" debe retirarse del veredicto.

El veredicto real es más simple y más fuerte: **MUERTA**. El Sharpe ACTIVO de la
rama perfil (-0.067) está muy por debajo del listón 0.961, y con el supuesto de
fills realista (cruce ≥5 bps) EMPEORA a -0.986. No es viable bajo ningún supuesto.
H008 no murió por redundancia (la coincidencia del 26% descartó esa vía) — murió
porque la REGLA DE SUBASTA no funciona, con niveles de perfil o sin ellos.

Este change es de REGISTRO y CORRECCIÓN documental (sin cambio de comportamiento,
sin re-correr nada): sella el veredicto, corrige las afirmaciones defectuosas,
registra el nulo y el sesgo de exclusión como defectos de diseño (para fichas
futuras), añade H008 como novena familia al veredicto del programa, y añade un
noveno eje al adversario del pipeline que ninguno de los 8 actuales habría detectado.

## What Changes

1. **Veredicto MUERTA** en la ficha `hypotheses/H008_amt_volume_profile.yaml`:
   estado `muerta`, `intentos_realizados: 1`, `fecha_test` poblada. Falsador y
   `resultado_esperado` quedan CONGELADOS (no se tocan).
2. **Corregir D5** en `docs/h008_block4.md`: "¿el veredicto cambia entre
   supuestos? SÍ" → NO. Es no-viable bajo ambos (-0.067 y -0.986); el supuesto de
   fills afecta la MAGNITUD, no el veredicto.
3. **Registrar el nulo como test defectuoso** (como se hizo con la coincidencia mal
   emparejada): causa mecánica (geometría rota), consecuencia (condición (3) no
   discrimina), QUITAR del veredicto la frase "supera al nulo… llevan información",
   y documentar el diseño correcto (preservar la geometría) para fichas futuras.
4. **Registrar el sesgo de exclusión en D2**: los 73 episodios excluidos (341→268)
   no son aleatorios — sesgados hacia rango amplio. Diseño correcto futuro: definir
   episodios donde AMBOS niveles sean alcanzables por construcción.
5. **Matiz del veredicto**: H008 no murió por redundancia; murió porque la regla de
   fade de subasta pierde dinero (341 episodios / 18 meses / 2 instrumentos).
6. **Actualizar `docs/program_verdict.md`**: novena familia con veredicto + dos
   hallazgos empíricos limpios (niveles no redundantes; regla de subasta sin edge).
7. **Holdout**: nunca descargado, intacto. Registrarlo.
8. **Añadir eje al adversario** (`src/pipeline/adversarial.py`, estación 5):
   "¿el benchmark nulo preserva la geometría de la estrategia, o sólo aleatoriza
   el punto de entrada?"

## Impact

- Ficha `hypotheses/H008_amt_volume_profile.yaml` (estado → muerta; sub-bloque de
  cierre; falsador/resultado_esperado intactos).
- `docs/h008_block4.md` (D1/D5/D8 corregidos, nota D4 sobre nulo defectuoso, nota
  D2 sobre sesgo de exclusión).
- `docs/program_verdict.md` (novena familia).
- `src/pipeline/adversarial.py` (noveno eje `nulo_preserva_geometria`) + su test.
- Sin cambio de comportamiento de estrategia; nada se re-corre; holdout intacto.
