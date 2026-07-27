# M6.2 PR8 — Remaining evidence triage

M6.2 remains in progress. PR8 classifies research work; it does not change
mapping status, evidence coverage, or work-queue priority.

The generated artifact is `catalog/crosswalk/triage.json`. Every current
work-queue item appears exactly once and retains its queue ID, host, operation,
priority, and reasons.

## Methodology

Each unassessed cell was compared with the host's cataloged archives, census
entries, reviewed neighboring operations, and the canonical operation
definition. Triage records three independent judgments:

1. the primary reason the cell remains unassessed;
2. estimated evidence-research effort;
3. confidence that sufficient additional evidence can be found.

These judgments are research guidance. They are not support claims, mapping
status, or changes to work-queue scoring.

## Categories

| Category | Meaning |
| --- | --- |
| `documented-but-not-reviewed` | Cataloged primary documentation names the behavior, but focused semantic review remains. |
| `insufficient-semantics` | Nearby commands or fields exist, but their documented behavior does not establish the canonical operation. |
| `missing-primary-source` | Observed door code exists without a primary SDK or protocol contract. |
| `insufficient-sdk` | The cataloged public SDK does not expose an interface for the operation. |
| `ambiguous-operation` | Status-related evidence does not clearly implement the canonical host-visible activity description. |
| `needs-additional-research` | Primary material exists, but the relevant interaction has not been isolated and interpreted. |

Exactly one category is assigned to each triage item.

## Effort

Effort estimates describe evidence research, not adapter implementation:

| Effort | Expected research |
| --- | --- |
| `trivial` | A direct citation is already isolated and only confirmation remains. |
| `small` | One known document section or example needs focused review. |
| `moderate` | Several documents, commands, or source paths must be correlated. |
| `extensive` | New primary material must be located or a broad archive/source investigation is required. |

## Confidence

| Confidence | Meaning |
| --- | --- |
| `high` | Current primary documentation already points directly to likely sufficient evidence. |
| `medium` | Additional evidence is plausible, but current material is incomplete or ambiguous. |
| `low` | The public interface omits the behavior or no primary contract is currently cataloged. |

Confidence estimates whether sufficient evidence can be found. They do not
estimate whether a host supports the operation.

## Current distributions

The committed triage contains 34 items.

Categories:

- `documented-but-not-reviewed`: 2
- `insufficient-semantics`: 3
- `missing-primary-source`: 18
- `insufficient-sdk`: 6
- `ambiguous-operation`: 3
- `needs-additional-research`: 2

Effort:

- `trivial`: 0
- `small`: 2
- `moderate`: 8
- `extensive`: 24

Confidence:

- `high`: 2
- `medium`: 6
- `low`: 26

## Host summaries

| Host | Reviewed | Remaining | Documentation | Recommendation | Next opportunity |
| --- | ---: | ---: | --- | --- | --- |
| ABBS | 7 | 2 | comprehensive | medium | Review ARexx host-command dispatch and normal script completion. |
| AEDoor | 8 | 1 | comprehensive | low | Seek a status-text setter beyond the reviewed public AEDoor calls. |
| AmBoS | 4 | 5 | comprehensive | high | Review `bbs_close` and `bbs_open`/`ExternInfo` for lifecycle exit and caller identity. |
| Door-IO | 5 | 4 | targeted | low | Seek host-specific wrapper documentation; the public library exposes no remaining operation. |
| FAME | 8 | 1 | comprehensive | medium | Check developer-only commands for node action-string mutation. |
| Paragon | 7 | 2 | limited | medium | Locate a primary MAXs command table for time and activity fields. |
| UCDoor | 8 | 1 | comprehensive | low | Research the underlying MAXs protocol for activity-description mutation. |
| WWBBS | 0 | 9 | observational | low | Locate a primary ARexx programmer reference or protocol definition. |
| Zeus | 0 | 9 | observational | low | Locate and catalog a primary door SDK or protocol specification. |

## Contributor workflow

Start with the host summaries:

```bash
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools crosswalk --triage
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools crosswalk --triage --host ambos
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools crosswalk --triage --json
```

Prefer high-confidence, small-effort items with a cataloged primary source.
Before changing a mapping, inspect the cited archive manifest and the canonical
operation definition. If the evidence remains ambiguous, leave the mapping
unassessed and refine the triage only when new evidence justifies it.

After a future evidence batch changes the queue, update the explicit triage
assignment and regenerate:

```bash
python3 tools/generate_crosswalk_triage.py
python3 tools/generate_crosswalk_triage.py --check
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools validate
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools validate --strict
```

Generation fails if a queue item has no triage assignment or if an assignment
no longer belongs to the queue.
