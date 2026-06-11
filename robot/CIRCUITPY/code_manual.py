# code_manual.py — three-mode robot controller
# WiFi page at http://192.168.4.1/ with three modes:
#   MANUAL  — arrow keys / WASD / on-screen pad drive the robot
#   AUTO    — autonomous beacon-following + docking pipeline
#   SEARCH  — ultrasonic object scan (lighthouse + specularity probe)
# Boots in MANUAL: robot stays put until you switch on the web page.
# NOTE: serves its own combined page — do NOT also run telemetry.serve().
import time
import math
import board
import asyncio
import analogio
import digitalio

from motor import StepperMotor
import telemetry
from telemetry import log

# ---- motors (differential drive) ----
motor1 = StepperMotor(board.GP15, board.GP16, board.GP17, board.GP18, rpm=8)
motor2 = StepperMotor(board.GP19, board.GP20, board.GP21, board.GP22, rpm=8)

# ---- light sensors (photodiodes) ----
sensorL = analogio.AnalogIn(board.GP26)
sensorR = analogio.AnalogIn(board.GP28)

# ---- docking hardware ----
hall = digitalio.DigitalInOut(board.GP27)
hall.direction = digitalio.Direction.INPUT
hall.pull = digitalio.Pull.UP

led = digitalio.DigitalInOut(board.GP8)
led.direction = digitalio.Direction.OUTPUT
led.value = False

# ---- ultrasonic sensor (HC-SR04) ----
us_trig = digitalio.DigitalInOut(board.GP12)
us_trig.direction = digitalio.Direction.OUTPUT
us_trig.value = False

us_echo = digitalio.DigitalInOut(board.GP13)
us_echo.direction = digitalio.Direction.INPUT

# ================= TUNABLE CONSTANTS =================
FWD_M1, FWD_M2   = -1, 1     # forward = OPPOSITE signs (mirror-mounted motors)
SPIN_M1, SPIN_M2 = -1, -1    # spin in place = SAME sign
STEER_SIGN       = 1
BRIGHTER_IS_HIGHER = True

# -- blinking-beacon detection (phone strobe app) --
USE_FLICKER = True
BEACON_HZ   = 9.4
LOOK_PERIODS = 2.4
SMOOTH_MS   = 10

DEADBAND_FRAC = 0.20
TURN_GAIN = 1400
TURN_MIN  = 60
TURN_MAX  = 500

NEAR_LEVEL = 7000
FWD_FAR    = 1200
FWD_NEAR   = 400

# 360 light-seek
SPIN_STEP       = 360
FULL_TURN_STEPS = 12000
SEEK_EXIT_LEVEL = 1400
RAIL_LEVEL      = 64000
R_DISABLED      = False
AIM_EVERY       = 4
LOST_LEVEL      = 1000 if USE_FLICKER else 1500
MISS_LIMIT      = 3

# docking (hall sensor GP27, indicator LED GP8)
DOCKING_ENABLED = True
MAGNET_DETECTED = True
SETTLE_TIME     = 0.5

# mat rake
RAKE_ENABLED = False
SWEEP_LEVEL = 3000
RAKE_STEPS  = 990
RAKE_CREEP  = 160
RAKE_CYCLES = 18
RAKE_BACKUP = 2000

# manual mode
LEAD    = 200
DEADMAN = 0.8

# ---- ultrasonic / object search ----
STEPS_PER_DEG  = FULL_TURN_STEPS / 360
STEPS_PER_CM   = 200.0
PING_DELAY     = 0.035
ECHO_TIMEOUT   = 0.04
MIN_RANGE_CM   = 3
MAX_RANGE_CM   = 200
LIGHT_DEG      = 8
NEAR_WALL_CM   = 25
TARGET_CM      = 40
PROBE_DEG      = 5
PROBE_PINGS    = 5
HIT_THRESH     = 0.4
DROPOUT_MIN    = 2
SPIKE_CM       = 4
SPIKE_MIN      = 2
OBS_FRAC       = 0.65
FLAT_CM        = 3
MIN_FACE_LEN   = 3
FACE_MIN       = 2
# ====================================================


