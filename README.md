# Stellar Unicorn DDP Receiver

This MicroPython script runs on the Pimoroni **Stellar Unicorn** (16x16 LED matrix with a Pico W) and listens for DDP (Distributed Display Protocol) packets over Wi-Fi. Incoming pixel data is displayed live on the grid.

If no DDP packets are received for 5 seconds, the device enters **idle mode**: the display turns off and the lower-left pixel slowly pulses red to indicate that the receiver is still alive but not receiving data.

## Features

- Listens on UDP port `4048` for DDP pixel data
- Displays live 16x16 RGB content from the network
- Idle indicator after timeout: red pulsing LED in lower-left corner
- Adjustable brightness via onboard buttons (`LUX+` and `LUX-`)
- Wi-Fi credentials are stored securely in a separate `config.json` file (not hardcoded)

---

### 1. Create `config.json`

Wi-Fi credentials should be placed in a file called `config.json` on the root of the device:

```json
{
  "ssid": "YourNetworkName",
  "password": "YourSuperSecretPassword"
}
```

> ✋ Do **not** commit this file to version control.

---

### 2. Upload the Script

Save the main Python file as `main.py` on the device. This ensures it runs automatically at boot.

---

## 🔧 Controls

| Button        | Function                |
|---------------|-------------------------|
| LUX +         | Increase brightness     |
| LUX -         | Decrease brightness     |

Brightness is adjustable from 1 (dim) to 10 (max). The current level is applied live and resets on reboot unless persisted.

---

## 🛑 Idle Behavior

If no DDP packets are received within 5 seconds:

- The entire display is cleared (turned off)
- A red LED at coordinate `(0, 15)` pulses softly to show the system is active but idle

This allows for graceful fallback without leaving stale data on screen.

---

## 🔒 Security

Wi-Fi credentials are never stored in the script. Always use `config.json` and ensure it's excluded from version control.

---

## 📡 DDP Format

This receiver expects pixel data starting at byte 10 of each UDP packet (skipping standard DDP headers). Each pixel is 3 bytes: RGB.

Total payload size (excluding header):  
```
16 x 16 x 3 = 768 bytes
```

