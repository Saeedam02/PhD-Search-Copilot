# Data model

## CandidateProfile

Structured evidence about the candidate: education, research interests, methods, skills, publications, projects, languages, and source files.

## Opportunity

Normalized PhD opportunity with funding, deadline, location, topics/methods, eligibility, evidence, verification state, fit scores, ranking score, priority, and pipeline status.

## EvidenceItem

A claim plus source URL/title, authority category, and verification flag. The data model intentionally keeps evidence separate from narrative analysis.

## ApprovalItem

Persistent record for an external action that cannot proceed without human authorization.

## RunRecord

Stores cycle start/end, counts, status, and error summary.

## Outcome

Stores application outcome and optional notes. Outcomes are factual history; they do not automatically modify scoring weights without explicit calibration logic.
