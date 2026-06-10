# code_manual.py - code.py PLUS a manual-drive mode on the WiFi page.
# Same autonomous pipeline (seek -> home -> dock), but http://192.168.4.1/
# now shows the log AND an AUTO/MANUAL toggle: in MANUAL the arrow keys
# (or WASD, or on-screen pad) drive the robot; the LED is solid ON (robot
# alive) and goes OUT over the magnet, so you can hunt it by hand. AUTO starts
# the autonomous run from the seek; back to MANUAL cancels it and halts.
# BOOTS IN MANUAL: the robot stays put on power-up until you press AUTO.
# Run from Thonny to try it; rename to code.py on the board to make it boot.
# NOTE: serves its own combined page - do NOT also run telemetry.serve().
import time
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
sensorL = analogio.AnalogIn(board.GP28)
sensorR = analogio.AnalogIn(board.GP26)

# ---- docking hardware ----
hall = digitalio.DigitalInOut(board.GP27)
hall.direction = digitalio.Direction.INPUT
hall.pull = digitalio.Pull.UP

led = digitalio.DigitalInOut(board.GP8)
led.direction = digitalio.Direction.OUTPUT
led.value = False            # indicator stays OFF until docked AND stationary

# ================= TUNABLE CONSTANTS =================
FWD_M1, FWD_M2   = 1, -1     # forward = OPPOSITE signs (mirror-mounted motors)
SPIN_M1, SPIN_M2 = 1, 1      # spin in place = SAME sign
STEER_SIGN       = 1         # set -1 if it steers AWAY from the light
BRIGHTER_IS_HIGHER = True    # set False if covering a sensor RAISES its number
                             # (only matters when USE_FLICKER = False)

# -- blinking-beacon detection (phone strobe app) --
USE_FLICKER = True           # True = home on the BLINKING light only; steady room light cancels
BEACON_HZ   = 9.4            # strobe blink rate, re-MEASURED with beacon_meter.py
                             # 2026-06-10 bright room: 9.38 Hz, 53% duty
LOOK_PERIODS = 2.4           # blink periods per look (~0.26 s). Was 1.2: at 1 m
                             # the beacon wobble is only ~900 over a ~40k ambient
                             # floor; one period gave +/-30% look noise -> false
                             # weak looks. Two+ full cycles steadies the estimate
SMOOTH_MS   = 10             # per-sample averaging window; >=10 ms cancels mains (100 Hz) flicker

DEADBAND_FRAC = 0.20         # turn only if |L-R| exceeds this fraction of the mean signal
                             # (relative, so it works at any distance/brightness)
# steering: turn size scales with how off-centre the light is (proportional)
TURN_GAIN = 1400             # turn steps = TURN_GAIN * |L-R| / (L+R), clamped:
                             # (900 gave 3-5 deg nudges that never cancelled the
                             #  leftward drift -> persistent RIGHT-arc in telemetry)
TURN_MIN  = 60               #   barely off-centre -> small trim
TURN_MAX  = 500              #   strongly off-centre -> one big correction (~15 deg)

# stride: cover ground when far, fine-tune when near (levels from live telemetry)
NEAR_LEVEL = 7000            # L+R above this = close to the beacon. One-eyed sum
                             # is 2L; mat-edge L measured ~5000 (beacon_meter
                             # 2026-06-10) -> fires just before the mat, switches
                             # to 2 cm strides for the magnet crossing.
                             # (Old 35000 was a two-eyed darker-room number.)
FWD_FAR    = 1200            # ~6 cm per advance when far
FWD_NEAR   = 400             # ~2 cm per advance when near

# 360 light-seek
SPIN_STEP       = 360        # steps per scan step (~11 deg; smaller = finer but slower scan)
FULL_TURN_STEPS = 12000      # steps for ONE full 360 in-place turn (CALIBRATE - see notes)
SEEK_EXIT_LEVEL = 1400       # scan early-exit, two-eyed again (R replaced).
                             # Bright room, L alone: facing at 1 m ~929, off-axis
                             # noise 300-420 -> two-eyed facing sum ~1900, noise
                             # ceiling ~840. 1400 sits between. If the new R is
                             # weak, the full-circle best-pick still recovers.
