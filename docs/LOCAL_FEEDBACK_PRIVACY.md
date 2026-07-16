# Local Feedback and Patient Data Boundary

Version: 0.1 (Draft)

Patient responses and real personal or medical information are local-only inputs. They may inform improvement of Knowledge and Fact definitions, but they must never be committed, pushed, published through GitHub Pages, or embedded in a Custom GPT knowledge snapshot.

## Allowed local use

Local processing may:

- detect missing Facts, question groups, answer choices, and safety transitions;
- count recurring response patterns;
- produce de-identified aggregate candidate Knowledge and Facts;
- run private evaluation before the raw material is deleted or archived locally.

## Publishable output

Only a generalized candidate may move from the local feedback boundary into the repository. It must:

- contain no name, identifier, contact detail, exact date, account number, or uncommon identifying combination;
- contain no raw patient quote or reversible paraphrase;
- use aggregate counts only when the cohort is large enough to avoid singling out a person;
- state `contains_raw_patient_text: false`;
- state `deidentification_status: deidentified_aggregate`;
- state `source_type: local_feedback_aggregate`;
- remain `status: research_only` and `review_status: unreviewed` until review.

Synthetic simulation fixtures are permitted in `simulation/` and `examples/` only when they are invented test cases and are clearly described as synthetic. Real conversations must use ignored local paths such as `local-data/`, `feedback/raw/`, or `playground/sessions/`.

## Custom GPT boundary

The public Knowledge GPT Action only reads static Knowledge, Fact, question-group, and safety-rule resources from GitHub Pages. GitHub receives no interview answers through this Action.

An optional separately hosted feedback Action may receive structured end-of-test metrics only after a separate explicit agreement. It rejects raw answers, free text, transcripts, uploaded material, demographics, contact information, direct identifiers and unexpected fields. It does not receive data when the user declines, and it does not observe abandoned sessions. Its write credential and administrator credential are separate secrets, and row-level retention is bounded.

The ChatGPT conversation itself is outside this repository. Test users must be told not to enter directly identifying information and must follow the privacy terms applicable to their ChatGPT account.
