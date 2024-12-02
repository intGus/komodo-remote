# CircuitPython Camera Control

This project allows you to control and monitor a camera over a WebSocket connection using a button and a NeoPixel indicator on a CircuitPython-supported microcontroller.

## Features

- **Button Control**: 
  - Single press toggles the camera's recording state.
  - Double press disconnects from the camera.
- **State Monitoring**:
  - Displays the camera's current state using a NeoPixel indicator:
    - Green: Idle
    - Red: Recording
    - Yellow: Transition to idle
- **WebSocket Communication**:
  - Communicates with the camera server to send and receive commands.

## Installation

1. **Prepare Your CircuitPython Board**:
   - Install the latest version of CircuitPython on your board.
   - Add the code.py file, `cpwebsockets` and `lib/` folder to the root of your board. 

2. **Configure Your Settings**:
   - Edit the `main.py` file to replace:
     - `SSID` with your Wi-Fi network name.
     - `PASSWORD` with your Wi-Fi password.
     - `WEBSOCKET_URL` with the WebSocket URL of your camera (e.g., `ws://<camera_ip>:<port>/rcp`).

## Usage

1. **Power the Board**:
   - Connect the board to power. It will automatically connect to Wi-Fi and the camera's WebSocket server.

2. **Interact with the Button**:
   - **Single Press**: Toggles the camera's recording state.
   - **Double Press**: Disconnects the WebSocket connection.

3. **Monitor Camera State**:
   - The NeoPixel will update based on the camera's current state:
     - **Green**: Idle
     - **Red**: Recording
     - **Yellow**: Transition to idle

## Configuration

Replace the placeholders in the code with your values:

```python
# Wi-Fi credentials
SSID = ""
PASSWORD = ""

#Camera IP
IP = ""
```

## Notes

This code uses a neopixel to reflect the status of the camera, if your board doesn't have a neopixel you can replace the code to use a regular onboard LED

## License

This repository is released under the MIT License.

## Acknowledgments

Using a [fork](https://github.com/intGus/cpwebsockets) of [uwebsockets](https://github.com/danni/uwebsockets) originally created by danni.