RAIL_LEVEL      = 64000      # raw MIN above this = diode pegged by ambient the
                             # whole look: it is BLIND (wobble ~0), not in the
                             # dark. Seen on R in the bright-room run: raw
                             # (25133, 25549, 65056, 65058) -> R yanked steering
R_DISABLED      = False      # R photodiode REPLACED 2026-06-10 (old one was
                             # stuck at ~65.3k = electrically dead). New diode
                             # untested - if it also rails, the blind-guard
                             # below auto-mirrors L, so this stays False
AIM_EVERY       = 4          # forward strides between 5-point re-aims: one-eyed
                             # straight legs drift off the beacon line; a quick
                             # +/-2-step scan every ~24 cm keeps the line honest
LOST_LEVEL      = 1000 if USE_FLICKER else 1500  # a look with L+R below this is
                             # "weak". With R mirrored from L the sum is 2L, and
                             # off-axis L noise runs 300-420 -> weak below L~500
MISS_LIMIT      = 3          # re-seek only after this many consecutive weak looks
                             # (single weak looks happen when a look lands in the
                             #  strobe's pause - don't restart the whole scan for one)

# docking (hall sensor GP27, indicator LED GP8)
DOCKING_ENABLED = True       # hall VERIFIED with neodymium magnet (hall_watch
                             # 2026-06-10: 4/4 clean detect/release cycles on GP27;
                             # GP10 dead - hall_test.py's old pin comment was stale)
MAGNET_DETECTED = True       # hall.value while the magnet is present; idles False.
                             # ONE pole only (unipolar) - mount the dock magnet
                             # working-face toward the sensor. NOTE: an unplugged
                             # hall floats HIGH = false "docked" (pull-up), and the
                             # boot self-check only catches that at boot - keep the
                             # hall connector seated.
SETTLE_TIME     = 0.5        # seconds fully stopped before the indicator turns on
                             # (the -5 rule: NEVER signal while moving)

# mat rake: no funnel built yet + the hall's trigger zone is small, so a
# straight approach can pass the magnet a few cm to one side and never fire.
# Once beacon-close, zigzag-creep so the sensor rakes the whole mat area.
RAKE_ENABLED = False         # OFF: ambient/app conditions shifted between runs
                             # and the rake fired at the start line -> robot
                             # wagged in place. Re-enable only after re-running
                             # beacon_meter in the FINAL room and re-setting
                             # SWEEP_LEVEL from that measurement.
SWEEP_LEVEL = 3000           # single-sensor wobble that starts the rake.
                             # CALIBRATED (beacon_meter 2026-06-10): mat distance
                             # ~15-20 cm reads 5020 on L, 1 m reads 929 -> 60% of
                             # mat = fires on arrival, silent on approach. L's 40k
                             # ambient baseline leaves only ~21k headroom, so the
                             # old 30000 was physically unreachable.
RAKE_STEPS  = 990            # half-swing ~30 deg: front sensor arcs ~+/-2.5 cm
                             # (was 20 deg - lateral wander dominated the misses)
RAKE_CREEP  = 160            # ~0.8 cm forward between swings: the rake mesh
                             # must be finer than the hall trigger radius
                             # (first run missed the magnet with 1.5 cm mesh)
RAKE_CYCLES = 18             # swings before giving up (~12 cm of mat depth)
RAKE_BACKUP = 2000           # ~10 cm reverse after an empty rake, re-approach

# manual mode (web page arrow keys). Directions derive from the SAME verified
# convention constants as autonomous driving, so they can't disagree.
LEAD    = 200                # steps the target stays ahead while a key is held
DEADMAN = 0.8                # s without a command -> auto stop (page re-sends
                             # the held key every 250 ms)
# ====================================================


def brightness(ai):
    v = ai.value
    return v if BRIGHTER_IS_HIGHER else (65535 - v)


