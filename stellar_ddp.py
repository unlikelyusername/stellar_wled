from stellar import StellarUnicorn
from picographics import PicoGraphics, DISPLAY_STELLAR_UNICORN
import network
import socket
import time
import ujson
from machine import Pin

# === Load Wi-Fi Config from File ===
with open("config.json") as f:
    conf = ujson.load(f)
WIFI_SSID = conf["ssid"]
WIFI_PASSWORD = conf["password"]

# === Constants ===
DDP_PORT = 4048
PIXEL_COUNT = 256  # 16x16
BYTES_PER_PIXEL = 3
MAX_PACKET_SIZE = PIXEL_COUNT * BYTES_PER_PIXEL

# === Init Display ===
unicorn = StellarUnicorn()
graphics = PicoGraphics(display=DISPLAY_STELLAR_UNICORN)

# === Brightness Control ===
brightness_level = 5  # 1–10 scale

def update_brightness():
    unicorn.set_brightness(brightness_level / 10)

update_brightness()

def check_buttons():
    global brightness_level
    if unicorn.is_pressed(StellarUnicorn.SWITCH_BRIGHTNESS_UP):
        if brightness_level < 10:
            brightness_level += 1
            update_brightness()
            print("Brightness:", brightness_level)
            time.sleep(0.2)
    if unicorn.is_pressed(StellarUnicorn.SWITCH_BRIGHTNESS_DOWN):
        if brightness_level > 1:
            brightness_level -= 1
            update_brightness()
            print("Brightness:", brightness_level)
            time.sleep(0.2)

# === Connect Wi-Fi ===
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            time.sleep(0.2)
    print("Connected to Wi-Fi:", wlan.ifconfig())
    return wlan

# === Display Frame ===
def show_frame(data):
    if len(data) < PIXEL_COUNT * 3:
        return
    for i in range(PIXEL_COUNT):
        r = data[i * 3]
        g = data[i * 3 + 1]
        b = data[i * 3 + 2]
        x = i % 16
        y = i // 16
        graphics.set_pen(graphics.create_pen(r, g, b))
        graphics.pixel(x, y)
    unicorn.update(graphics)

# === Idle Pulse ===
last_packet_time = time.ticks_ms()

def pulse_indicator():
    t = (time.ticks_ms() // 50) % 100
    b = 25 if t < 50 else 100 - t

    # Set all pixels to off
    graphics.set_pen(graphics.create_pen(0, 0, 0))
    graphics.clear()

    # Draw the pulsing red pixel at (0, 15)
    graphics.set_pen(graphics.create_pen(b, 0, 0))
    graphics.pixel(0, 15)

    unicorn.update(graphics)


# === Main Loop ===
def run_ddp_receiver():
    global last_packet_time
    connect_wifi()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", DDP_PORT))
    sock.setblocking(False)
    print(f"DDP Receiver listening on UDP {DDP_PORT}...")

    while True:
        check_buttons()

        try:
            data, _ = sock.recvfrom(MAX_PACKET_SIZE + 40)
            if len(data) >= 10:
                pixel_data = data[10:]
                show_frame(pixel_data)
                last_packet_time = time.ticks_ms()
        except:
            pass

        # Idle pulse
        if time.ticks_diff(time.ticks_ms(), last_packet_time) > 5000:
            pulse_indicator()

        time.sleep(0.01)

run_ddp_receiver()

