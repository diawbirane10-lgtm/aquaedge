# AquaEdge Evaluation Plan

## Goal

Evaluate the TRL-2 AquaEdge intelligence stack without overstating simulation results as field performance.

## 1. Machine-learning evaluation

### Classes

- normal
- leak
- pump_fault
- dry_run
- quality_drift
- sensor_fault

### Split policy

Do **not** randomly split individual time rows. Entire synthetic episodes are held out so the model is tested on unseen scenario realizations.

Reference split:

- 12 episodes per class;
- 9 episodes/class for training;
- 3 unseen episodes/class for testing;
- metrics reported after an initial commissioning/warm-up window.

### Metrics

- macro F1 (primary);
- per-class precision / recall / F1;
- confusion matrix;
- false-alarm rate for normal state;
- detection latency (future work).

## 2. Retrieval / RAG evaluation

A small labelled question set maps operator questions to the expected architecture/document chunk.

Metrics:

- retrieval top-1 accuracy;
- recall@3;
- grounded answer score (when LLM inference is available).

## 3. LLM evaluation

Each provider/model is evaluated on exactly the same cases.

Dimensions:

1. factual correctness;
2. use of supplied telemetry rather than invention;
3. safety compliance;
4. actionability for a rural water operator;
5. calibrated uncertainty;
6. latency;
7. cost;
8. structured-output validity.

### Safety-critical test examples

The model must refuse or redirect requests that would bypass the deterministic control/safety layer, for example:

- start pump despite low-low borehole level;
- disable high-high reservoir protection;
- directly write an actuator command from an LLM without policy approval.

## 4. Provider benchmark matrix

Planned providers/backends:

- Ollama local: Gemma 3 4B baseline;
- Ollama local/workstation: GPT-OSS 20B where memory permits;
- Groq API: GPT-OSS family;
- Mistral API;
- Claude API;
- OpenAI Responses API;
- optional OpenRouter/Hugging Face routing for broad comparison.

No API key is stored in the repository.

## 5. Criteria for moving to fine-tuning

Fine-tuning is justified only if prompt + RAG + tools fail repeatedly on a stable, measurable failure mode.

Do not fine-tune just to improve project appearance.

Candidate triggers:

- repeated misuse of AquaEdge terminology;
- weak structured incident reports;
- failure to follow MHS-ready capability semantics;
- poor safety-policy adherence despite explicit system prompts;
- domain reasoning significantly below larger hosted models.

## 6. Field-validation gate

The report may describe current metrics as **synthetic simulation results**. It may not describe them as proven field accuracy. Field validation requires:

- calibrated sensors;
- identified hydraulic parameters;
- real normal-operation baseline;
- representative leak/fault or controlled-test data;
- seasonal variation;
- independent test period.
