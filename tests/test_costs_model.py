"""test_costs_model.py — the cost-floor decision tool (Bloque A)."""
from src import costs_model as cm


def test_reproduces_measured_floor():
    # H001-A operating point: gross 1.71, turnover 8.8 → ~1.9%/año total (medido 1.91).
    b = cm.annual_cost(1.71, 8.8)
    assert 0.017 <= b.total <= 0.021
    assert b.margin > 5 * b.spread          # el margen domina (~92%)


def test_required_gross_sharpe():
    # break-even ~0.24, requerido (net 0.4) ~0.64 con los parámetros actuales.
    assert abs(cm.break_even(0.08, 1.71, 8.8) - 0.24) < 0.03
    assert abs(cm.sharpe_bruto_requerido(0.08, 1.71, 8.8, 0.4) - 0.64) < 0.03


def test_margin_scales_linearly_with_gross():
    a = cm.annual_cost(1.0, 0).margin
    assert abs(cm.annual_cost(2.0, 0).margin - 2 * a) < 1e-12


def test_higher_turnover_needs_higher_gross_sharpe():
    lo = cm.sharpe_bruto_requerido(0.08, 1.5, 10)
    hi = cm.sharpe_bruto_requerido(0.08, 1.5, 75)   # reversión corto plazo
    assert hi > lo + 0.05                            # el spread de rotación pesa


def test_required_gross_by_duty_cycle():
    from src import costs_model as cm
    assert abs(cm.sharpe_bruto_requerido_duty(1.0) - 0.64) < 1e-9   # always-in
    assert abs(cm.sharpe_bruto_requerido_duty(0.5) - 0.52) < 1e-9
    assert abs(cm.sharpe_bruto_requerido_duty(0.1) - 0.424) < 1e-9  # low duty → floor ~umbral
    # monotone: lower duty → lower required gross (margin saving)
    assert cm.sharpe_bruto_requerido_duty(0.1) < cm.sharpe_bruto_requerido_duty(1.0)


def test_low_duty_raises_the_active_bar():
    from src import costs_model as cm
    # CORRECCIÓN: bajar el duty SUBE el Sharpe activo requerido (0.40/√duty + 0.245).
    assert abs(cm.sharpe_activo_requerido(1.0) - 0.645) < 1e-3
    assert abs(cm.sharpe_activo_requerido(0.2) - 1.139) < 1e-3
    assert cm.sharpe_activo_requerido(0.1) > cm.sharpe_activo_requerido(1.0)   # sube, no baja