def brightness(ai):
    v = ai.value
    return v if BRIGHTER_IS_HIGHER else (65535 - v)


async def read_lr():
    global raw_extremes
    if not USE_FLICKER:
        return brightness(sensorL), brightness(sensorR)
    min_l = min_r = 65535
    max_l = max_r = 0
    t_end = time.monotonic() + LOOK_PERIODS / BEACON_HZ
    while time.monotonic() < t_end:
        sum_l = sum_r = n = 0
        t_smooth = time.monotonic() + SMOOTH_MS / 1000
        while time.monotonic() < t_smooth:
            sum_l += sensorL.value
            sum_r += sensorR.value
            n += 1
        l = sum_l // n
        r = sum_r // n
        if l < min_l: min_l = l
        if l > max_l: max_l = l
        if r < min_r: min_r = r
        if r > max_r: max_r = r
        await asyncio.sleep(0)
    raw_extremes = (min_l, max_l, min_r, max_r)
    return max_l - min_l, max_r - min_r


raw_extremes = (0, 0, 0, 0)


def drive_forward(steps):
    motor1.move(FWD_M1 * steps)
    motor2.move(FWD_M2 * steps)


def spin(steps):
    motor1.move(SPIN_M1 * steps)
    motor2.move(SPIN_M2 * steps)


def docked():
    return DOCKING_ENABLED and hall.value == MAGNET_DETECTED


async def wait_for_motors(*motors):
    while any(m.busy for m in motors):
        await asyncio.sleep(0)


async def wait_or_dock(*motors):
    while any(m.busy for m in motors):
        if docked():
            for m in motors:
                m.move_to(m.position)
            return True
        await asyncio.sleep(0)
    return docked()


# ---- ultrasonic primitives ----

def ping_cm():
    us_trig.value = False
    time.sleep(0.000005)
    us_trig.value = True
    time.sleep(0.00001)
    us_trig.value = False
    deadline = time.monotonic() + ECHO_TIMEOUT
    while not us_echo.value:
        if time.monotonic() > deadline:
            return -1.0
    t0 = time.monotonic()
    while us_echo.value:
        if time.monotonic() > deadline:
            return -1.0
    return (time.monotonic() - t0) * 17150.0