async def read_lr():
    # One "look" with both sensors at once.
    # USE_FLICKER mode: watch for ~1.2 blink periods and return how much each
    # sensor WOBBLES (max - min). Steady room light doesn't wobble, so it
    # cancels out -- only the blinking torch registers. Each sample is itself
    # averaged over SMOOTH_MS, which erases the 100 Hz flicker of mains-powered
    # room lights. (BRIGHTER_IS_HIGHER is irrelevant here: blinking wobbles
    # the reading either way.)
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
    # raw levels for saturation diagnosis: max near 65535 = diode railed by
    # ambient light -> wobble collapses no matter how bright the strobe is
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
    # Like wait_for_motors, but watches the hall sensor DURING the move:
    # the instant we make dock contact, cancel any remaining motion.
    while any(m.busy for m in motors):
        if docked():
            for m in motors:
                m.move_to(m.position)
            return True
        await asyncio.sleep(0)
    return docked()


async def rake_for_magnet():
    # Endgame coverage: zigzag-creep over the mat, hall watched during every
    # move (incl. the recentre + backup - reversing onto the magnet is still
    # a dock). spin(+) = LEFT. True = contact; False = swept through clean,
    # caller backs onto the beacon line and re-approaches.
    log("RAKE: beacon-close - sweeping the mat for the magnet")
    net = RAKE_STEPS
    spin(RAKE_STEPS)                  # half-swing left off the centerline
    if await wait_or_dock(motor1, motor2):
        return True
    sign = -1
    for _ in range(RAKE_CYCLES):
        drive_forward(RAKE_CREEP)
        if await wait_or_dock(motor1, motor2):
            return True
        net += sign * 2 * RAKE_STEPS
        spin(sign * 2 * RAKE_STEPS)   # full swing across the centerline
        if await wait_or_dock(motor1, motor2):
            return True
        sign = -sign
    log("RAKE: no magnet - recentre, back up", RAKE_BACKUP, "steps, re-approach")
    spin(-net)                        # undo the leftover heading offset
    if await wait_or_dock(motor1, motor2):
        return True
    drive_forward(-RAKE_BACKUP)
    return await wait_or_dock(motor1, motor2)


async def seek_light():
    # Rotate one full turn, remember the heading with the most light,
    # then turn back to face it ("lock on").
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
    # One-eyed steering: straight legs drift off the beacon line, so every
    # AIM_EVERY strides nudge across 5 headings (+/-2 scan steps ~ +/-21 deg)
    # and keep the strongest. Hall watched during every nudge. Returns True
    # on dock contact.
    best, best_at = -1, 2
    spin(-2 * SPIN_STEP)
    if await wait_or_dock(motor1, motor2):
        return True
    for k in range(5):                  # headings -2..+2 SPIN_STEPs
        if k:
            spin(SPIN_STEP)
            if await wait_or_dock(motor1, motor2):
                return True
        l, r = await read_lr()
        if max(l, r) > best:
            best, best_at = max(l, r), k
    spin((best_at - 4) * SPIN_STEP)     # from +2 back to the best heading
    if await wait_or_dock(motor1, motor2):
        return True
    log("AIM: best", best, "at offset", best_at - 2)
    return False


async def light_follow():
    # 1) spin 360 to find & lock onto the beacon, 2) home in on it.
    # Exits as soon as the hall sensor reports dock contact.
    # (With DOCKING_ENABLED = False this never exits - pure homing test.)
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
            continue                    # hold position, just look again
        misses = 0
        # a railed diode reads "dark" while actually blinded by ambient -
        # don't let it yank the steering; mirror the seeing side instead
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
            continue                # empty rake: backed off, approach again
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
    # We just stopped on the dock. Settle, verify we are STILL docked and
    # fully stationary, and only then turn the indicator on (-5 rule).
    await wait_for_motors(motor1, motor2)
    await asyncio.sleep(SETTLE_TIME)
    if docked() and not (motor1.busy or motor2.busy):
        led.value = True
        log("DOCKED + STATIONARY -> indicator ON. Holding position.")
        return True
    log("dock contact lost during settle -> resume homing")
    return False


# ===================== MANUAL MODE + WEB UI =====================
DIRECTIONS = {
    "F": (FWD_M1, FWD_M2),        # forward = OPPOSITE signs (mirror-mounted)
    "B": (-FWD_M1, -FWD_M2),
    "L": (SPIN_M1, SPIN_M2),      # spin(+) = LEFT (verified on this robot)
    "R": (-SPIN_M1, -SPIN_M2),
    "S": (0, 0),
}

mode = "manual"                   # boot in MANUAL: robot stays put until you
                                  # switch to AUTO on the web page
manual_state = "S"
last_cmd = 0.0
auto_task = None


