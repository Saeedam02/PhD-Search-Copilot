# Scoring

## Hard filters come first

A confirmed hard-constraint violation sets the opportunity to `FAIL`. No semantic score can override it.

Examples:

- user requires fully funded and official evidence says self-funded;
- country is explicitly excluded;
- deadline has passed;
- mandatory GRE is disallowed;
- required topic is absent after verification;
- application fee exceeds the configured maximum.

Unknown information can produce `REVIEW` rather than an invented pass/fail.

## Semantic score

For opportunities that are not hard-failed:

$$
S = \frac{\sum_i w_i s_i}{\sum_i w_i}
$$

with each $s_i \in [0,10]$.

Default dimensions:

| Dimension | Meaning |
|---|---|
| research_fit | overlap between candidate research and project problem |
| supervisor_fit | overlap with supervisor/lab agenda |
| methods_fit | overlap in methods/tools |
| skills_fit | evidence that candidate can execute the work |
| funding_quality | clarity and quality of funding package |
| location_fit | match to user preferences |
| deadline_practicality | realistic preparation time |
| competitiveness | candidate strength relative to stated requirements |
| evidence_quality | confidence/authority of supporting information |

The score is a prioritization aid, not a probability of admission.
