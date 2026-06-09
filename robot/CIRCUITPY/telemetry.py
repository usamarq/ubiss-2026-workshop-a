# telemetry.py - live logs over the robot's own WiFi.
# The robot becomes a WiFi access point and serves a tiny auto-refreshing
# log page. Join the robot's network on your PC/phone and open:
#     http://192.168.4.1/
# log(...) behaves like print(...) but also appears on that page.
# SSID/password come from settings.toml (AP_SSID / AP_PASSWORD); if no valid
# password is set, the network is open.
# Designed to NEVER crash the robot: all network errors are swallowed.

import os
import asyncio

try:
    import wifi
    import socketpool
except ImportError:
    wifi = None

_lines = []
_MAX_LINES = 50
_pool = None


def log(*args):
    s = " ".join(str(a) for a in args)
    print(s)
    _lines.append(s)
    if len(_lines) > _MAX_LINES:
        _lines.pop(0)


def start():
    # Start the access point. Returns True if the log server can run.
    global _pool
    if wifi is None:
        print("TELEMETRY: no wifi module on this board")
        return False
    try:
        ssid = os.getenv("AP_SSID") or "UBISS-Robot"
        pwd = os.getenv("AP_PASSWORD")
        if pwd and len(pwd) >= 8:
            wifi.radio.start_ap(ssid=ssid, password=pwd)
            kind = "(password in settings.toml)"
        else:
            wifi.radio.start_ap(ssid=ssid)
            kind = "(OPEN network)"
        _pool = socketpool.SocketPool(wifi.radio)
        log("TELEMETRY: join WiFi '%s' %s then open http://%s/"
            % (ssid, kind, wifi.radio.ipv4_address_ap))
        return True
    except Exception as e:
        print("TELEMETRY: wifi failed:", e)
        return False


def _page():
    body = ("<html><head><meta http-equiv='refresh' content='1'>"
            "<title>robot log</title>"
            "<style>body{background:#111;color:#9f9;font:14px/1.5 monospace;"
            "padding:1em}</style></head><body>"
            "<b>ROBOT LOG</b> (newest first, refreshes every second)<pre>"
            + "\n".join(reversed(_lines))
            + "</pre></body></html>")
    head = ("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n"
            "Connection: close\r\nContent-Length: %d\r\n\r\n" % len(body))
    return (head + body).encode()


async def serve():
    # Tiny HTTP server task. Run with: asyncio.create_task(telemetry.serve())
    if _pool is None:
        return
    srv = _pool.socket(_pool.AF_INET, _pool.SOCK_STREAM)
    try:
        srv.setsockopt(_pool.SOL_SOCKET, _pool.SO_REUSEADDR, 1)
    except Exception:
        pass
    srv.bind(("0.0.0.0", 80))
    srv.listen(2)
    srv.setblocking(False)
    req = bytearray(512)
    while True:
        try:
            client, _addr = srv.accept()
        except OSError:
            await asyncio.sleep(0.1)      # nobody connecting right now
            continue
        try:
            client.settimeout(0.5)
            try:
                client.recv_into(req)     # read & discard the request
            except OSError:
                pass
            data = _page()
            mv = memoryview(data)
            sent = 0
            while sent < len(data):
                n = client.send(mv[sent:])
                if not n:
                    break
                sent += n
        except Exception:
            pass
        try:
            client.close()
        except Exception:
            pass
        await asyncio.sleep(0)
