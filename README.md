# AquaEdge TMS-01

**Autonomous Edge AIoT platform for rural water monitoring, control and decision support**

Pilot concept: **Tamsoult, Commune d’Aguinane, Province de Tata, Morocco**.

AquaEdge TMS-01 is a distributed cyber-physical water supervision concept built around:

- one **central AquaEdge Hub** based on the Revolution Pi / Raspberry Pi ecosystem;
- four peripheral **AquaNodes** around a rectangular monitored cell;
- LoRa telemetry from nodes to the hub;
- 4G/LTE backhaul for remote supervision;
- deterministic local control and hardwired safety interlocks;
- a hydraulic digital twin;
- local machine learning for anomaly detection;
- an **MHS-ready hardware registry** exposed to an LLM through an MCP-facing gateway;
- offline-first operation with local historian, alarms and control.

> **TRL / scope:** this repository currently contains a TRL-2 engineering MVP: architecture, synthetic telemetry, baseline ML, RAG/evaluation harnesses and provider adapters. It does **not** claim field validation at Tamsoult.

## System architecture

```text
                 Remote supervision / LLM
                         read & advise
                              |
                             MCP
                              |
                     MHS-ready gateway
                              |
                       Hardware registry
                              |
                    AquaEdge Hub TMS-01
                  RevPi Connect 5 + I/O
                  /       /      \       \
              LoRa     LoRa      LoRa     LoRa
               |         |         |        |
              N1        N2        N3       N4
           Borehole   Reservoir  Valve/   Quality/
            /pump                distrib.   downstream
```

The LLM is **never** the safety controller. Safety-critical pump inhibition and emergency functions remain deterministic and independent from cloud, ML and LLM services.

## AI roles

AquaEdge separates the AI stack into distinct responsibilities:

1. **Hydraulic digital twin** — estimates expected physical behaviour.
2. **XGBoost / ML** — classifies anomalies from telemetry and physics-derived features.
3. **LLM** — explains events, queries the MHS-ready registry, answers operator questions and recommends actions.
4. **CODESYS / deterministic control** — executes normal automation logic.
5. **Hardwired interlocks** — provide independent safety inhibition.

## Repository layout

```text
app/
  agents/          # AquaEdge assistant orchestration
  llm/             # Ollama / Groq / Mistral / Claude / OpenAI adapters
  mhs_registry/    # normalized device/capability registry
  ml/              # anomaly-classification pipeline
  rag/             # local document retrieval
  rules/           # safety and policy guardrails
  telemetry/       # synthetic and future field telemetry
configs/           # project configuration
data/
  eval/            # LLM/RAG evaluation cases
  finetune/        # domain SFT examples
  synthetic_telemetry/
docs/              # architecture, model card, evaluation plan
results/           # loop-engineering results
scripts/           # runnable entry points
tests/             # unit tests
```

## Local LLM strategy

### Baseline local model

The first local backend is **Ollama**. Recommended test order:

- `gemma3:4b` — compact local baseline;
- `gpt-oss:20b` — stronger reasoning benchmark when workstation memory permits;
- cloud/API candidates: Groq GPT-OSS, Mistral, Claude and OpenAI Responses API.

The repository uses provider-neutral adapters so the same AquaEdge evaluation set can be run against several backends.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .

# Generate telemetry
python scripts/generate_synthetic_data.py

# Run ML loop
python scripts/run_ml_loop.py

# Start Ollama separately, then benchmark a model
ollama run gemma3:4b
python scripts/benchmark_llm.py --provider ollama --model gemma3:4b
```

API keys are always read from environment variables. **Never commit keys to this public repository.**

## Current engineering-loop status

Three design iterations plus a cascade correction were evaluated on synthetic telemetry with **complete unseen episodes held out**, rather than a random row split.

- Cycle 1 — naive baseline: macro-F1 **0.325** (rejected).
- Cycle 2 — temporal + physics-derived features: macro-F1 **0.590**.
- Cycle 3 — normalized physics-informed feature set: macro-F1 **0.697**.
- Cycle 3b — two-stage sensor-health + process classifier: initial development run macro-F1 **0.721**.
- **Reproducible GitHub Actions validation of the current code:** accuracy **0.728**, macro-F1 **0.718**.

Reproducible per-class F1 for the current baseline:

- normal: **0.580**;
- leak: **0.710**;
- pump fault: **0.738**;
- dry run: **0.957**;
- quality drift: **0.895**;
- sensor fault: **0.425**.

These results are promising for a TRL-2 synthetic proof of concept but **not field-conclusive**. See `results/loop_engineering.md` and `results/cycle3_runtime.json`.

## Scientific caution

The current dataset is synthetic. Reported metrics must be described as **simulation results**, not Tamsoult field performance. Field deployment will require sensor calibration, hydraulic parameter identification, radio survey, representative seasonal data and independent validation.

## License

Project engineering code is currently published for research/prototyping. A formal license will be selected before external reuse is encouraged.
