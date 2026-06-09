"""
WiFi arrow-key remote control for the Pico 2 W robot.
======================================================

The Pico 2 W has built-in WiFi. This script turns the robot into its own
WiFi access point and serves a small web page. You drive the robot with the
arrow keys (or WASD) from any device that joins the network and opens the page
in a browser -- no software to install on your PC.

HOW TO RUN
----------
1. Open this file in Thonny (with the Pico 2 W selected as the interpreter)
   and press Run/F5.  ->  OR, from the serial REPL, type:  import wifi_control
   (This runs INSTEAD of the code.py demo -- don't run both at once, they use
    the same motor pins.)

2. Watch the serial output. It prints the network name and the address, e.g.
       Connect your PC to WiFi:  UBISS-Robot   (password: CHANGE_ME)
       Then open a browser to:   http://192.168.4.1

3. On your PC: join that WiFi network, open the address in a browser, then
   hold the arrow keys to drive.  (Your PC has no internet while joined to the
   robot's network -- that's normal for access-point mode.)

CALIBRATION (do this once, it depends on how the motors are wired/mounted)
--------------------------------------------------------------------------
* If UP drives the robot backwards  -> negate both numbers in "F" and "B".
* If LEFT and RIGHT are swapped      -> swap the "L" and "R" lines.
See the DIRECTIONS table below.
"""

import os
import time
import asyncio

import board
import wifi
import socketpool

from motor import StepperMotor

# ---- WiFi access-point settings (override in settings.toml if you like) ----
AP_SSID = os.getenv("AP_SSID") or "UBISS-Robot"
AP_PASSWORD = os.getenv("AP_PASSWORD") or "CHANGE_ME"   # must be 8-63 chars

# ---- Motor setup (same pins as code.py) ----
SPEED_RPM = 8        # 28BYJ-48 steppers run reliably up to ~10-12 rpm
motor1 = StepperMotor(board.GP15, board.GP16, board.GP17, board.GP18, rpm=SPEED_RPM)
motor2 = StepperMotor(board.GP19, board.GP20, board.GP21, board.GP22, rpm=SPEED_RPM)

# ---- Drive configuration ----
# Each command maps to (motor1_direction, motor2_direction).
# code.py's demo drives straight with both motors the SAME sign, and turns with
# OPPOSITE signs, so we follow that convention here.
DIRECTIONS = {
    "F": (1, 1),     # forward
    "B": (-1, -1),   # back
    "L": (-1, 1),    # rotate left
    "R": (1, -1),    # rotate right
    "S": (0, 0),     # stop
}
LEAD = 200           # steps to keep the target ahead of position (smooth motion)
DEADMAN = 0.8        # seconds: auto-stop if no command arrives (safety)

# Current drive state, shared between the web server and the drive loop.
state = "S"
last_cmd = time.monotonic()


# ---------------------------------------------------------------------------
# Motor control
# ---------------------------------------------------------------------------
async def drive_loop():
    """Continuously keep the motor targets ahead of position while a key is
    held, and stop immediately when the state is 'S' (or the deadman trips)."""
    global state
    while True:
        # Safety: if we haven't heard a move command recently, stop.
        if state != "S" and (time.monotonic() - last_cmd) > DEADMAN:
            state = "S"

        d1, d2 = DIRECTIONS[state]
        if d1 == 0 and d2 == 0:
            motor1.move_to(motor1.position)   # halt at current position
            motor2.move_to(motor2.position)
        else:
            motor1.move_to(motor1.position + d1 * LEAD)
            motor2.move_to(motor2.position + d2 * LEAD)

        await asyncio.sleep(0.05)


