# ALU physical implementation experiments

Baseline: display revision `63c6dd60c1c729c403af95ad6027286210b5ae57` (D0). Local D0 final metrics exactly match its successful GitHub run 34155861764; D0_ci_metrics_diff.json is empty.
Selected implementation: **D10_routed_slew_repair**. RTL, synthesis netlist, PDK, floorplan and final SDC are identical across this display series.

Worst-path delay after external input delay changes by **-19.63%**; functional cell area changes by **-6.22%**. The tile remains 1x1; this is not a smaller purchased die footprint.

| Run | Input buffers | Output buffers | Repair slew margin % | Path delay ns | Setup slack ns | Cell area um2 | Cells | Buffers | Wire um | Vias | Slew violations |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D0_display | True | 0 | 20 | 8.4511 | 3.2989 | 1025.98 | 125 | 19 | 2186 | 865 | 11 |
| D2_display_no_port_buffers | False | 0 | 20 | 7.8484 | 3.9016 | 915.88 | 114 | 8 | 2156 | 812 | 11 |
| D3_output_buffers | True | True | 20 | 8.5196 | 3.2304 | 1113.57 | 134 | 28 | 2324 | 906 | 11 |
| D4_input_off_output_on | False | True | 20 | 7.9340 | 3.8160 | 1003.46 | 123 | 17 | 2267 | 866 | 11 |
| D5_slew_margin | False | True | 60 | 7.8262 | 3.9238 | 967.18 | 129 | 23 | 2199 | 874 | 11 |
| D7_slow_corner | False | True | 20 | 7.9083 | 3.8417 | 1004.71 | 122 | 16 | 2300 | 845 | 11 |
| D8_no_delay_buffers | False | True | 20 | 7.2443 | 4.5057 | 1007.22 | 136 | 30 | 2262 | 904 | 22 |
| D9_post_route_repair | False | True | 20 | 7.9168 | 3.8332 | 997.21 | 123 | 17 | 2295 | 867 | 11 |
| D10_routed_slew_repair | False | True | 20 | 6.7922 | 4.9578 | 962.17 | 123 | 17 | 2280 | 863 | 0 |

## Selected hardening changes

```json
{
  "DESIGN_REPAIR_BUFFER_INPUT_PORTS": false,
  "DESIGN_REPAIR_BUFFER_OUTPUT_PORTS": true,
  "RUN_POST_GRT_DESIGN_REPAIR": true,
  "GRT_DESIGN_REPAIR_MAX_SLEW_PCT": 60,
  "RSZ_CORNERS": [
    "max_ss_100C_1v60"
  ]
}
```

These are changes relative to D0. The table abbreviates settings: D7 additionally uses RSZ_CORNERS=[max_ss_100C_1v60]; D8 additionally excludes sky130_fd_sc_hd__clkdlybuf*; D9 enables RUN_POST_GRT_DESIGN_REPAIR. D10 combines post-GRT repair, a 60% post-GRT slew repair margin and the slow resizer corner. Every complete variant is recorded in configs/.

## Interpretation

D0 has positive setup/hold slack, but the ALU result drives both the hex decoder and output load, producing slew violations. The violating net is driven by sky130_fd_sc_hd__clkdlybuf4s25_1. Removing input buffers reduces delay and area but alone does not clear those violations. Output isolation and stronger placement-repair margins leave violations. Excluding clock-delay buffers improves delay but also leaves slew violations. Post-GRT repair at its default margin also leaves violations. The selected D10 combines routed-load repair, a 60% post-GRT repair margin and the slow resizer corner. This combination passes all nine final extracted corners without relaxing the SDC. These experiments establish the combination's effect; they do not isolate the separate contribution of each D10 setting. D6 was terminated during repair without final results; see incomplete_runs.json.

