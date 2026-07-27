# M6.2 completion criteria and research backlog

M6.2 is complete when all readily actionable crosswalk evidence has been
reviewed and every harder unassessed cell is assigned to a deterministic
research backlog. Completion does not mean that every historical host supports
every canonical operation, and it does not convert an unassessed cell into an
unsupported claim.

The generated source of truth is
`catalog/crosswalk/m62-completion.json`.

## Completion criteria

The report evaluates these conditions:

1. no `documented-but-not-reviewed` or high-confidence triage item remains;
2. every work-queue item has exactly one triage record and one backlog record;
3. provenance validation accepts every reviewed mapping;
4. queue and triage IDs match in deterministic order;
5. backlog IDs are unique, resolve to unassessed cells, and have no orphans.

Completion also requires normal and strict repository validation, current
generated artifacts, and byte-identical generator output for unchanged input.
Those checks protect the stored report from drifting away from its queue and
triage sources.

The current generated report satisfies every criterion, so M6.2 is complete.
The remaining backlog is research debt for later milestones, not unfinished
M6.2 review work.

## Backlog classes

- `completion-blocker`: primary evidence is already cataloged or triage
  confidence is high. These items must be resolved before M6.2 can complete.
- `deferred-research`: available evidence has ambiguous semantics or needs a
  focused historical interpretation. These are recommended for a post-M6.2
  evidence-expansion milestone.
- `archival-source-discovery`: the catalog lacks a sufficiently broad primary
  SDK, protocol, or programmer reference. These belong in future archive
  discovery.

Within those classes, backlog groups reuse the PR8 triage reasons:
`documented-but-not-reviewed`, `insufficient-semantics`,
`missing-primary-source`, `insufficient-sdk`, `ambiguous-operation`, and
`needs-additional-research`.

Each non-empty group records affected hosts, affected canonical operations,
research-effort distribution, expected value, recommended future milestone,
and the exact stable mapping IDs.

## Contributor workflow

Inspect the completion state and backlog:

```bash
ods crosswalk --completion
ods crosswalk --backlog
ods crosswalk --backlog --json
```

Choose work by reason group. For source-discovery groups, first catalog a
reproducible primary source; do not infer mappings from a missing SDK. For
deferred research, review the named semantic ambiguity against the canonical
operation definition. Any future reviewed mapping must still satisfy the
provenance validator.

After source, mapping, queue, or triage changes, regenerate and validate:

```bash
python3 tools/generate_crosswalk.py
python3 tools/generate_crosswalk_coverage.py
python3 tools/generate_crosswalk_work_queue.py
python3 tools/generate_crosswalk_triage.py
python3 tools/generate_crosswalk_completion.py

python3 tools/generate_crosswalk_completion.py --check
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools validate
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools validate --strict
```

Future milestones should consume stable backlog IDs and remove an item only
when its mapping is reviewed or its triage classification is deliberately
updated. Queue priority remains a research-order recommendation, not a support
claim or support-likelihood estimate.
