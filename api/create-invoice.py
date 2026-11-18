"""Axten Pro - Telegram Stars invoice backend (Vercel serverless, Python).

Stateless: only creates a Stars invoice link. The Telegram Mini App opens the
link with Telegram.WebApp.openInvoice and activates Pro when the callback
reports "paid". No webhook, no stored state.

Env:
  TELEGRAM_BOT_TOKEN - @Axten_Bot token (set as a Vercel env var, never in code)
"""
import json
import os
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TG_API = "https://api.telegram.org/bot" + BOT_TOKEN


def tg_call(method, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        TG_API + "/" + method, data=data, method="POST",
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode())


class handler(BaseHTTPRequestHandler):
    def _send(self, status, obj):
        body = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        self._send(200, {"ok": True, "service": "axten-stars-backend"})

    def do_POST(self):
        if not BOT_TOKEN:
            self._send(500, {"ok": False, "error": "payment server not configured"})
            return
        try:
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(length) if length else b"{}"
            body = json.loads(raw.decode() or "{}")
        except Exception:
            body = {}
        # Donation: body {"kind": "donation", "amount": <stars>} - any 1..10000.
        # Default (no kind / kind "pro"): Axten Pro, fixed 100 Stars.
        import time, secrets
        kind = (body.get("kind") or "pro") if isinstance(body, dict) else "pro"
        if kind == "donation":
            try:
                amount = int(body.get("amount"))
            except Exception:
                amount = 0
            if amount < 1 or amount > 10000:
                self._send(400, {"ok": False, "error": "amount must be 1..10000 Stars"})
                return
            title = "Donasi Axten"
            desc = "Donasi sukarela buat dukung pengembangan Axten. Terima kasih!"
            label = "Donasi Axten"
            prefix = "axten-donation-"
        else:
            amount = 100
            title = "Axten Pro"
            desc = "Axten Pro - sekali bayar, aktif selamanya di perangkat ini. Tema aksen custom, badge PRO, Insight Lanjutan, dompet tanpa batas."
            label = "Axten Pro"
            prefix = "axten-pro-"
        # Unique payload per invoice so each purchase is distinguishable.
        payload = prefix + str(int(time.time())) + "-" + secrets.token_hex(4)
        try:
            res = tg_call("createInvoiceLink", {
                "title": title,
                "description": desc,
                "payload": payload,
                "currency": "XTR",
                "prices": [{"label": label, "amount": amount}],
            })
        except urllib.error.HTTPError as e:
            detail = e.read().decode()[:300]
            self._send(502, {"ok": False, "error": "telegram api error", "detail": detail})
            return
        except Exception as e:
            self._send(502, {"ok": False, "error": str(e)[:200]})
            return
        if not res.get("ok"):
            self._send(502, {"ok": False, "error": "telegram api error", "detail": str(res)[:300]})
            return
        self._send(200, {"ok": True, "invoice_link": res.get("result"), "payload": payload})

    def log_message(self, *args):
        pass
