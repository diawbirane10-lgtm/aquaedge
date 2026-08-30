# AquaEdge TMS-01 Architecture

## 1. Purpose

AquaEdge TMS-01 is a distributed monitoring and control concept for a rural water cell. The reference topology contains one central hub and four peripheral AquaNodes positioned at hydraulically meaningful locations rather than at arbitrary geometric points.

## 2. Reference monitored cell

The reference geometry used in the TRL-2 MVP is rectangular for clarity:

- **N1 — Borehole / pump:** groundwater level, pressure, flow, pump/VFD status.
- **N2 — Reservoir:** reservoir level and independent high-high contact.
- **N3 — Distribution / valve:** pressure, flow, valve position and authorized actuation.
- **N4 — Downstream / quality:** nitrate, turbidity, conductivity and temperature.
- **Hub — AquaEdge TMS-01:** central automation, local historian, ML, digital-twin services, communications and supervision.

The physical installation does not require a perfect rectangle. The final positions must follow the actual water network, radio survey and access constraints.

## 3. Central Hub

Reference hardware:

- Revolution Pi Connect 5 as the modular industrial base unit;
- RevPi AIO for analog / RTD channels;
- RevPi DIO for digital inputs/outputs and pulse counting;
- RevPi RO for relay outputs;
- CODESYS for deterministic normal automation;
- industrial 4G/LTE router for remote backhaul;
- dedicated PV + MPPT + LiFePO4/BMS + regulated 24 VDC electronics supply.

The small AquaEdge PV subsystem powers electronics, telemetry, low-power actuation and alarms. It does **not** power the borehole pump motor. Pump power is provided by an independent grid or pumping-PV/VFD chain.

## 4. Communications

### Local cell

AquaNodes use LoRa star topology to communicate with the hub. The exact frequency plan, EIRP, antenna placement and radio budget must be selected according to Moroccan regulatory requirements and a site radio survey.

### Remote link

The hub uses 4G/LTE when available. The system is offline-first: loss of WAN does not stop local acquisition, deterministic control, local ML inference, historian or local alarms.

## 5. MHS-ready intelligence architecture

The Model Hardware Standard is treated as an architectural direction, not as a claimed compliance certification.

```text
Field devices / AquaNodes
        |
Device drivers / protocols
        |
Shared state + hardware registry
        |
MHS-ready abstraction layer
        |
MCP-facing gateway
        |
LLM assistant
```

The hardware registry normalizes device identity, location, capabilities, state, constraints and topology. An LLM can discover and query this representation without knowing each low-level field protocol.

## 6. AI separation of responsibilities

### Digital twin

Estimates physically expected hydraulic behaviour and generates physics-derived residuals.

### Machine learning

The baseline uses XGBoost to classify process anomalies from telemetry, temporal features and physics-informed features. A separate sensor-health stage is evaluated because sensor faults should not be conflated with process faults.

### LLM

The LLM provides:

- event explanation;
- operator Q&A;
- report generation;
- MHS-ready registry queries;
- diagnostic recommendations.

The LLM is read-only in the MVP. It has no safety authority.

## 7. Safety architecture

Safety remains independent from AI and cloud services.

Hardwired / deterministic permissives include at minimum:

- borehole low-low level;
- reservoir high-high level;
- emergency stop;
- major VFD fault.

A command proposed by the LLM must never bypass CODESYS policies or hardwired interlocks.

## 8. Current TRL-2 limitation

The current architecture is a design and simulation MVP. No claim is made that the topology, radio range, hydraulic parameters, sensor calibration or anomaly-model performance has been validated in the Tamsoult field environment.
