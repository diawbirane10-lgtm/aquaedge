# Loop Engineering Results — AquaEdge Intelligence MVP

Date: 2026-08-30

## Executive result

The engineering loop produced a **promising TRL-2 synthetic proof of concept**, but not field-conclusive evidence.

The strongest current result is a two-stage architecture:

1. sensor-health screening;
2. process anomaly classification with physics/temporal features.

On completely unseen synthetic episodes, the current cascade reaches:

- accuracy: **0.733**;
- macro F1: **0.721**.

This is sufficient to justify continued development and to document a preliminary MVP in the TAQA technical report, provided the report clearly labels the results as **synthetic simulation results**.

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

### Result

- accuracy: **0.733**;
- macro F1: **0.721**.

Per-class F1:

- normal: **0.584**;
- leak: **0.721**;
- pump fault: **0.743**;
- dry run: **0.966**;
- quality drift: **0.902**;
- sensor fault: **0.410**.

### Interpretation

The cascade is the current baseline architecture.

The relatively low sensor-fault recall shows that sensor diagnostics still require dedicated engineering: plausibility checks, stuck-sensor detection, redundancy/cross-consistency and eventually calibration/maintenance metadata.

---

## Retrieval baseline

A simple TF-IDF retrieval baseline was tested on 15 labelled AquaEdge architecture questions.

- top-1 retrieval accuracy: **0.667**;
- recall@3: **1.000**.

Interpretation: document retrieval is already usable as a minimal baseline, but a better embedding model / reranker should be evaluated before claiming robust RAG performance.

---

## LLM cycle status

Provider adapters and the evaluation harness can be implemented without credentials, but **live hosted-LLM benchmarking cannot be scientifically executed without provider API keys**, and this environment does not contain downloadable model weights.

Therefore no fabricated Claude/Groq/Mistral/OpenAI score is reported.

Recommended local first model on the user's workstation: **Gemma 3 4B through Ollama**. A higher-capability comparison can use **GPT-OSS 20B** when memory allows, plus hosted models through the same evaluation harness.

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
- preliminary synthetic metrics;
- limitations and field-validation plan.

### What must not be claimed?

Do not claim:

- 73% field accuracy;
- Tamsoult validation;
- physical deployment;
- MHS compliance certification;
- successful hosted-LLM benchmark before actual API runs;
- regulatory water-potability certification from the AI model.