def ping_median(n=3):
    vals = []
    for _ in range(n):
        d = ping_cm()
        if d > MIN_RANGE_CM:
            vals.append(d)
        time.sleep(PING_DELAY)
    if not vals:
        return -1.0
    vals.sort()
    return vals[len(vals) // 2]


def ping_probe():
    vals = []
    for _ in range(PROBE_PINGS):
        d = ping_cm()
        if MIN_RANGE_CM < d < MAX_RANGE_CM:
            vals.append(d)
        time.sleep(PING_DELAY)
    hr = len(vals) / PROBE_PINGS
    md = -1.0
    if vals:
        vals.sort()
        md = vals[len(vals) // 2]
    return hr, md


# ---- mapping motor helpers ----

async def drive_cm(cm):
    motor1.move(FWD_M1 * int(cm * STEPS_PER_CM))
    motor2.move(FWD_M2 * int(cm * STEPS_PER_CM))
    await wait_for_motors(motor1, motor2)


async def turn_deg(deg):
    motor1.move(SPIN_M1 * int(deg * STEPS_PER_DEG))
    motor2.move(SPIN_M2 * int(deg * STEPS_PER_DEG))
    await wait_for_motors(motor1, motor2)


# ===================== AUTONOMOUS (DOCKING) PIPELINE =====================

async def rake_for_magnet():
    log("RAKE: beacon-close - sweeping the mat for the magnet")
    net = RAKE_STEPS
    spin(RAKE_STEPS)
    if await wait_or_dock(motor1, motor2):
        return True
    sign = -1
    for _ in range(RAKE_CYCLES):
        drive_forward(RAKE_CREEP)
        if await wait_or_dock(motor1, motor2):
            return True
        net += sign * 2 * RAKE_STEPS
        spin(sign * 2 * RAKE_STEPS)
        if await wait_or_dock(motor1, motor2):
            return True
        sign = -sign
    log("RAKE: no magnet - recentre, back up", RAKE_BACKUP, "steps, re-approach")
    spin(-net)
    if await wait_or_dock(motor1, motor2):
        return True
    drive_forward(-RAKE_BACKUP)
    return await wait_or_dock(motor1, motor2)


async def seek_light():
    log("SEEK: rotating to find the light...")
    best = -1
    best1, best2 = motor1.position, motor2.position
    done = 0
    while done < FULL_TURN_STEPS:
        spin(SPIN_STEP)
        await wait_for_motors(motor1, motor2)
        done += SPIN_STEP
        l, r = await read_lr()
        level = l + r
        if level >= SEEK_EXIT_LEVEL:
            log("SEEK: strong signal (", level, ") - early lock, driving now")
            return
        if level > best:
            best = level
            best1, best2 = motor1.position, motor2.position
    motor1.move_to(best1)
    motor2.move_to(best2)
    await wait_for_motors(motor1, motor2)
    log("SEEK: locked on (level", best, ")")


async def fine_aim():
    best, best_at = -1, 2
    spin(-2 * SPIN_STEP)
    if await wait_or_dock(motor1, motor2):
        return True
    for k in range(5):
        if k:
            spin(SPIN_STEP)
            if await wait_or_dock(motor1, motor2):
                return True
        l, r = await read_lr()
        if max(l, r) > best:
            best, best_at = max(l, r), k
    spin((best_at - 4) * SPIN_STEP)
    if await wait_or_dock(motor1, motor2):
        return True
    log("AIM: best", best, "at offset", best_at - 2)
    return False


async def light_follow():
    await seek_light()
    misses = 0
    strides = 0
    while not docked():
        l, r = await read_lr()
        if (l + r) < LOST_LEVEL:
            misses += 1
            log("weak look", misses, "of", MISS_LIMIT, "- L:", l, " R:", r,
                " raw", raw_extremes)
            if misses >= MISS_LIMIT:
                log("LOST -> re-seek")
                await seek_light()
                misses = 0
            continue
        misses = 0
        lmin, _, rmin, _ = raw_extremes
        tag = ""
        if R_DISABLED or (rmin > RAIL_LEVEL and lmin <= RAIL_LEVEL):
            r = l
            tag = "[R off]"
        elif lmin > RAIL_LEVEL and rmin <= RAIL_LEVEL:
            l = r
            tag = "[L blind]"
        diff = l - r
        if abs(diff) > DEADBAND_FRAC * (l + r) / 2:
            toward_left = diff > 0
            turn = min(TURN_MAX, max(TURN_MIN, int(TURN_GAIN * abs(diff) / (l + r))))
            spin(STEER_SIGN * (turn if toward_left else -turn))
            log("L:", l, " R:", r, " -> turn", "LEFT" if toward_left else "RIGHT", turn, tag)
            if await wait_or_dock(motor1, motor2):
                break
        else:
            log("L:", l, " R:", r, " -> straight", tag)
        if RAKE_ENABLED and max(l, r) >= SWEEP_LEVEL:
            log("NEAR DOCK (L", l, " R", r, " raw", raw_extremes, ") -> rake")
            if await rake_for_magnet():
                break
            continue
        steps = FWD_NEAR if (l + r) > NEAR_LEVEL else FWD_FAR
        drive_forward(steps)
        if await wait_or_dock(motor1, motor2):
            break
        strides += 1
        if strides % AIM_EVERY == 0:
            if await fine_aim():
                break

    log("HALL: dock contact detected")


async def dock_sequence():
    await wait_for_motors(motor1, motor2)
    await asyncio.sleep(SETTLE_TIME)
    if docked() and not (motor1.busy or motor2.busy):
        led.value = True
        log("DOCKED + STATIONARY -> indicator ON. Holding position.")
        return True
    log("dock contact lost during settle -> resume homing")
    return False


# ===================== OBJECT SEARCH (MAPPING) PIPELINE =====================

async def lighthouse():
    log("PHASE 1  LIGHTHOUSE — scanning from corner")
    readings = []
    step_n = int(LIGHT_DEG * STEPS_PER_DEG)
    angle = 0.0
    done = 0
    total = int(360 * STEPS_PER_DEG)

    while done < total:
        d = ping_median()
        readings.append((angle, d))
        motor1.move(SPIN_M1 * step_n)
        motor2.move(SPIN_M2 * step_n)
        await wait_for_motors(motor1, motor2)
        done += step_n
        angle += LIGHT_DEG

    interior = [(a, d) for a, d in readings if d > NEAR_WALL_CM]
    log("lighthouse: ", len(interior), "/", len(readings), " interior readings")

    if len(interior) < 3:
        log("lighthouse: cannot see interior — try repositioning")
        return None

    dists = sorted(d for _, d in interior)
    median_d = dists[len(dists) // 2]
    threshold = median_d * OBS_FRAC
    cluster = [(a, d) for a, d in interior if d < threshold]

    if not cluster:
        cluster = sorted(interior, key=lambda x: x[1])[:3]
        log("lighthouse: no clear cluster, using 3 shortest")

    mid = cluster[len(cluster) // 2]
    log("lighthouse: obstacle ~", int(mid[1]), "cm at ",
        int(mid[0]), "deg  (", len(cluster), " readings)")

    for i in range(0, len(readings), 12):
        ch = readings[i:i + 12]
        log("  ", " ".join("%d:%d" % (int(a), int(d)) for a, d in ch if d > 0))

    return mid[0], mid[1]


async def approach_obj(angle, dist):
    log("PHASE 2  APPROACH — turning ", int(angle), " deg")
    await turn_deg(angle)

    to_go = dist - TARGET_CM
    while to_go > 5:
        step = min(to_go, 15)
        await drive_cm(step)
        to_go -= step
        d = ping_median()
        if 0 < d <= TARGET_CM + 8:
            log("approach: in range (", int(d), " cm)")
            break
        if d > 0:
            to_go = d - TARGET_CM

    d = ping_median()
    log("approach: stopped ~", int(d) if d > 0 else "?", "cm from obstacle")


async def us_probe():
    log("PHASE 3  SPECULARITY PROBE — ", PROBE_DEG, " deg steps, ",
        PROBE_PINGS, " pings each")

    await turn_deg(180)

    readings = []
    step_n = int(PROBE_DEG * STEPS_PER_DEG)
    angle = 0.0
    done = 0
    total = int(360 * STEPS_PER_DEG)

    while done < total:
        hr, md = ping_probe()
        readings.append((angle, hr, md))
        motor1.move(SPIN_M1 * step_n)
        motor2.move(SPIN_M2 * step_n)
        await wait_for_motors(motor1, motor2)
        done += step_n
        angle += PROBE_DEG

    log("probe: ", len(readings), " readings collected")
    return readings


def count_faces(dists):
    run = 0
    faces = 0
    for i in range(1, len(dists)):
        if abs(dists[i] - dists[i - 1]) <= FLAT_CM:
            run += 1
        else:
            if run >= MIN_FACE_LEN:
                faces += 1
            run = 0
    if run >= MIN_FACE_LEN:
        faces += 1
    return faces


def classify(readings):
    got_echo = [(a, hr, d) for a, hr, d in readings if d > MIN_RANGE_CM]
    if len(got_echo) < 5:
        log("classify: too few echoes (", len(got_echo), ")")
        return "disk"

    dists = sorted(d for _, _, d in got_echo)
    median_d = dists[len(dists) // 2]
    threshold = median_d * OBS_FRAC

    obs_hits = [(a, hr, d) for a, hr, d in got_echo if d < threshold]
    if len(obs_hits) < 2:
        log("classify: obstacle sector too narrow")
        return "disk"

    margin = PROBE_DEG * 5
    lo = min(a for a, _, _ in obs_hits) - margin
    hi = max(a for a, _, _ in obs_hits) + margin
    sector = [(a, hr, d) for a, hr, d in readings if lo <= a <= hi]

    log("classify: sector ", int(lo), "-", int(hi), " deg, ",
        len(sector), " readings, threshold ", int(threshold), " cm")

    sd = [d for _, _, d in sector if d > MIN_RANGE_CM]

    dropouts = 0
    in_drop = False
    for _, hr, _ in sector:
        if hr < HIT_THRESH:
            if not in_drop:
                dropouts += 1
                in_drop = True
        else:
            in_drop = False

    spikes = 0
    for i in range(1, len(sd)):
        if abs(sd[i] - sd[i - 1]) >= SPIKE_CM:
            spikes += 1

    faces = count_faces(sd)

    if sd:
        mean = sum(sd) / len(sd)
        std = math.sqrt(sum((x - mean) ** 2 for x in sd) / len(sd))
    else:
        std = 0.0

    is_tri = (dropouts >= DROPOUT_MIN
              or spikes >= SPIKE_MIN
              or faces >= FACE_MIN)
    verdict = "triangle" if is_tri else "disk"

    log("classify: dropouts=", dropouts, "  spikes=", spikes,
        "  faces=", faces, "  std=", round(std, 1),
        " -> ", verdict.upper())

    for a, hr, d in sector:
        tag = ""
        if hr < HIT_THRESH:
            tag = " <<<DROP"
        log("  %3d deg  hit %3d%%  %s cm%s"
            % (int(a), int(hr * 100),
               ("%3d" % int(d)) if d > 0 else "---", tag))

    return verdict


# ===================== MODE TASKS =====================

async def autonomous():
    while True:
        await light_follow()
        if await dock_sequence():
            break
    while True:
        await asyncio.sleep(1)


async def search_mission():
    d = ping_cm()
    log("SEARCH: ultrasonic =", round(d, 1) if d > 0 else "NO ECHO", "cm")
    if d < 0:
        log("HC-SR04 not responding — check Trig->GP12, Echo->GP13, VCC->3V3")
        return

    t0 = time.monotonic()

    result = await lighthouse()

    if result is None:
        log("FALLBACK: driving toward center, retrying")
        await turn_deg(45)
        await drive_cm(45)
        result = await lighthouse()

    if result:
        await approach_obj(result[0], result[1])
    else:
        log("FALLBACK: no obstacle found, probing from here")

    data = await us_probe()
    verdict = classify(data)

    log("total elapsed ", int(time.monotonic() - t0), " s")
    log("========================================")
    log("  RESULT:  ", verdict.upper())
    log("========================================")

    while True:
        led.value = True
        await asyncio.sleep(0.4 if verdict == "triangle" else 3600)
        if verdict == "triangle":
            led.value = False
            await asyncio.sleep(0.4)


# ===================== MANUAL MODE + WEB UI =====================
DIRECTIONS = {
    "F": (FWD_M1, FWD_M2),
    "B": (-FWD_M1, -FWD_M2),
    "L": (SPIN_M1, SPIN_M2),
    "R": (-SPIN_M1, -SPIN_M2),
    "S": (0, 0),
}

mode = "manual"
manual_state = "S"
last_cmd = 0.0
auto_task = None
blink_until = time.monotonic() + 30


def halt_motors():
    motor1.move_to(motor1.position)
    motor2.move_to(motor2.position)


def set_mode(m):
    global mode, auto_task, manual_state, blink_until
    if m not in ("auto", "manual", "search") or m == mode:
        return
    mode = m
    manual_state = "S"
    if auto_task is not None:
        auto_task.cancel()
        auto_task = None
    halt_motors()
    led.value = False
    if m == "manual":
        blink_until = time.monotonic() + 30
        log("MODE: MANUAL - arrow keys drive; LED blinks 30 s then = magnet")
    elif m == "auto":
        log("MODE: AUTO - restarting from seek")
        auto_task = asyncio.create_task(autonomous())
    else:
        log("MODE: SEARCH - starting object scan")
        auto_task = asyncio.create_task(search_mission())


async def drive_loop():
    global manual_state
    was_magnet = False
    while True:
        if mode == "manual":
            if manual_state != "S" and time.monotonic() - last_cmd > DEADMAN:
                manual_state = "S"
            d1, d2 = DIRECTIONS[manual_state]
            if d1 == 0 and d2 == 0:
                halt_motors()
            else:
                motor1.move_to(motor1.position + d1 * LEAD)
                motor2.move_to(motor2.position + d2 * LEAD)
            now = time.monotonic()
            magnet = hall.value == MAGNET_DETECTED
            if magnet:
                led.value = True
            elif now < blink_until:
                led.value = (now % 1.0) < 0.5
            else:
                led.value = False
            if magnet and not was_magnet:
                log("HALL: magnet under the sensor")
            was_magnet = magnet
        await asyncio.sleep(0.05)


PAGE = """<!DOCTYPE html><html><head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>UBISS robot</title><style>
body{font-family:sans-serif;background:#111;color:#eee;text-align:center;user-select:none;margin:0;padding:1em}
#modes{display:flex;gap:8px;justify-content:center;margin-bottom:.5em}
#modes button{flex:1;max-width:140px;font-size:16px;padding:.5em;border:0;border-radius:10px;background:#333;color:#eee}
#modes button.on{background:#2a7;color:#000}
#pad{display:inline-grid;grid-template-columns:repeat(3,70px);grid-gap:6px;margin:.5em;opacity:.25}
#pad.on{opacity:1}
#pad button{font-size:24px;height:70px;border:0;border-radius:10px;background:#333;color:#eee}
#pad button.on{background:#2a7;color:#000}
i{visibility:hidden}
pre{background:#000;color:#9f9;font:13px/1.4 monospace;text-align:left;padding:.8em;border-radius:8px;max-height:50vh;overflow:auto}
</style></head><body>
<div id="modes">
<button data-m="manual">MANUAL</button>
<button data-m="auto">AUTO</button>
<button data-m="search">SEARCH</button>
</div>
<div id="pad"><i></i><button data-c="F">&#9650;</button><i></i>
<button data-c="L">&#9664;</button><button data-c="S">&#9209;</button><button data-c="R">&#9654;</button>
<i></i><button data-c="B">&#9660;</button><i></i></div>
<p style="color:#888;font-size:.85em">manual: hold arrows / WASD or the pad</p>
<pre id="log">connecting...</pre>
<script>
var mode='manual',active=null,timer=null;
function send(p){fetch(p).catch(function(){})}
function ui(){
 document.querySelectorAll('#modes button').forEach(function(b){
  b.classList.toggle('on',b.dataset.m==mode)});
 document.getElementById('pad').classList.toggle('on',mode=='manual')}
function poll(){fetch('/log').then(function(r){return r.text()}).then(function(t){
 var i=t.indexOf('\\n');mode=t.slice(0,i).split(' ')[1]||'manual';
 document.getElementById('log').textContent=t.slice(i+1);ui()}).catch(function(){})}
setInterval(poll,1000);poll();
document.querySelectorAll('#modes button').forEach(function(b){
 b.onclick=function(){send('/mode?m='+b.dataset.m);setTimeout(poll,200)}});
function pads(){return document.querySelectorAll('#pad button')}
function start(c){if(mode!='manual'||active==c)return;active=c;send('/'+c);
 clearInterval(timer);timer=setInterval(function(){send('/'+c)},250);
 pads().forEach(function(b){b.classList.toggle('on',b.dataset.c==c)})}
function stop(){active=null;clearInterval(timer);send('/S');
 pads().forEach(function(b){b.classList.remove('on')})}
var K={ArrowUp:'F',ArrowDown:'B',ArrowLeft:'L',ArrowRight:'R',w:'F',s:'B',a:'L',d:'R'};
addEventListener('keydown',function(e){var c=K[e.key]||K[e.key.toLowerCase&&e.key.toLowerCase()];
 if(!c)return;e.preventDefault();if(!e.repeat)start(c)});
addEventListener('keyup',function(e){var c=K[e.key]||K[e.key.toLowerCase&&e.key.toLowerCase()];
 if(!c)return;e.preventDefault();if(active==c)stop()});
pads().forEach(function(b){var c=b.dataset.c;
 b.addEventListener('pointerdown',function(e){e.preventDefault();c=='S'?stop():start(c)});
 b.addEventListener('pointerup',stop);
 b.addEventListener('pointerleave',function(){if(active==c)stop()});
 b.addEventListener('pointercancel',stop)});
</script></body></html>"""


def _http(content_type, body):
    if isinstance(body, str):
        body = body.encode("utf-8")
    head = ("HTTP/1.1 200 OK\r\nContent-Type: %s\r\nContent-Length: %d\r\n"
            "Connection: close\r\n\r\n" % (content_type, len(body)))
    return head.encode("utf-8") + body


def _handle(conn):
    global manual_state, last_cmd
    conn.settimeout(2)
    req = bytearray(512)
    try:
        conn.recv_into(req)
    except OSError:
        return
    line = bytes(req).split(b"\r\n", 1)[0].decode("utf-8")
    parts = line.split(" ")
    full = parts[1] if len(parts) > 1 else "/"
    path, _, query = full.partition("?")

    if path == "/" or path == "/index.html":
        data = _http("text/html", PAGE)
    elif path == "/log":
        data = _http("text/plain",
                     "MODE " + mode + "\n" + "\n".join(reversed(telemetry._lines)))
    elif path == "/mode":
        set_mode(query.partition("=")[2])
        data = _http("text/plain", mode)
    else:
        cmd = path[1:].upper()
        if cmd in DIRECTIONS and mode == "manual":
            manual_state = cmd
            last_cmd = time.monotonic()
        data = _http("text/plain", "ok")

    mv = memoryview(data)
    sent = 0
    while sent < len(data):
        try:
            n = conn.send(mv[sent:])
        except OSError:
            break
        if not n:
            break
        sent += n


async def serve_ui():
    pool = telemetry._pool
    if pool is None:
        return
    srv = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
    try:
        srv.setsockopt(pool.SOL_SOCKET, pool.SO_REUSEADDR, 1)
    except (AttributeError, OSError):
        pass
    srv.bind(("0.0.0.0", 80))
    srv.listen(4)
    srv.setblocking(False)
    while True:
        try:
            conn, _addr = srv.accept()
        except OSError:
            await asyncio.sleep(0.02)
            continue
        try:
            _handle(conn)
        except Exception as e:
            log("web request error:", e)
        finally:
            try:
                conn.close()
            except Exception:
                pass
        await asyncio.sleep(0)
# ================================================================


async def main():
    global DOCKING_ENABLED, auto_task
    asyncio.create_task(motor1.run())
    asyncio.create_task(motor2.run())
    if telemetry.start():
        asyncio.create_task(serve_ui())
    asyncio.create_task(drive_loop())

    if DOCKING_ENABLED and hall.value == MAGNET_DETECTED:
        log("WARNING: hall reads 'docked' at boot - check wiring / MAGNET_DETECTED.")
        log("Docking checks DISABLED for this run (pure light-follow).")
        DOCKING_ENABLED = False

    d = ping_cm()
    log("boot: ultrasonic =", round(d, 1) if d > 0 else "NO ECHO", "cm")

    log("MODE: MANUAL at boot - robot waits. Switch mode on the web page.")
    while True:
        await asyncio.sleep(1)


asyncio.run(main())
