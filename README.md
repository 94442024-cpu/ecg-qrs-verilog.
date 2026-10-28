# ECG QRS Detector in Verilog

Pan-Tompkins style heartbeat detector, built in Verilog and taken through
synthesis and layout on the open-source SKY130 process.

## Status

| Stage | Block | Simulation | Synthesis | Layout |
|---|---|---|---|---|
| 1 | moving_avg (32-sample integrator) | PASS | 784 cells (533 flip-flops) | OpenLane run completed |
| 2 | derivative | planned | | |
| 3 | squarer, bandpass, threshold | planned | | |

## Run the simulation

    iverilog -g2012 -o sim rtl/moving_avg.v tb/tb_moving_avg.v && vvp sim

Expected output: `PASS`.

## Synthesis

    yosys -p "read_verilog rtl/moving_avg.v; synth -top moving_avg; stat"

## Tools

Icarus Verilog, GTKWave, Yosys, OpenLane 1 (Docker), KLayout, SKY130 PDK.

## Data

MIT-BIH Arrhythmia Database from PhysioNet (not included in this repo).
