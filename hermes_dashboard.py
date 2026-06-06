#!/usr/bin/env python3
"""
Hermes Dashboard — Standalone Server
Run: python3 hermes_dashboard.py
Then open: http://localhost:8080

Login: admin / hermes2026
"""
import json, os, re, subprocess, sqlite3, shlex
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime

PORT = 8081
GATEWAY_HOST = "YOUR_GATEWAY_IP"  # e.g. 192.168.1.170
HERMES_NUMBER = "YOUR_HERMES_NUMBER"  # Target WhatsApp number
SSH_USER = "YOUR_SSH_USER"  # SSH username on gateway
AGENT_LOG = "/root/.hermes/logs/agent.log"
STATE_DB = "/root/.hermes/state.db"
AUTH = ("YOUR_USERNAME", "YOUR_PASSWORD")

HTML = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Hermes Dashboard</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#0f0f23;--bg2:#1a1a35;--card:#25254a;--accent:#667eea;--accent2:#764ba2;--border:#2a2a50;--text:#e8e8f0;--text2:#8888aa;--green:#00d68f;--red:#ff6b6b;--radius:14px;--radius-sm:10px}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:var(--bg);color:var(--text);height:100vh;overflow:hidden}
.login-wrap{display:flex;align-items:center;justify-content:center;height:100vh;background:radial-gradient(ellipse at top,var(--bg2) 0%,var(--bg) 70%)}
.login-box{background:var(--bg2);border:1px solid var(--border);border-radius:20px;padding:48px 40px;width:100%;max-width:360px;text-align:center}
.login-logo{font-size:48px;margin-bottom:8px}.login-title{font-size:20px;font-weight:700}.login-sub{color:var(--text2);font-size:12px;margin-bottom:28px}
.fld{margin-bottom:14px;text-align:left}.fld label{display:block;font-size:10px;font-weight:700;color:var(--text2);margin-bottom:6px;text-transform:uppercase}
.fld input{width:100%;padding:11px 14px;background:var(--bg);border:1.5px solid var(--border);border-radius:10px;color:var(--text);font-size:14px;outline:none}
.fld input:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(108,92,231,.15)}
.btn-pri{width:100%;padding:13px;background:var(--accent);color:#fff;border:none;border-radius:10px;font-size:14px;font-weight:600;cursor:pointer}
.btn-pri:hover:not(:disabled){background:var(--accent2);transform:translateY(-1px)}
.btn-pri:disabled{opacity:.45;cursor:not-allowed}.login-err{color:var(--red);font-size:12px;margin-top:10px;min-height:18px}
.app{display:none;flex-direction:column;height:100vh}.app.on{display:flex}
.topbar{background:var(--bg2);border-bottom:1px solid var(--border);padding:10px 20px;display:flex;align-items:center;gap:12px;flex-shrink:0}
.topbar-logo{font-size:26px}.topbar-actions{display:flex;gap:6px;margin-left:auto}
.topbar-btn{background:none;border:1.5px solid var(--border);color:var(--text2);padding:5px 10px;border-radius:10px;font-size:11px;cursor:pointer;display:flex;align-items:center;gap:5px}
.topbar-btn:hover{border-color:var(--accent);color:var(--accent)}
.chat-area{flex:1;display:flex;flex-direction:column;overflow:hidden;min-height:0}
.chat-msgs{flex:1;overflow-y:auto;padding:20px 16px;display:flex;flex-direction:column;gap:6px;background:var(--bg)}
.chat-msgs::-webkit-scrollbar{width:5px}
.chat-msgs::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px}
.date-divider{text-align:center;margin:14px 0 10px;display:flex;align-items:center;gap:12px}
.date-divider::before,.date-divider::after{content:'';flex:1;height:1px;background:var(--border)}
.date-divider span{font-size:11px;color:var(--text2);padding:0 8px;background:var(--bg)}
.msg-row{display:flex;flex-direction:column;max-width:82%;animation:fadeIn .2s}
@keyframes fadeIn{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}
.msg-row.hermes{align-self:flex-start}
.msg-row.user{align-self:flex-end}.msg-row.user .bubble{background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff;border-radius:16px 4px 16px 16px}
.msg-row.hermes .bubble{background:var(--card);color:var(--text);border-radius:4px 16px 16px 16px}
.bubble{padding:10px 14px;font-size:14px;line-height:1.45;white-space:pre-wrap;word-break:break-word}
.msg-meta{font-size:10px;color:var(--text2);padding:3px 4px 0;display:flex;align-items:center;gap:6px}
.msg-row.user .msg-meta{justify-content:flex-end}
.model-badge,.from-badge{font-size:9px;background:rgba(255,255,255,.06);padding:1px 6px;border-radius:6px;opacity:.7}
.chat-empty{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;color:var(--text2);font-size:13px}
.chat-empty-icon{font-size:42px;opacity:.35}
.compose{display:flex;gap:10px;padding:12px 16px 16px;background:var(--bg2);border-top:1px solid var(--border);align-items:flex-end}
.compose textarea{flex:1;resize:none;padding:12px 16px;background:var(--bg);border:1.5px solid var(--border);border-radius:16px;color:var(--text);font-size:14px;outline:none;max-height:120px;line-height:1.4;font-family:inherit}
.compose textarea:focus{border-color:var(--accent)}
.compose button{width:44px;height:44px;border-radius:50%;background:var(--accent);border:none;color:#fff;font-size:20px;cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.toast{position:fixed;bottom:90px;left:50%;transform:translateX(-50%) translateY(20px);background:var(--card);border:1px solid var(--border);border-radius:24px;padding:10px 20px;font-size:13px;color:var(--text);opacity:0;transition:all .3s;pointer-events:none;z-index:999}
.toast.on{opacity:1;transform:translateX(-50%) translateY(0)}.toast.ok{border-color:var(--green);color:var(--green)}.toast.fail{border-color:var(--red);color:var(--red)}
@media(max-width:600px){.msg-row{max-width:90%}.topbar{padding:8px 12px;gap:8px}.chat-msgs{padding:14px 10px}.compose{padding:8px 10px 12px}}
</style></head><body>
<div class="login-wrap" id="loginWrap">
  <div class="login-box">
    <div class="login-logo">🦐</div>
    <div class="login-title">Hermes Agent</div>
    <div class="login-sub">Chat Interface</div>
    <div class="fld"><label>Username</label><input type="text" id="inUser" placeholder="admin" autocomplete="username"></div>
    <div class="fld"><label>Password</label><input type="password" id="inPass" placeholder="••••••••" autocomplete="current-password" onkeydown="if(event.key==='Enter')doLogin()"></div>
    <button class="btn-pri" id="btnLogin" onclick="doLogin()">Sign In</button>
    <div class="login-err" id="loginErr"></div>
  </div>
</div>
<div class="app" id="app">
  <div class="topbar">
    <div class="topbar-logo">🦐</div>
    <div style="flex:1"><div style="font-size:15px;font-weight:700">Hermes</div></div>
    <div class="topbar-actions">
      <button class="topbar-btn" onclick="doAction('force_send')" title="Force Send">📡 Send</button>
      <button class="topbar-btn" onclick="doAction('restart')" title="Restart">🔄 Restart</button>
      <button class="topbar-btn" onclick="toggleLogs()" title="Logs">📋 Logs</button>
      <button class="topbar-btn" onclick="doLogout()" title="Logout">🚪</button>
    </div>
  </div>
  <div class="chat-area">
    <div class="chat-msgs" id="chatMsgs"><div class="chat-empty"><div class="chat-empty-icon">🦐</div><div>Loading...</div></div></div>
    <div class="compose"><textarea id="composeInput" rows="1" placeholder="Message Hermes..." onkeydown="composeKey(event)" oninput="this.style.height='auto';this.style.height=Math.min(this.scrollHeight,120)+'px'"></textarea><button id="sendBtn" onclick="sendMessage()">➤</button></div>
  </div>
</div>
<div class="toast" id="toast"></div>
<div class="log-drawer" id="logDrawer" style="display:none;position:fixed;bottom:0;left:0;right:0;max-height:50vh;background:var(--bg2);border-top:2px solid var(--border);z-index:100;overflow-y:auto;padding:16px;font-family:monospace;font-size:11px;color:var(--text2);white-space:pre-wrap"><div style="display:flex;justify-content:space-between;margin-bottom:10px"><b>📋 Logs</b><button class="topbar-btn" onclick="document.getElementById('logDrawer').style.display='none';document.getElementById('logOverlay').style.display='none'">✕</button></div><pre id="logContent" style="margin:0">Loading...</pre></div>
<div id="logOverlay" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:99" onclick="document.getElementById('logDrawer').style.display='none';this.style.display='none'"></div>
<script>
var API='',auth={};
function b64(s){return btoa(s)}
function api(a,ok,fail){var x=new XMLHttpRequest();x.open('GET',API+'api/'+a,true);x.setRequestHeader('Authorization','Basic '+b64(auth.user+':'+auth.pass));x.onload=function(){if(x.status===401){doLogout();return}try{ok(JSON.parse(x.responseText))}catch(e){if(fail)fail(x.responseText);else ok({})}};x.onerror=function(){if(fail)fail('Network error')};x.send()}
function apiq(a,ok,fail){var x=new XMLHttpRequest();x.open('GET',API+'api/'+a,true);x.setRequestHeader('Authorization','Basic '+b64(auth.user+':'+auth.pass));x.onload=function(){try{ok(JSON.parse(x.responseText))}catch(e){if(fail)fail()}};x.onerror=function(){if(fail)fail()};x.send()}
function esc(s){if(!s)return '';return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;')}
function doLogin(){var u=document.getElementById('inUser').value.trim(),p=document.getElementById('inPass').value,b=document.getElementById('btnLogin');if(!u||!p){document.getElementById('loginErr').textContent='Enter username and password.';return}b.disabled=true;b.textContent='Signing in...';auth={user:u,pass:p};api('ping',function(){document.getElementById('loginWrap').style.display='none';document.getElementById('app').classList.add('on');refreshStatus();loadChatHistory();startChatRefresh();startStatusRefresh()},function(){b.disabled=false;b.textContent='Sign In';document.getElementById('loginErr').textContent='Invalid credentials.'})}
function doLogout(){stopChatRefresh();stopStatusRefresh();auth={};document.getElementById('app').classList.remove('on');document.getElementById('loginWrap').style.display='flex';document.getElementById('inPass').value=''}
function doAction(a){var btn=event&&event.target?event.target:null;if(btn)btn.disabled=true;api(a,function(d){showToast(d.status||'Done!','ok');if(btn)btn.disabled=false;if(a==='force_send'||a==='restart')setTimeout(loadChatHistory,3000)},function(e){showToast('Failed','fail');if(btn)btn.disabled=false})}
function toggleLogs(){var d=document.getElementById('logDrawer'),o=document.getElementById('logOverlay');if(d.style.display==='none'){d.style.display='block';o.style.display='block';document.getElementById('logContent').textContent='Loading...';api('logs',function(r){document.getElementById('logContent').textContent=r.logs||r.output||'No logs.'})}else{d.style.display='none';o.style.display='none'}}
var chatTimer,statusTimer;
function renderChat(msgs,model){var el=document.getElementById('chatMsgs');if(!msgs||!msgs.length){if(!el.querySelector('.chat-empty')){el.innerHTML='<div class=\"chat-empty\"><div class=\"chat-empty-icon\">🦐</div><div>No messages yet.</div></div>'}return}var h='',ld='';msgs.forEach(function(m){var ts=m.timestamp?new Date(m.timestamp):new Date();if(isNaN(ts.getTime()))ts=new Date();var ds=ts.toLocaleDateString('en-GB',{day:'numeric',month:'short',year:'numeric'});if(ds!==ld){h+='<div class=\"date-divider\"><span>'+ds+'</span></div>';ld=ds}var tm=ts.toLocaleTimeString('en-GB',{hour:'2-digit',minute:'2-digit'});var plat=esc(m.platform||'WA'),send=esc(m.sender||'?'),modl=esc(model||'?');if(m.role==='assistant'){h+='<div class=\"msg-row hermes\"><div class=\"bubble hermes\">'+esc(m.body||'')+'</div><div class=\"msg-meta\">'+tm+' <span class=\"model-badge\">['+plat+'] ['+send+'] '+modl+'</span></div></div>'}else{h+='<div class=\"msg-row user\"><div class=\"bubble user\">'+esc(m.body||'')+'</div><div class=\"msg-meta\">'+tm+' <span class=\"from-badge\">['+plat+'] ['+send+']</span></div></div>'}});el.innerHTML=h;el.scrollTop=el.scrollHeight}
function loadChatHistory(){apiq('chat_history',function(d){renderChat(d.messages||[],d.model||'?')})}
function composeKey(e){if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();sendMessage()}}
function sendMessage(){var inp=document.getElementById('composeInput'),body=inp.value.trim();if(!body)return;inp.value='';inp.style.height='auto';var btn=document.getElementById('sendBtn');btn.disabled=true;var id='p_'+Date.now(),el=document.getElementById('chatMsgs');var empty=el.querySelector('.chat-empty');if(empty)empty.remove();el.innerHTML+='<div class=\"msg-row user\" id=\"'+id+'\"><div class=\"bubble user\" style=\"opacity:.7\">'+esc(body)+'</div><div class=\"msg-meta\">Sending...</div></div>';el.scrollTop=el.scrollHeight;var x=new XMLHttpRequest();x.open('POST',API+'api/chat_send',true);x.setRequestHeader('Authorization','Basic '+b64(auth.user+':'+auth.pass));x.setRequestHeader('Content-Type','application/x-www-form-urlencoded');x.onload=function(){btn.disabled=false;var row=document.getElementById(id);if(!row)return;var meta=row.querySelector('.msg-meta');if(x.status===200){try{var d=JSON.parse(x.responseText)}catch(e){}if(d.ok||d.status==='sent'){meta.textContent=new Date().toLocaleTimeString('en-GB',{hour:'2-digit',minute:'2-digit'});row.querySelector('.bubble').style.opacity='1';showToast('Sent!','ok');setTimeout(loadChatHistory,2000)}else{meta.textContent='Failed';row.querySelector('.bubble').style.background='var(--red)';showToast(d.error||'Failed','fail')}}else{meta.textContent='Failed';row.querySelector('.bubble').style.background='var(--red)';showToast('Failed','fail')}};x.onerror=function(){btn.disabled=false;var row=document.getElementById(id);if(row){row.querySelector('.msg-meta').textContent='Failed';row.querySelector('.bubble').style.background='var(--red)'}showToast('Network error','fail')};x.timeout=60000;x.send('body='+encodeURIComponent(body))}
function showToast(msg,t){var e=document.getElementById('toast');e.textContent=msg;e.className='toast on '+(t||'');setTimeout(function(){e.className='toast'},3000)}
function refreshStatus(){api('status',function(d){})}
function startChatRefresh(){chatTimer=setInterval(loadChatHistory,15000)}
function stopChatRefresh(){if(chatTimer){clearInterval(chatTimer)}}
function startStatusRefresh(){statusTimer=setInterval(refreshStatus,30000)}
function stopStatusRefresh(){if(statusTimer){clearInterval(statusTimer)}}
</script></body></html>"""

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *a):
        pass
    def send_cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Authorization, Content-Type')
    def check_auth(self):
        h = self.headers.get('Authorization', '')
        if not h.startswith('Basic '):
            return False
        try:
            import base64
            d = base64.b64decode(h[6:]).decode()
            u, p = d.split(':', 1)
            return u == AUTH[0] and p == AUTH[1]
        except:
            return False
    def send_json(self, data, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_cors()
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_cors()
        self.end_headers()
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')
        if path.startswith('/api') and not self.check_auth():
            self.send_json({"error": "Unauthorized"}, 401)
            return
        path = parsed.path.rstrip('/')
        q = parse_qs(parsed.query)
        
        if path == '/api/ping':
            self.send_json({"pong": True})
        elif path == '/api/status':
            try:
                r = subprocess.run(["ps", "aux"], capture_output=True, text=True, timeout=5)
                running = "hermes_monitor" in r.stdout
            except:
                running = False
            self.send_json({"running": running, "status": "running" if running else "stopped"})
        elif path == '/api/chat_history':
            msgs = []
            model = "?"
            # Try state.db first
            if os.path.exists(STATE_DB):
                try:
                    conn = sqlite3.connect(STATE_DB)
                    c = conn.cursor()
                    c.execute("SELECT model FROM sessions WHERE model IS NOT NULL ORDER BY started_at DESC LIMIT 1")
                    row = c.fetchone()
                    if row and row[0]: model = row[0]
                    c.execute("SELECT role, content, timestamp FROM messages WHERE role IN ('user','assistant') AND content IS NOT NULL AND length(content)>0 ORDER BY timestamp DESC LIMIT 50")
                    for row in c.fetchall():
                        role, content, ts = row
                        ts_str = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S") if ts else "?"
                        body = content[:500] + "..." if len(content) > 500 else content
                        sender = "Wilson Fung" if role == "user" else "Hermes"
                        msgs.append({"role": role, "sender": sender, "platform": "WhatsApp", "body": body, "timestamp": ts_str})
                    conn.close()
                except:
                    pass
            # Fallback to log
            if not msgs and os.path.exists(AGENT_LOG):
                with open(AGENT_LOG) as f:
                    for line in f.readlines()[-200:]:
                        if "inbound message:" in line:
                            m = re.search(r"msg='(.+?)'", line)
                            if m:
                                body = m.group(1)[:500]
                                msgs.append({"role": "user", "sender": "Wilson Fung", "platform": "WhatsApp", "body": body, "timestamp": line[:19]})
                        elif "Sending response (" in line:
                            msgs.append({"role": "assistant", "sender": "Hermes", "platform": "WhatsApp", "body": "[response sent]", "timestamp": line[:19]})
            msgs.reverse()
            self.send_json({"messages": msgs, "total": len(msgs), "model": model, "target": HERMES_NUMBER})
        elif path == '/api/chat_send':
            body = q.get("text", [""])[0]
            if not body:
                self.send_json({"error": "No text"})
                return
            try:
                safe = body.replace("'", "'\\''")
                r = subprocess.run(
                    ["ssh", "-o", "StrictHostKeyChecking=no",
                     "SSH_USER@" + GATEWAY_HOST + "",
                     "openclaw", "message", "send", "--channel", "whatsapp",
                     "--target", HERMES_NUMBER, "--message", body],
                    capture_output=True, text=True, timeout=60)
                self.send_json({"status": "sent" if r.returncode == 0 else "error", "output": (r.stdout.strip() or r.stderr.strip())[:200]})
            except Exception as e:
                self.send_json({"error": str(e)})
        elif path == '/api/force_send':
            try:
                r = subprocess.run(
                    ["ssh", "-o", "StrictHostKeyChecking=no",
                     "SSH_USER@" + GATEWAY_HOST + "",
                     "cd /root/.openclaw/workspace && /root/.openclaw/workspace/vibe_env/bin/python /root/.openclaw/workspace/scripts/hermes_monitor.py 2>&1"],
                    capture_output=True, text=True, timeout=120)
                self.send_json({"status": "done", "output": r.stdout[:500]})
            except Exception as e:
                self.send_json({"error": str(e)})
        elif path == '/api/restart':
            try:
                subprocess.run(
                    ["ssh", "-o", "StrictHostKeyChecking=no",
                     "SSH_USER@" + GATEWAY_HOST + "",
                     "pkill -f hermes_monitor 2>/dev/null; nohup /root/.openclaw/workspace/vibe_env/bin/python /root/.openclaw/workspace/scripts/hermes_monitor.py > /tmp/hermes_monitor.log 2>&1 &"],
                    capture_output=True, text=True, timeout=30)
                self.send_json({"status": "restarted"})
            except Exception as e:
                self.send_json({"error": str(e)})
        elif path == '/api/logs':
            logs = ""
            try:
                r = subprocess.run(
                    ["ssh", "-o", "StrictHostKeyChecking=no",
                     "SSH_USER@" + GATEWAY_HOST + "",
                     "cat /tmp/hermes_monitor.log 2>/dev/null; echo '---'; cat /tmp/financial_report.log 2>/dev/null"],
                    capture_output=True, text=True, timeout=30)
                logs = r.stdout[-2000:]
            except:
                logs = "Failed to fetch logs"
            self.send_json({"logs": logs})
        else:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_cors()
            self.end_headers()
            self.wfile.write(HTML.encode('utf-8'))
    
    def do_POST(self):
        if not self.check_auth():
            self.send_json({"error": "Unauthorized"}, 401)
            return
        parsed = urlparse(self.path)
        if parsed.path == '/api/chat_send':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode() if length > 0 else ""
            import urllib.parse
            params = urllib.parse.parse_qs(body)
            msg = params.get('body', [''])[0]
            if not msg:
                self.send_json({"error": "No body"})
                return
            try:
                r = subprocess.run(
                    ["ssh", "-o", "StrictHostKeyChecking=no",
                     "SSH_USER@" + GATEWAY_HOST + "",
                     "openclaw", "message", "send", "--channel", "whatsapp",
                     "--target", HERMES_NUMBER, "--message", msg],
                    capture_output=True, text=True, timeout=60)
                self.send_json({"status": "sent" if r.returncode == 0 else "error", "output": (r.stdout.strip() or r.stderr.strip())[:200]})
            except Exception as e:
                self.send_json({"error": str(e)})
        else:
            self.send_json({"error": "Not found"}, 404)

if __name__ == '__main__':
    print(f"🦐 Hermes Dashboard running on http://0.0.0.0:{PORT}")
    print(f"   Login: {AUTH[0]} / {AUTH[1]}")
    HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
