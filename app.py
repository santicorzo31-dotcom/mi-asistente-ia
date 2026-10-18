import os, requests
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

API_KEY = os.environ.get("GEMINI_API_KEY")
# Conexión siempre abierta, esto es lo que te ahorra 5 segundos
sess = requests.Session()

HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>🌿🙃😎 Soy Sam - tu super ayudante digital 👽</title>
<style>
body{margin:0;font-family:sans-serif;background:#0f3d20;display:flex;flex-direction:column;min-height:100vh}
.header{background:#0a2e18;padding:15px;text-align:center;color:#a7f3d0;font-size:17px;font-weight:bold}
#chat{max-width:700px;width:95%;margin:15px auto;background:white;border-radius:20px;display:flex;flex-direction:column;height:80vh;overflow:hidden}
#messages{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:10px}
.user{align-self:flex-end;background:#bbf7d0;padding:10px 14px;border-radius:18px}
.ia{align-self:flex-start;background:#14532d;color:white;padding:10px 14px;border-radius:18px}
.bar{display:flex;padding:10px;gap:6px;border-top:1px solid #eee}
#msg{flex:1;padding:12px;border-radius:20px;border:1px solid #ccc;outline:none}
button{border:none;border-radius:20px;padding:10px 14px;font-weight:bold;cursor:pointer}
.send{background:#14532d;color:white}
</style></head><body>
<div class="header">🌿🙃😎 Soy Sam - tu super ayudante digital 👽</div>
<div id="chat"><div id="messages"><div class="ia">Soy Sam 👽 modo rápido ⚡ Dime.</div></div>
<div class="bar">
<button onclick="voice()">🎤</button>
<input id="msg" placeholder="Escribe..." onkeypress="if(event.key==='Enter')send()">
<button class="send" onclick="send()">Enviar</button>
</div></div>
<script>
let rec;
function voice(){
  let SR=window.SpeechRecognition||window.webkitSpeechRecognition;
  if(!SR)return alert('Usa Chrome');
  rec=new SR(); rec.lang='es-ES'; rec.onresult=e=>{document.getElementById('msg').value=e.results[0][0].transcript; send();}; rec.start();
}
async function send(){
  let i=document.getElementById('msg'), t=i.value.trim(); if(!t)return;
  let b=document.getElementById('messages'); b.innerHTML+=`<div class="user">${t}</div>`; i.value='';
  let d=document.createElement('div'); d.className='ia'; d.innerText='⚡...'; b.appendChild(d); b.scrollTop=b.scrollHeight;
  try{
    let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:t})});
    let j=await r.json(); d.innerText=j.reply;
  }catch(e){ d.innerText='Error, dale enviar de nuevo'; }
  b.scrollTop=b.scrollHeight;
}
</script></body></html>"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        msg = request.get_json().get('message','Hola')
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key={API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": f"Responde corto: {msg}"}]}],
            "generationConfig": {"maxOutputTokens": 200, "temperature": 0.6}
        }
        r = sess.post(url, json=payload, timeout=10)
        data = r.json()
        text = data['candidates'][0]['content']['parts'][0]['text']
        return jsonify({"reply": text})
    except Exception as e:
        return jsonify({"reply": "Se demoró 1 seg, dale enviar de nuevo 🙏"})

if __name__ == '__main__':
    app.run() 