async def autonomous():
    # The whole code.py mission as one cancellable task: home, dock, hold.
    while True:
        await light_follow()
        if await dock_sequence():
            break
    while True:
        await asyncio.sleep(1)


def halt_motors():
    motor1.move_to(motor1.position)
    motor2.move_to(motor2.position)


def set_mode(m):
    global mode, auto_task, manual_state
    if m not in ("auto", "manual") or m == mode:
        return
    mode = m
    manual_state = "S"
    if m == "manual":
        if auto_task is not None:
            auto_task.cancel()
            auto_task = None
        halt_motors()
        log("MODE: MANUAL - arrow keys drive; LED solid = on, out = magnet")
    else:
        halt_motors()
        led.value = False
        log("MODE: AUTO - restarting from seek")
        auto_task = asyncio.create_task(autonomous())


async def drive_loop():
    # Keeps the targets just ahead of position while a key is held; stops on
    # release or deadman. Only touches motors in manual mode. The LED echoes
    # the hall sensor so you can hunt the magnet by hand.
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
            # LED as power indicator in manual: solid ON = robot alive,
            # goes OUT while the hall sits over a magnet (inverted echo)
            magnet = hall.value == MAGNET_DETECTED
            led.value = not magnet
            if magnet and not was_magnet:
                log("HALL: magnet under the sensor")
            was_magnet = magnet
        await asyncio.sleep(0.05)


PAGE = """<!DOCTYPE html>
<html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<title>UBISS robot</title><style>
 body{font-family:sans-serif;background:#111;color:#eee;text-align:center;
      user-select:none;-webkit-user-select:none;margin:0;padding:1em}
 #bar{margin:.5em}
 #toggle{font-size:18px;padding:.5em 1.5em;border:none;border-radius:10px;
         background:#a40;color:#fff}
 #toggle.manual{background:#2a7;color:#000}
 #pad{display:inline-grid;grid-template-columns:repeat(3,70px);grid-gap:6px;
      margin:.5em;opacity:.25}
 #pad.on{opacity:1}
 #pad button{font-size:24px;height:70px;border:none;border-radius:10px;
             background:#333;color:#eee}
 #pad button:active,#pad button.on{background:#2a7;color:#000}
 .blank{visibility:hidden}
 pre{background:#000;color:#9f9;font:13px/1.45 monospace;text-align:left;
     padding:.8em;border-radius:8px;max-height:50vh;overflow:auto}
</style></head><body>
<div id="bar"><button id="toggle">AUTO</button></div>
<div id="pad">
 <div class="blank"></div><button data-cmd="F">&#9650;</button><div class="blank"></div>
 <button data-cmd="L">&#9664;</button><button data-cmd="S">&#9209;</button>
 <button data-cmd="R">&#9654;</button>
 <div class="blank"></div><button data-cmd="B">&#9660;</button><div class="blank"></div>
</div>
<div style="color:#888;font-size:.85em">manual: hold arrow keys / WASD or the pad</div>
<pre id="log">connecting...</pre>
<script>
let mode='auto',active=null,timer=null;
const send=p=>fetch(p).catch(()=>{});
function ui(){
  const t=document.getElementById('toggle'),p=document.getElementById('pad');
  t.textContent=mode.toUpperCase();
  t.classList.toggle('manual',mode==='manual');
  p.classList.toggle('on',mode==='manual');
}
async function poll(){
  try{
    const t=await(await fetch('/log')).text();
    const nl=t.indexOf('\\n');
    mode=(t.slice(0,nl).split(' ')[1])||'auto';
    document.getElementById('log').textContent=t.slice(nl+1);
    ui();
  }catch(e){}
}
setInterval(poll,1000);poll();
document.getElementById('toggle').onclick=()=>
  send('/mode?m='+(mode==='auto'?'manual':'auto')).then(()=>setTimeout(poll,150));
function start(c){
  if(mode!=='manual'||active===c)return;
  active=c;send('/'+c);
  clearInterval(timer);timer=setInterval(()=>send('/'+c),250);
  document.querySelectorAll('#pad button').forEach(b=>
    b.classList.toggle('on',b.dataset.cmd===c));
}
function stop(){
  active=null;clearInterval(timer);send('/S');
  document.querySelectorAll('#pad button').forEach(b=>b.classList.remove('on'));
}
const KEYS={ArrowUp:'F',ArrowDown:'B',ArrowLeft:'L',ArrowRight:'R',
            w:'F',s:'B',a:'L',d:'R',W:'F',S:'B',A:'L',D:'R'};
addEventListener('keydown',e=>{const c=KEYS[e.key];if(!c)return;
  e.preventDefault();if(!e.repeat)start(c);});
addEventListener('keyup',e=>{const c=KEYS[e.key];if(!c)return;
  e.preventDefault();if(active===c)stop();});
document.querySelectorAll('#pad button').forEach(b=>{
  const c=b.dataset.cmd;
  b.addEventListener('pointerdown',e=>{e.preventDefault();
    c==='S'?stop():start(c);});
  b.addEventListener('pointerup',stop);
  b.addEventListener('pointerleave',()=>{if(active===c)stop();});
  b.addEventListener('pointercancel',stop);
});
</script></body></html>"""


