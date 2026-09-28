# Test results summary

The final prototype was evaluated through module validation and system-level indoor experiments. The results below match the data reported in the final thesis.

## System-level tests

| Function | Successful trials | Success rate | Main observation |
|---|---:|---:|---|
| Manual control | 15/15 | 100% | Browser commands were executed correctly. |
| Video monitoring | 14/15 | 93.3% | One temporary stream-freeze event occurred. |
| Obstacle response | 15/15 | 100% | Basic front and side responses worked under the tested conditions. |
| Patrol logic | 14/15 | 93.3% | One trial failed when the rover was blocked by a chair leg. |
| Target detection and reporting | 13/15 | 86.7% | Strong background lighting caused two detection failures. |
| Integrated end-to-end workflow | 5/5 | 100% | Video, movement, detection, reporting, and stop behaviour worked together. |

## Video latency

Ten observations were recorded:

```text
0.56 0.62 0.58 0.70 0.60
0.64 0.57 1.80 0.61 0.58
```

- Average across all ten trials: approximately **0.73 s**
- Average across the nine stable trials: approximately **0.61 s**
- Observed failure: one temporary freeze at **1.80 s**

## Sensor validation

- The HC-SR04 produced small average errors across the tested 5-30 cm range and was used for short-distance front obstacle sensing.
- Both IR sensors triggered at approximately 3.5-4.0 cm and did not trigger from 4.5 cm upward under the tested conditions. They should therefore be interpreted as close-range digital side sensors, not distance sensors.

## Interpretation boundary

These results demonstrate prototype feasibility under controlled indoor conditions. They do not establish production reliability, full autonomous navigation, or robust animal recognition across unconstrained environments.
