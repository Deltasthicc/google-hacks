# Model Notes

The ML layer currently trains a logistic-regression baseline and evaluates
standard classification quality with accuracy, precision, recall, and F1. Bias
detection uses Fairlearn `MetricFrame` to compute per-group accuracy and recall.

Mitigation is implemented with Fairlearn `ThresholdOptimizer` using an
`equalized_odds` constraint. This is a post-processing mitigation, so it can
wrap an already-trained classifier and compare before/after fairness and utility
metrics.

Counterfactual checks currently focus on relationship-proxy feature flips. This
is intentionally narrow for the MVP and should be extended when new datasets add
different protected attributes or proxy columns.