`DESIGN_REPAIR_MAX_SLEW_PCT` experiments used a stricter implementation repair margin, not a relaxed signoff limit. `RSZ_CORNERS` was another implementation-only experiment; final STA always checked all nine corners. `EXTRA_EXCLUDED_CELLS` applies to both synthesis and PnR; synthesis hashes were explicitly compared to verify that this particular exclusion left the mapped synthesis netlist unchanged. The final SDC SHA256 is also identical. Removing input buffers can increase the load presented to the upstream shuttle driver; the external drive model is included in STA, and input capacitance is recorded in summary.json. This tradeoff needs board/shuttle context in further integration signoff.

All listed runs completed local LibreLane hardening with Magic DRC=0, LVS=0, max-cap violations=0, and setup/hold TNS=0. Slew violations are separately shown above; completion of a flow alone is not proof of electrical closure. Local functional gate-level tests cover 2,048 combinations for each run; see verification.json. GitHub CI results must be checked on the exact pushed commit. Physical board testing is pending silicon.

## Controlled conditions and metric definitions

Power has not been measured or estimated with an activity profile. These results establish timing, area and electrical-rule tradeoffs, not a quantified power reduction.
- LibreLane 3.0.5; OpenROAD dcf36133a369abc8f3c5e5738cd4d82e4903c0e0; Yosys 0.62.
- SKY130A / sky130_fd_sc_hd / open_pdks 8afc8346a57fe1ab7934ba5a6056ea8b43078e71.
- Fixed TT 1x1 template: 161.00 x 111.52 um. Placement density target 60%.
- Nine RC/PVT combinations: min/nom/max parasitics x ff_n40C_1v95, tt_025C_1v80, ss_100C_1v60.
- 20 ns reference clock constraint, 4 ns input delay, 4 ns output delay and 0.25 ns setup uncertainty. This ALU has no registers and needs no operating clock; these constraints define its I/O timing budget, not a measured clock frequency.
- Path delay = reported worst data arrival minus 4 ns external input delay. It includes external-driver load effect. Compare each implementation's actual worst path; the path can change.
- Functional area sums combinational/inverter/buffer/timing-repair-buffer classes, excluding 225 tap cells and filler cells. Physical tile dimensions remain fixed. Buffer count can increase while area decreases when buffer types and strengths change.
- Small net-delay numbers do not mean wire capacitance is irrelevant: RC load affects cell delay and slew too.
- Common synthesis netlist SHA256: `b78906a8d10314bcb817b27f639f7833f609fedd5556655246030e6b9a7f2430`.
- Common final SDC SHA256: `26b27cb0a4c64fec2fcce6237a6008668ff832475a2bef792b2a28cef8df0d19`.

## Earlier binary-only ALU

The original submitted revision is 09ad68dc50be88310353c8e8806c234fcc530af1. Its local B0 reproduction exactly matched all CI final metrics. The earlier ~10% delay and ~14% functional-area improvement belongs to that binary-only circuit; it must not be mixed with the display baseline. Its three-run comparison is in original_binary_summary.json.

## Reproduction

Use the same LibreLane/PDK versions and the TT SKY26c tt_block_1x1_pg.def template. Run reproduce.py with the selected config, an output directory and the installed PDK root. The script copies the unchanged RTL and supplied template into an isolated project before invoking LibreLane.

```sh
python experiments/reproduce.py --variant D10_routed_slew_repair --pdk-root /path/to/pdk --template /path/to/tt_block_1x1_pg.def --work-dir /tmp/alu-reproduction
```

Run the repository cocotb test for RTL, then with GATES=yes and the final powered netlist copied to test/gate_level_netlist.v. Functional simulation has no extracted timing back-annotation; STA provides the timing evidence.

## Portfolio and silicon demo

Project theme: trace an RTL-to-layout critical path, make controlled physical implementation changes, and explain timing/area/electrical-rule tradeoffs with extracted parasitics. OPC experience contributes layout interpretation and manufacturing awareness; these experiments do not perform OPC or establish lithographic/yield improvement.

The ASIC drives the onboard hex display directly. A/B come from DIP switches or the management MCU; opcode uses uio[2:0]. Binary result remains visible on uio[7:4], zero on uio[3]. demo/alu_demo.py supplies a future silicon self-test and interactive examples. Functional board measurements must be distinguished from block STA.
