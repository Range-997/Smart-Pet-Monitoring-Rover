# Pin assignment

This file records the wiring used in the final prototype.

## Arduino to L298N

| Arduino pin | L298N pin |
|---|---|
| D5 | ENA |
| D6 | ENB |
| D8 | IN1 |
| D9 | IN2 |
| D10 | IN3 |
| D11 | IN4 |

## Sensors

| Sensor | Arduino connection |
|---|---|
| HC-SR04 VCC | 5V |
| HC-SR04 TRIG | D12 |
| HC-SR04 ECHO | D13 |
| HC-SR04 GND | GND |
| Left IR OUT | A0 |
| Right IR OUT | A1 |
| IR VCC | 5V |
| IR GND | GND |

## Power

- Raspberry Pi uses a separate 5 V rechargeable battery pack.
- L298N motor input uses a 7.4 V battery pack.
- Arduino GND, L298N GND and motor battery negative share common ground.