# ---------------------------------------------------------------------------
# Web page (captures arrow keys and sends commands back to the robot)
# ---------------------------------------------------------------------------
PAGE = """<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Robot Control</title>
<style>
  body { font-family: sans-serif; text-align: center; background: #111; color: #eee;
         user-select: none; -webkit-user-select: none; touch-action: none; }
  h1 { font-size: 1.2em; margin: 16px; }
  #pad { display: inline-grid; grid-template-columns: repeat(3, 80px);
         grid-gap: 8px; margin-top: 10px; }
  button { font-size: 28px; height: 80px; border: none; border-radius: 12px;
           background: #333; color: #eee; }
  button:active, button.on { background: #2a7; color: #000; }
  .blank { visibility: hidden; }
  #hint { color: #888; margin-top: 18px; font-size: 0.9em; }
</style>
</head>
<body>
  <h1>Use the arrow keys (or WASD) to drive</h1>
  <div id="pad">
    <div class="blank"></div>
    <button data-cmd="F">&#9650;</button>
    <div class="blank"></div>
    <button data-cmd="L">&#9664;</button>
    <button data-cmd="S">&#9209;</button>
    <button data-cmd="R">&#9654;</button>
    <div class="blank"></div>
    <button data-cmd="B">&#9660;</button>
    <div class="blank"></div>
  </div>
  <p id="hint">Hold a key to move, release to stop.</p>
<script>
  let active = null, timer = null;
  const send = c => fetch('/' + c).catch(() => {});

  function start(cmd) {
    if (active === cmd) return;
    active = cmd;
    send(cmd);
    clearInterval(timer);                       // re-send so the robot's
    timer = setInterval(() => send(cmd), 250);  // deadman timer never trips
    document.querySelectorAll('button').forEach(b =>
      b.classList.toggle('on', b.dataset.cmd === cmd));
  }
  function stop() {
    active = null;
    clearInterval(timer);
    send('S');
    document.querySelectorAll('button').forEach(b => b.classList.remove('on'));
  }

  const KEYS = { ArrowUp:'F', ArrowDown:'B', ArrowLeft:'L', ArrowRight:'R',
                 w:'F', s:'B', a:'L', d:'R', W:'F', S:'B', A:'L', D:'R' };
  addEventListener('keydown', e => {
    const c = KEYS[e.key];
    if (!c) return;
    e.preventDefault();
    if (!e.repeat) start(c);
  });
  addEventListener('keyup', e => {
    const c = KEYS[e.key];
    if (!c) return;
    e.preventDefault();
    if (active === c) stop();
  });

  // On-screen buttons (touch / mouse) as a fallback.
  document.querySelectorAll('button').forEach(b => {
    const cmd = b.dataset.cmd;
    b.addEventListener('pointerdown', e => { e.preventDefault();
      cmd === 'S' ? stop() : start(cmd); });
    b.addEventListener('pointerup', stop);
    b.addEventListener('pointerleave', () => { if (active === cmd) stop(); });
    b.addEventListener('pointercancel', stop);
  });
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Minimal non-blocking HTTP server (built on raw sockets, no extra libraries)
# ---------------------------------------------------------------------------
def http_response(content_type, body):
    if isinstance(body, str):
        body = body.encode("utf-8")
    header = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: %s\r\n"
        "Content-Length: %d\r\n"
        "Connection: close\r\n"
        "\r\n" % (content_type, len(body))
    )
    return header.encode("utf-8") + body


async def read_request_line(conn, timeout=1.0):
    """Read just the first line of the HTTP request (all we need)."""
    buf = b""
    chunk = bytearray(256)
    start = time.monotonic()
    while b"\r\n" not in buf:
        if time.monotonic() - start > timeout:
            break
        try:
            n = conn.recv_into(chunk)
            if n == 0:               # client closed the connection
                break
            buf += bytes(chunk[:n])
        except OSError:              # no data yet -> yield and retry
            await asyncio.sleep(0)
    return buf.split(b"\r\n", 1)[0].decode("utf-8") if buf else ""


async def send_all(conn, data, timeout=1.0):
    view = memoryview(data)
    sent = 0
    start = time.monotonic()
    while sent < len(data):
        if time.monotonic() - start > timeout:
            break
        try:
            sent += conn.send(view[sent:])
        except OSError:
            await asyncio.sleep(0)


async def handle(conn):
    global state, last_cmd
    conn.setblocking(False)
    line = await read_request_line(conn)        # e.g. "GET /F HTTP/1.1"
    if not line:
        return

    parts = line.split(" ")
    path = parts[1].split("?", 1)[0] if len(parts) > 1 else "/"

    if path == "/" or path == "/index.html":
        await send_all(conn, http_response("text/html", PAGE))
        return

    cmd = path[1:].upper()                       # "/F" -> "F"
    if cmd in DIRECTIONS:
        state = cmd
        last_cmd = time.monotonic()
    await send_all(conn, http_response("text/plain", "ok"))


async def serve(pool):
    server = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
    try:                                         # frees the port on quick re-runs
        server.setsockopt(pool.SOL_SOCKET, pool.SO_REUSEADDR, 1)
    except (AttributeError, OSError):
        pass
    server.bind(("0.0.0.0", 80))
    server.listen(4)
    server.setblocking(False)
    print("Web server ready.")

    while True:
        try:
            conn, _addr = server.accept()
        except OSError:                          # no pending connection -> idle
            await asyncio.sleep(0.02)
            continue
        try:
            await handle(conn)
        except Exception as e:                   # never let one bad request kill us
            print("request error:", e)
        finally:
            conn.close()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
async def main():
    print("Starting WiFi access point:", AP_SSID)
    wifi.radio.start_ap(ssid=AP_SSID, password=AP_PASSWORD)
    ip = wifi.radio.ipv4_address_ap
    print("-" * 48)
    print("Connect your PC to WiFi:  %s   (password: %s)" % (AP_SSID, AP_PASSWORD))
    print("Then open a browser to:   http://%s" % ip)
    print("-" * 48)

    pool = socketpool.SocketPool(wifi.radio)

    asyncio.create_task(motor1.run())
    asyncio.create_task(motor2.run())
    asyncio.create_task(drive_loop())
    await serve(pool)


asyncio.run(main())
