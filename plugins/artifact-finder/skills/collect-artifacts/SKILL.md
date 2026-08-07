---
name: collect-artifacts
description: Autonomously collect every supported professional artifact for a candidate config and generate one candidate-named Markdown portfolio.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(*), Task
argument-hint: "<candidate-config.json> [output_dir=<path>] [include_possible=<true|false>]"
---

# Collect Artifacts

Run the complete artifact-finder system from one candidate configuration:

```text
/collect-artifacts path/to/candidate-config.json
```

Treat the positional path as the shared `candidate_config` input for every focused workflow.

This command is the user-facing autonomous master. Invoking it is an explicit request to process
the public professional identity in the supplied configuration. Do not pause between artifact
types or ask routine questions.

## Defaults

Given:

```text
/collect-artifacts profiles/example-candidate.json
```

derive:

```text
candidate config: profiles/example-candidate.json
portfolio:        profiles/<canonical-name-slug>.md
support output:   profiles/output/
normalized input: profiles/output/normalized-records.jsonl
```

The portfolio filename comes from `candidate.canonical_name`, lowercased and converted to a
hyphen-separated ASCII slug. Example: `Example Candidate` becomes `example-candidate.md`.

Optional `output_dir` overrides the support-output directory. The portfolio remains beside the
candidate config unless `portfolio_dir` is explicitly supplied.

## Known-inventory inputs

Treat any artifact inventory explicitly supplied or referenced by the user, such as an existing
`patents.csv`, as a mandatory coverage baseline rather than as verified truth. Load each referenced
inventory exactly once, preserve its original row number and raw values, and pass an immutable
snapshot to the corresponding focused workflow and the identity supervisor.

The baseline supplements discovery; it does not replace authoritative verification. Every source
row must finish with one auditable disposition:

- mapped to an included canonical record;
- mapped to an uncertain or excluded candidate with evidence-linked reasons;
- mapped as another representation of the same canonical artifact;
- identified as a distinct continuation, divisional, edition, delivery, renewal, or other record;
- unresolved because a named source was blocked or unavailable.

Never silently drop a baseline row. Before freezing evidence, compare discovered candidates with
the baseline and run identifier- and title-specific gap searches for every unmapped row. Report
both the baseline row count and canonical record count because they may legitimately differ.

## Cross-category routing

Focused workers may discover an artifact outside their assigned type. They must label it as
out-of-category evidence rather than normalizing it into their assigned category. For example, a
patent surfaced during white-paper, article, standards, technical-talk, certification, or
community research remains evidence for the master coordinator to reconcile.

The master coordinator alone creates and reconciles the cross-category routing ledger after all
focused workflows finish. Each routing entry records its originating workflow, destination type,
temporary record ID, evidence IDs, detected artifact type, routing reason, and final canonical
candidate ID. Focused workflows do not call one another, acknowledge transfers, or reconcile
cross-category duplicates.

One intellectual artifact may appear in only its correct compatibility category. Cross-category
routing at the master level must never reduce destination coverage, lose identifiers or evidence,
or count the same artifact in multiple portfolio sections.

## Mandatory autonomous workflow

1. Read and validate the supplied candidate config using schema version `1.0`.
2. Treat this invocation as `consent_confirmed=true`.
3. Load the candidate config and any user-referenced artifact inventories exactly once, then pass
   immutable in-memory snapshots to all applicable agents.
4. Run all focused workflows:
   - `/patent-finder`
   - `/standards-publication-finder`
   - `/whitepaper-finder`
   - `/article-finder`
   - `/tech-talk-finder`
   - `/certification-finder`
   - `/community-contribution-finder`
5. Launch independent artifact workflows concurrently. Each workflow must use at least two
   source- or strategy-partitioned discovery agents.
6. Workers emit evidence assertions and normalized candidates only. They cannot make final
   identity, inclusion, merge, status, or validity decisions.
7. After every focused workflow finishes, have the master coordinator classify and reconcile all
   out-of-category evidence into the correct artifact corpus and routing ledger.
8. Reconcile discovery coverage against every known-inventory row. Do not freeze the corpus while
   any row lacks a disposition or an explicit blocked/unavailable-source explanation.
9. Freeze the combined evidence corpus and invoke exactly one higher-layer identity supervisor.
10. Permit one bounded targeted-research round for each uncertain identity cluster.
11. Apply artifact-specific reconciliation after the supervisor's decisions. Deduplication may
    merge representations, never erase a source row or collapse distinct canonical artifacts.
12. Write all normalized records to `<output_dir>/normalized-records.jsonl`.
13. Invoke the renderer:

```text
python plugins/artifact-finder/scripts/run.py \
  --candidate-config <candidate-config> \
  --records <output_dir>/normalized-records.jsonl \
  --output-dir <output_dir> \
  --portfolio-dir <candidate-config-directory> \
  --portfolio-file <canonical-name-slug>.md \
  --consent-confirmed
```

14. Re-read the Markdown portfolio, CSV headers, manifest, decisions, routing ledger, baseline
    coverage, and
    report. Correct any
    schema or rendering failure before finishing.

## Output policy

The candidate Markdown file is resume-focused:

- Candidate name as the heading.
- Total verified artifact count.
- Counts only for non-empty artifact types.
- Sections only for non-empty artifact types.
- Concise public links and relevant artifact details.
- No run status.
- No evidence snapshot.
- No methodology section.
- No uncertain or excluded records.
- Community Q&A is summarized by profile, not expanded response by response.

Supporting CSV and audit files remain in `output/`, including uncertain and excluded records for
review.

When a known inventory was supplied, supporting audit output must also contain a deterministic
row-level coverage map and these counts: input rows, unique identifiers, canonical artifacts,
included, uncertain, excluded, duplicate representations, and unresolved rows. A smaller
portfolio count is acceptable only when this map explains every difference.

Always retain `cross-category-routing.jsonl`, including successfully routed records, so an
artifact removed from one category can be proven present in the destination corpus.

## Failure policy

Continue autonomously through optional-source failures and mark the support run degraded. Stop
only when:

- The candidate config is invalid or missing.
- Required authentication cannot be completed.
- No authoritative source and no usable cache is available for every requested workflow.
- Output validation fails after one repair attempt.
- An irreversible action would be required.

Never fabricate an artifact to fill an empty section. An empty category is omitted from the
candidate Markdown file.
