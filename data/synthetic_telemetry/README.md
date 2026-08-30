# Synthetic telemetry v0

The full dataset is generated reproducibly with:

```bash
python scripts/generate_synthetic_data.py
```

Default generation produces:

- 6 classes;
- 12 episodes per class;
- 50 time steps per episode;
- 72 complete episodes;
- 3,600 telemetry rows.

Signals:

- borehole level;
- flow;
- pressure;
- pump power;
- tank level;
- valve position;
- nitrate;
- turbidity;
- conductivity;
- water temperature;
- hub battery voltage / SOC.

Fault scenarios:

- normal;
- leak;
- pump fault;
- dry run / groundwater-level stress;
- water-quality drift;
- sensor fault.

The dataset is deliberately **not** described as Tamsoult field data. It is a controlled TRL-2 simulation dataset designed to exercise the software/ML pipeline before real calibration data exist.

Do not use a random row split when benchmarking. Hold out entire episodes.
