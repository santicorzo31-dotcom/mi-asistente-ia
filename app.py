import os
from flask import Flask, request, jsonify, render_template_string
from google import genai
from google.genai import types

app = Flask(__name__)
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>🌿🙃😎 Soy Sam - tu super ayudante digital 👽</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
body{margin:0;font-family:-apple-system,sans-serif;background:#0f3d20;min-height:100vh;display:flex;flex-direction:column}
.header{background:#0a2e18;padding:15px;text-align:center} .header h1{margin:0;color:#a7f3d0;font-size:18px}
#chat{max-width:700px;width:95%;margin:15px auto;background:white;border-radius:20px;display:flex;flex-direction:column;overflow:hidden;height:80vh}
#messages{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:12px}
.msg{max-width:85%;padding:12px 16px;border-radius:18px;line-height:1.5}
.user{align-self:flex-end;background:#bbf7d0;color:#052e16}
.ia{align-self:flex-start;background:#14532d;color:white}
.input-area{display:flex;align-items:center;padding:10px;border-top:1px solid #eee;background:#f9fafb;gap:6px}
#msg{flex:1;padding:12px 16px;border:1px solid #bbf7d0;border-radius:25px;outline:none}
.btn{padding:12px 14px;border:none;border-radius:25px;font-weight:bold;cursor:pointer}
.mic{background:#e8f5e9;font-size:18px}
.send{background:#14532d;color:white}
.recording{background:#ff4444 !important;color:white;animation:pulse 1s infinite}
@keyframes pulse{0%{transform:scale(1)}50%{transform:scale(1.1)}100%{transform:scale(1)}}
</style></head><body>
<div class="header"><h1>🌿🙃😎 Soy Sam - tu super ayudante digital 👽</h1></div>
<div id="chat"><div id="messages"><div class="msg ia">Hola, ¿qué más? Soy Sam 👽 tu super ayudante digital 😎<br><br>¿Qué hacemos hoy? Tareas, cuentos, historia... tú dirás.</div></div>
<div class="input-area">
<button id="micBtn" class="btn mic" onclick="toggleVoice()">🎤</button>
<input id="msg" placeholder="Escribe o habla..." autofocus onkeypress="if(event.key==='Enter')send()">
<button class="btn send" onclick="send()">Enviar</button>
</div></div>
<script>
let recognition; let isRecording = false;
function toggleVoice(){
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if(!SR){ alert('Usa Chrome en el celular para voz'); return; }
  if(!recognition){
    recognition = new SR();
    recognition.lang = 'es-ES';
    recognition.onresult = function(e){ document.getElementById('msg').value = e.results[0][0].transcript; send(); };
    recognition.onend = function(){ isRecording=false; document.getElementById('micBtn').classList.remove('recording'); document.getElementById('micBtn').innerText='🎤'; };
  }
  if(isRecording){ recognition.stop(); } else { isRecording=true; document.getElementById('micBtn').classList.add('recording'); document.getElementById('micBtn').innerText='⏹️'; recognition.start(); }
}
async function send(){
 let input=document.getElementById('msg'); let text=input.value.trim(); if(!text) return;
 let box=document.getElementById('messages');
 box.innerHTML+=`<div class="msg user">${text}</div>`; input.value='';
 let tid='t'+Date.now(); box.innerHTML+=`<div id="${tid}" class="msg ia">⚡</div>`;
 box.scrollTop=box.scrollHeight;
 let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:text})});
 let d=await r.json(); document.getElementById(tid).remove();
 let div=document.createElement('div'); div.className='msg ia'; div.innerHTML=marked.parse(d.reply);
 box.appendChild(div); box.scrollTop=box.scrollHeight;
}
</script></body></html>"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_msg = request.get_json().get('message','Hola')
        prompt = f"Eres Sam, un super ayudante digital alienigena 👽, amigable, divertido y rapido. Responde corto. Pregunta: {user_msg}"
        resp = client.models.generate_content(
            model='gemini-flash-lite-latest',
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=400,
                temperature=0.8,
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            )
        )
        return jsonify({'reply': resp.text})
    except Exception as e:
        try:
            resp = client.models.generate_content(model='gemini-flash-latest', contents=user_msg)
            return jsonify({'reply': resp.text})
        except Exception as e2:
            return jsonify({'reply': f'Google está ocupado 5s, dale a enviar de nuevo 🙏'})

if __name__ == '__main__':
    app.run() 
