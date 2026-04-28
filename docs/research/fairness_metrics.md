# Fairness Metrics

- Demographic parity difference
- Equalized odds difference
- Selection rate by group
- Counterfactual sensitivity

## Working Definitions

- Demographic parity difference: maximum absolute difference in positive
  prediction or selection rates across protected groups.
- Equalized odds difference: disparity in true positive and false positive
  behavior across protected groups.
- Selection rate by group: share of rows receiving the favorable outcome per
  protected group.
- Counterfactual sensitivity: share of predictions that change after flipping
  sensitive-attribute proxy features.

The report generator treats deterministic metric outputs as the source of truth.
Gemini is used only to narrate and structure those already-measured results.