def _http(content_type, body):
    if isinstance(body, str):
        body = body.encode("utf-8")
    head = ("HTTP/1.1 200 OK\r\nContent-Type: %s\r\nContent-Length: %d\r\n"
            "Connection: close\r\n\r\n" % (content_type, len(body)))
    return head.encode("utf-8") + body


async def _read_request_line(conn, timeout=1.0):
    buf = b""
    chunk = bytearray(256)
    t0 = time.monotonic()
    while b"\r\n" not in buf:
        if time.monotonic() - t0 > timeout:
            break
        try:
            n = conn.recv_into(chunk)
            if n == 0:
                break
            buf += bytes(chunk[:n])
        except OSError:
            await asyncio.sleep(0)
    return buf.split(b"\r\n", 1)[0].decode("utf-8") if buf else ""


async def _send_all(conn, data, timeout=1.0):
    view = memoryview(data)
    sent = 0
    t0 = time.monotonic()
    while sent < len(data):
        if time.monotonic() - t0 > timeout:
            break
        try:
            sent += conn.send(view[sent:])
        except OSError:
            await asyncio.sleep(0)


async def _handle(conn):
    global manual_state, last_cmd
    conn.setblocking(False)
    line = await _read_request_line(conn)       # "GET /F HTTP/1.1"
    if not line:
        return
    parts = line.split(" ")
    full = parts[1] if len(parts) > 1 else "/"
    path, _, query = full.partition("?")

    if path == "/" or path == "/index.html":
        await _send_all(conn, _http("text/html", PAGE))
    elif path == "/log":
        body = "MODE " + mode + "\n" + "\n".join(reversed(telemetry._lines))
        await _send_all(conn, _http("text/plain", body))
    elif path == "/mode":
        set_mode(query.partition("=")[2])
        await _send_all(conn, _http("text/plain", mode))
    else:
        cmd = path[1:].upper()
        if cmd in DIRECTIONS and mode == "manual":
            manual_state = cmd
            last_cmd = time.monotonic()
        await _send_all(conn, _http("text/plain", "ok"))


async def serve_ui():
    # Combined log + control server (replaces telemetry.serve - same port).
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
            await _handle(conn)
        except Exception as e:
            log("web request error:", e)
        finally:
            try:
                conn.close()
            except Exception:
                pass
# ================================================================


async def main():
    global DOCKING_ENABLED, auto_task
    asyncio.create_task(motor1.run())
    asyncio.create_task(motor2.run())
    if telemetry.start():
        asyncio.create_task(serve_ui())     # combined log + manual-control page
    asyncio.create_task(drive_loop())

    # Boot self-check: an unwired/mispolarized hall would read "docked" here
    # and freeze the robot at the start line. Detect that and fall back to a
    # pure homing run instead.
    if DOCKING_ENABLED and hall.value == MAGNET_DETECTED:
        log("WARNING: hall reads 'docked' at boot - check wiring / MAGNET_DETECTED.")
        log("Docking checks DISABLED for this run (pure light-follow).")
        DOCKING_ENABLED = False

    log("MODE: MANUAL at boot - robot waits. Switch to AUTO on the web page.")
    while True:
        await asyncio.sleep(1)          # mode switches happen via the web page


asyncio.run(main())
