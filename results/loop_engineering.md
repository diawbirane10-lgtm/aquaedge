# Loop Engineering Results — AquaEdge Intelligence MVP

Date: 2026-08-30

## Executive result

The engineering loop produced a **promising TRL-2 synthetic proof of concept**, but not field-conclusive evidence.

The strongest current architecture is a two-stage cascade:

1. sensor-health screening;
2. process anomaly classification with normalized physics/temporal features.

The development run reached accuracy **0.733** / macro-F1 **0.721**. The current repository was then re-executed independently in GitHub Actions; the reproducible run reached:

- accuracy: **0.728**;
- macro-F1: **0.718**.

This close agreement is useful evidence that the result is reproducible at software-MVP level. It is sufficient to justify continued development and to document a preliminary MVP in the TAQA technical report, provided the report clearly labels the values as **synthetic simulation results**.

It is **not** sufficient to claim field detection accuracy at Tamsoult.

---

## Cycle 1 — naive baseline

### Design

- 3,600 synthetic time rows;
- 72 scenario episodes;
- six classes: normal, leak, pump fault, dry run, quality drift, sensor fault;
- raw + simple derivative features;
- XGBoost multiclass;
- held-out episodes.

### Result

- accuracy: **0.348**;
- macro F1: **0.325**.

### Decision

**Rejected.**

The model did not generalize well across operating baselines. Absolute values were too influential and normal/sensor-fault states were poorly separated.

Engineering lesson: a water-monitoring model must not learn one absolute operating point as if it were universal.

---

## Cycle 2 — temporal + physics-derived features

### Changes

- class-stratified hold-out by complete episode;
- 9 train + 3 unseen test episodes per class;
- rolling means and standard deviations;
- episode-reference residuals;
- energy-per-volume / pressure-flow features;
- preliminary leak, pump and dry-run indices.

### Result

- accuracy: **0.590**;
- macro F1: **0.590**.

Selected class F1:

- leak: **0.768**;
- dry run: **0.914**;
- quality drift: **0.724**;
- sensor fault: **0.648**.

### Decision

**Promising but insufficient.**

Generalization improved strongly, but normal and pump-fault discrimination remained weak.

---

## Cycle 3 — normalized physics-informed model

### Changes

- per-episode normalization against an initial reference window;
- only normalized/temporal/physics-informed features used for the main classifier;
- longer temporal statistics;
- pump-efficiency proxy;
- leak, pump, dry-run and quality composite features.

### Result

- accuracy: **0.713**;
- macro F1: **0.697**.

Per-class F1:

- normal: **0.582**;
- leak: **0.719**;
- pump fault: **0.702**;
- dry run: **0.975**;
- quality drift: **0.926**;
- sensor fault: **0.277**.

### Decision

The process classes improved significantly, but the sensor-fault class behaved differently from process anomalies.

Engineering lesson: **sensor health should be a separate diagnostic layer** instead of one more hydraulic/process class.

---

## Cycle 3b — two-stage cascade

### Architecture correction

A separate binary sensor-health classifier screens telemetry before a five-class process XGBoost model.

This better matches the physical architecture:

```text
sensor validation / health
        |
        +-- invalid / suspected sensor fault -> maintenance alert
        |
        v
physics residuals + process ML
        |
 normal / leak / pump fault / dry run / quality drift
```

### Development result

- accuracy: **0.733**;
- macro F1: **0.721**.

### Reproducible GitHub Actions validation

Workflow run: `33296487271`.

- accuracy: **0.728**;
- macro F1: **0.718**.

Per-class F1 in the reproducible run:

- normal: **0.580**;
- leak: **0.710**;
- pump fault: **0.738**;
- dry run: **0.957**;
- quality drift: **0.895**;
- sensor fault: **0.425**.

### Interpretation

The cascade is the current baseline architecture. Dry-run and quality-drift scenarios are already strongly separable in the synthetic environment; leak and pump-fault detection are promising; normal-state and especially sensor-fault discrimination require further work.

The low sensor-fault recall (**0.283**) confirms that sensor diagnostics still require dedicated engineering: plausibility checks, stuck-sensor detection, redundancy/cross-consistency and eventually calibration/maintenance metadata.

---

## Retrieval baseline

A simple TF-IDF retrieval baseline was tested on 15 labelled AquaEdge architecture questions.

- top-1 retrieval accuracy: **0.667**;
- recall@3: **1.000**.

Interpretation: document retrieval is already usable as a minimal baseline, but a better embedding model / reranker should be evaluated before claiming robust RAG performance.

---

## LLM engineering cycle

The repository now contains:

- a provider-neutral LLM adapter layer (Ollama, Groq, Mistral, Anthropic, OpenAI Responses, OpenRouter);
- an AquaEdge system prompt with explicit safety boundaries;
- an MHS-ready hardware registry;
- a 20-case domain/safety evaluation set;
- a small supervised instruction dataset for optional LoRA/QLoRA adaptation;
- an Ollama benchmark workflow that runs open-source models without external API credentials.

Live hosted-provider benchmarking still requires provider API keys. No fabricated Claude/Groq/Mistral/OpenAI scores will be reported.

---

## Gate for the TAQA report

### Can report writing begin now?

**Yes**, for a TRL-2 concept/MVP dossier.

The report can truthfully contain:

- the final hardware/software architecture;
- Hub + four AquaNodes topology;
- MHS-ready/MCP/LLM architecture;
- synthetic telemetry methodology;
- three-cycle ML engineering process;
- reproducible preliminary synthetic metrics;
- RAG/LLM evaluation methodology;
- limitations and field-validation plan.

### What must not be claimed?

Do not claim:

- 72.8% field accuracy;
- Tamsoult field validation;
- physical deployment;
- MHS compliance certification;
- hosted-LLM benchmark results before actual API runs;
- regulatory water-potability certification from the AI model.
