#!/usr/bin/env python3
# serial_exec.py - desktop-side: interrupt code.py over the serial REPL and
# exec a payload file on the board, streaming its prints to stdout.
#
# Leaves code.py STOPPED afterwards (board quiet, pins released) unless
# --reload is given, which soft-reboots: code.py AUTO-RUNS AND MOTORS MOVE.
#
#   .venv/bin/python robot/tools/serial_exec.py \
#       --code robot/tools/payload_hall_watch.py --prelude "DURATION=60"
import argparse
import sys
import time

import serial


def read_stream(ser, until=None, quiet_after=None, echo=True, max_s=600):
    buf = b""
    last = time.time()
    t0 = time.time()
    while time.time() - t0 < max_s:
        chunk = ser.read(4096)
        if chunk:
            last = time.time()
            buf += chunk
            if echo:
                sys.stdout.write(chunk.decode("utf-8", "replace"))
                sys.stdout.flush()
            if until is not None and until in buf:
                return buf
        elif quiet_after is not None and time.time() - last > quiet_after:
            return buf
    return buf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", default="/dev/cu.usbmodem1101")
    ap.add_argument("--code", required=True)
    ap.add_argument("--prelude", default="", help="python prepended to payload")
    ap.add_argument("--reload", action="store_true",
                    help="Ctrl-D afterwards: code.py reruns - ROBOT MAY MOVE")
    a = ap.parse_args()

    payload = b""
    if a.prelude:
        payload += a.prelude.encode() + b"\n"
    with open(a.code, "rb") as f:
        payload += f.read()

    ser = serial.Serial(a.port, 115200, timeout=0.1)
    try:
        # interrupt whatever runs, drain the backlog, get a clean >>> prompt
        ser.write(b"\x03")
        time.sleep(0.4)
        ser.write(b"\x03")
        time.sleep(0.4)
        ser.reset_input_buffer()
        ser.write(b"\r\n")
        got = read_stream(ser, until=b">>>", quiet_after=2.0, echo=False, max_s=8)
        if b">>>" not in got:
            sys.exit("no REPL prompt (is Thonny holding the port?)")

        ser.write(b"\x01")  # raw REPL
        got = read_stream(ser, until=b"raw REPL", quiet_after=1.5, echo=False, max_s=5)
        if b"raw REPL" in got:
            ser.write(payload)
            ser.write(b"\x04")
            read_stream(ser, until=b"OK", quiet_after=1.0, echo=False, max_s=5)
            read_stream(ser, until=b"\x04", quiet_after=None, echo=True)  # stdout
            err = read_stream(ser, until=b"\x04", quiet_after=1.0, echo=False, max_s=5)
            err = err.replace(b"\x04", b"").strip()
            if err:
                print("\n[board error]\n" + err.decode("utf-8", "replace"))
            ser.write(b"\x02")  # back to normal REPL
        else:
            # fallback: exec() one-liner at the normal REPL
            ser.write(b"\x02")
            time.sleep(0.3)
            ser.reset_input_buffer()
            line = "exec(" + repr(payload.decode()) + ")\r\n"
            ser.write(line.encode())
            read_stream(ser, until=b"DONE-SENTINEL-NEVER", quiet_after=3.0, echo=True)

        if a.reload:
            ser.write(b"\x04")
            print("\n[soft reload sent: code.py is running - robot may MOVE]")
        else:
            print("\n[board left at REPL: code.py stopped, robot quiet]")
    finally:
        ser.close()


main()
