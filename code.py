import wifi
import time
import board
import digitalio
import cpwebsockets.client
import json
import neopixel

pixel = neopixel.NeoPixel(board.NEOPIXEL, 1) # 1 NeoPixel
pixel.brightness = 0.5
COLOR_RED = (0, 255, 0) # (G, R, B)
COLOR_GREEN = (255, 0 , 0)
COLOR_YELLOW = (255,255,0)

# Wi-Fi credentials
SSID = ""
PASSWORD = ""

#Camera IP
IP = ""

WEBSOCKET_URL = "ws://" + IP + ":9998/rcp"
BUTTON_PIN = board.BUTTON
DEBOUNCE_TIME = 0.2  # seconds
DOUBLE_PRESS_TIME = 0.5  # seconds

def connect_to_wifi():
    print("Connecting to Wi-Fi...")
    try:
        wifi.radio.connect(SSID, PASSWORD)
        #print("Connected to Wi-Fi!")
        print(f"IP Address: {wifi.radio.ipv4_address}")
    except Exception as e:
        print("Failed to connect to Wi-Fi:", e)
        raise
    
def monitor_and_listen(websocket, button):
    """
    Main loop to concurrently monitor button presses and listen for WebSocket events.
    """
    last_press_time = 0
    press_count = 0
    button_state = False  # Tracks whether the button is currently pressed
    websocket.settimeout(0.1)  # Non-blocking WebSocket handling

    while True:
        # Handle WebSocket events
        try:
            received_message = websocket.recv()
            update_LED_status(received_message)
            #print(f"Received: {received_message}")
        except OSError:
            #Timed out
            pass
            
        # Button event detection
        current_time = time.monotonic()

        if not button.value:  # Button is pressed
            if not button_state:  # Button just pressed
                button_state = True
                press_count += 1
                last_press_time = current_time
        else:  # Button released
            if button_state:  # Button just released
                button_state = False

        # Double-press and debounce handling
        if press_count > 0 and (current_time - last_press_time) > DOUBLE_PRESS_TIME:
            if press_count == 1:
                send_rcp_command(websocket, "RCP_PARAM_RECORD_STATE", "2") # 2 means toggle record
            elif press_count == 2:
                print("Double press detected, disconnecting...")
                websocket.close()
                pixel.fill((0,0,0))
                print("WebSocket connection closed.")
                break
            press_count = 0  # Reset press count

        time.sleep(0.01)  # Delay for polling
        
def send_config(websocket):
    """
    Sends a configuration message to the WebSocket server.
    """
    config = {
        "type": "rcp_config",
        "strings_decoded": 0,
        "json_minified": 1,
        "include_cacheable_flags": 0,
        "encoding_type": "html",
        "client": {
            "name": "RED Web App"
        }
    }

    # Serialize the config to JSON
    try:
        config_json = json.dumps(config)
        websocket.send(config_json)
        print(f"Configuration sent: {config_json}")
    except Exception as e:
        print(f"Failed to send configuration: {e}")


def send_rcp_command(websocket, param_id, value):
    """
    Send an RCP command over the WebSocket.
    """
    # Remove "RCP_PARAM_" prefix
    if param_id.startswith("RCP_PARAM_"):
        param_id = param_id[10:]

    # Create the command object
    command = {
        "type": "rcp_set",
        "id": param_id,
        "value": value,
    }

    # Serialize to JSON and send
    try:
        websocket.send(json.dumps(command, separators=(',', ':')))
        print(f"Command sent: {command}")
    except Exception as e:
        print(f"Failed to send command: {e}")

def get_rcp_status(websocket, param_id):
    """
    Get RCP status over the WebSocket.
    """
    # Remove "RCP_PARAM_" prefix
    if param_id.startswith("RCP_PARAM_"):
        param_id = param_id[10:]

    # Create the command object
    command = {
        "type": "rcp_get",
        "id": param_id,
    }

    # Serialize to JSON and send
    try:
        websocket.send(json.dumps(command, separators=(',', ':')))
        print(f"Command sent: {command}")
    except Exception as e:
        print(f"Failed to send command: {e}")

def update_LED_status(received_data):
    resp = json.loads(received_data)
    state = resp.get("cur", {}).get("val")
    if state == 0:
        pixel.fill(COLOR_GREEN)
        print("Set NeoPixel to GREEN (Idle).")
    elif state == 1:
        pixel.fill(COLOR_RED)
        print("Set NeoPixel to RED (Recording).")
    elif state == 2:
        pixel.fill(COLOR_YELLOW)
        print("Set NeoPixel to YELLOW (Paused).")
                

def main():
    # Initialize button
    button = digitalio.DigitalInOut(BUTTON_PIN)
    button.direction = digitalio.Direction.INPUT
    button.pull = digitalio.Pull.UP

    connect_to_wifi()

    # WebSocket connection
    try:
        print("Connecting to WebSocket server...")
        websocket = cpwebsockets.client.connect(WEBSOCKET_URL, wifi.radio)
        print("Connected!")
        send_config(websocket)
        resp = websocket.recv() # parse for auth?
        print("Received:", resp)
        get_rcp_status(websocket, "RCP_PARAM_RECORD_STATE")
        update_LED_status(websocket.recv())

        # Concurrently monitor button and listen for WebSocket events
        monitor_and_listen(websocket, button)

    except Exception as e:
        print(f"An error occurred: {e}")


main()
