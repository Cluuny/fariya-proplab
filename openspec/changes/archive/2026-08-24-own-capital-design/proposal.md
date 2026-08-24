# Fase de capital propio — DISEÑO (no se opera)

## Por qué

Cerrado el ciclo de descubrimiento (ocho familias, cero supervivientes), la siguiente fase
no es otra familia sino MEDIR la degradación backtest-vs-vivo con capital propio. Debe
diseñarse por escrito ANTES de tocar nada, para no distorsionar el objetivo (medición, no
ingreso) ni subestimar el riesgo nuevo (perder es perder).

## Qué cambia

Crea `docs/own_capital_phase.md`, SOLO DISEÑO:
- **(2.1)** El objetivo real primero: la fase NO genera ingreso (~$20/año esperado con $200,
  −$60 posible); mide degradación (slippage/latencia/fills/operación continua). Éxito =
  sobrevivir 12 meses con un factor de degradación medido, NO un retorno. Riesgo nuevo:
  capital real.
- **(2.2)** Qué cambia en el modelo de costes: bruto requerido a 15%/20% de vol (0.53/0.50)
  vs 0.65/0.64. CON la advertencia verificada de que subir la vol baja el listón sólo si
  viene de instrumentos más volátiles, NO de apalancamiento (coste/vol invariante). Y la
  verificación explícita: al listón más bajo (0.50) NINGUNA de las ocho sobrevive (H002 roza
  0.495 y muere por concentración). Baja el listón, no crea edge.
- **(2.3)** La pregunta abierta (qué se opera) documentada sin responder: reevaluar las 8 /
  buscar en el pipeline con el filtro nuevo / novena familia prohibida salvo vía pipeline.
- **(2.4)** Infraestructura mínima para vivo, sólo listada (claves, límites en código,
  kill-switch, log de órdenes, reconciliación diaria, alerta de degradación).

## Impacto

- Sólo `docs/own_capital_phase.md`. No se opera, no se deposita, no se conecta nada. Sin
  código, sin delta de spec.
