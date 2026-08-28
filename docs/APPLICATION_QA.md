# Application QA

The QA Agent checks:

- every candidate achievement is supported by the candidate profile;
- professor/lab claims are supported by verified research evidence;
- no paper is described as "read" unless its content was actually provided/retrieved;
- dates, degrees, titles, and publication status are consistent across documents;
- language is position-specific rather than generic praise;
- missing requirements are clearly marked instead of fabricated;
- the motivation explains a concrete research intersection;
- output files contain no placeholders unless explicitly flagged.

QA returns a structured verdict: `pass`, `needs_revision`, or `block`.
