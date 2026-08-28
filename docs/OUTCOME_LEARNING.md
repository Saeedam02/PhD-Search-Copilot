# Outcome learning

The system stores actual outcomes and offers two levels of feedback:

1. `phd-agent analytics` computes deterministic counts by outcome and priority.
2. `phd-agent learn` asks the Outcome Learning Agent to look for cautious patterns and generate recommendations.

The learning agent does **not** silently change ranking weights. It may propose changes for human review, because small applicant-specific samples are noisy and selection outcomes have many hidden variables.
