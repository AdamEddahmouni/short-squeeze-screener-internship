# Phase 3C Confidence-Interval Policy

`phase_3c_interval_policy.v1` supports binomial Wilson score intervals at confidence `0.95` only. Arithmetic uses `Decimal` precision 50, `ROUND_HALF_EVEN`, fixed z `1.95996398454005423552`, and serialized bound quantum `0.000000000001`. No inverse-normal implementation, sampling, NumPy, SciPy, or floating-point fallback is used.

Zero denominators remain undefined and receive no interval. Intervals disclose whether the independence assumption is satisfied. They quantify arithmetic uncertainty under the stated policy; they do not repair dependence, selection limits, or lack of representativeness.
