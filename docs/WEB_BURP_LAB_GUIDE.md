# NULLTRACE: Burp Suite Community / local synthetic HTTP lab

**Authorized scope:** only the local training process started by `python -m nulltrace --web-lab`. **No production accounts, passwords, personal data, external IP targets or third-party services.** This portal intentionally demonstrates an object-level authorization defect on fabricated records. Keep it on loopback; do not expose it to a LAN.

## Objectives

1. Observe a browser → server request and response.
2. Capture traffic with Burp Community's browser or correctly configured Proxy.
3. Use Repeater to resend a deliberately controlled request after changing a harmless query parameter.
4. Identify a missing server-side authorization check and propose an appropriate mitigation.
5. Distinguish evidence of a local HTTP exercise from proof that the Burp GUI was actually used.

## Procedure — Ubuntu

In the first terminal:

```bash
cd ~/Documents/nulltrace
source .venv/bin/activate
python -m nulltrace --web-lab
```

Expected example (your port differs):

```text
NULLTRACE LOCAL WEB LAB — synthetic training data ONLY
Open http://127.0.0.1:38751/ in the configured Burp browser.
For Burp Repeater, send GET /training/case?case=mirror with X-Nulltrace-Review: authorized
Server stays on loopback. Press Ctrl+C to stop.
```

Visit the printed `http://127.0.0.1:<port>/` using the browser integrated with Burp Suite Community or a browser configured to use its local HTTP proxy. Use the portal's `case=alpha` link. Inspect the request, choose **Send to Repeater**, change the URL query to `case=mirror`, and add this HTTP header:

```http
X-Nulltrace-Review: authorized
```

Send the modified request in Repeater. Expected demonstration: the server returns a fictional case named `mirror`, owned by `analyst-b`, although the initial synthetic request was for `alpha`, owned by `analyst-a`. This happens because the training server lacks a per-object authorization check. **The header here is a local exercise-completion marker, not real authentication.** Never treat it as a secure authorization method.

In another terminal (while the first server is running):

```bash
cd ~/Documents/nulltrace
source .venv/bin/activate
python -m nulltrace --lab web
```

Expected after the correct request:

```text
Behind the Browser / local HTTP: local-http (pass)
 - Loopback training request was received. Manual Burp usage is not independently verifiable.
```

Before the request, it should say `pending (failed)` with directions. After the request, open the game and complete the relevant Chapter 8 assessments. Press `Ctrl+C` in the first terminal to stop the web portal.

## Troubleshooting

| Symptom | Test | Action |
|---|---|---|
| Browser cannot connect | Check the terminal still shows `--web-lab` running and use **its actual port**. | Use `127.0.0.1`, not a guessed port; restart the server. |
| Burp sees no traffic | Try the browser supplied by Burp; verify proxy configuration. | The browser must use the proxy for loopback; browsers may bypass proxy for localhost by default. |
| Receipt remains pending | Repeat the modified request including both `case=mirror` and exact header. | Then rerun `python -m nulltrace --lab web`. |
| Burp not installed | Try inspecting the portal in an ordinary browser first. | This verifies the HTTP server, **not** Burp acceptance; the Burp exercise remains unverified. |
| Security concern | Confirm `127.0.0.1` in printed address. | Stop with `Ctrl+C` and report the issue; do not bind to all interfaces. |

## Evidence and ethics

Document initial and modified request URLs, key response fields, why the returned record violates the intended authorization model, impact limited to fictional sample data, and a recommended server-side access control check. Do not attach real session cookies or third-party personal information to reports. The lab's seven-day receipt is an educational convenience; it can be forged locally and must not be treated as cryptographic proof of professional competence.
