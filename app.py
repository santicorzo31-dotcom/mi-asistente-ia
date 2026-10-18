import os, requests
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
API_KEY = os.environ.get("GEMINI_API_KEY")
sess = requests.Session()

HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>🌿🙃😎 Soy Sam - tu super ayudante digital 👽</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
<style>
body{margin:0;font-family:-apple-system,sans-serif;background:#0f3d20;display:flex;flex-direction:column;min-height:100vh}
.header{background:#0a2e18;padding:12px;text-align:center;color:#a7f3d0;font-size:15px;font-weight:bold}
#chat{max-width:700px;width:95%;margin:10px auto;background:white;border-radius:20px;display:flex;flex-direction:column;height:85vh;overflow:hidden}
#messages{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:12px}
.user{align-self:flex-end;background:#bbf7d0;padding:10px 14px;border-radius:18px;max-width:85%}
.ia{align-self:flex-start;background:#14532d;color:white;padding:14px 16px;border-radius:18px;max-width:88%;line-height:1.6}
.bar{display:flex;padding:10px;gap:6px;border-top:1px solid #eee;background:#f9fafb;align-items:center}
#msg{flex:1;padding:12px 16px;border-radius:25px;border:1px solid #bbf7d0;outline:none}
button{border:none;border-radius:25px;padding:10px 14px;font-weight:bold;cursor:pointer}
.send{background:#14532d;color:white}
.mic{background:#e8f5e9;font-size:18px;transition:0.2s}
.mic.rec{background:#ff3b30;color:white;animation:pulse 1s infinite}
@keyframes pulse{0%{transform:scale(1)}50%{transform:scale(1.1)}100%{transform:scale(1)}}
</style></head><body>
<div class="header">🌿🙃😎 Soy Sam - tu super ayudante digital 👽</div>
<div id="chat"><div id="messages"><div class="ia">Soy Sam 👽 tu super ayudante para TODO: tareas, historia, cuentos, inglés, fórmulas... lo que necesites. Si es fórmula te la explico con manzanas 🍎</div></div>
<div class="bar">
<button id="micBtn" class="mic" onclick="toggleMic()">🎤</button>
<input id="msg" placeholder="Escribe o habla..." onkeypress="if(event.key==='Enter')send()">
<button class="send" onclick="send()">Enviar</button>
</div></div>
<script>
let recognition = null;
let isRecording = false;

function toggleMic(){
  let SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if(!SR){ alert('Tu celular no deja micro, usa Chrome y asegurate de estar en https'); return; }
  
  if(!recognition){
    recognition = new SR();
    recognition.lang = 'es-ES';
    recognition.interimResults = false;
    recognition.continuous = false;
    
    recognition.onstart = ()=>{
      isRecording = true;
      document.getElementById('micBtn').classList.add('rec');
      document.getElementById('micBtn').innerText = '⏹️';
    };
    recognition.onresult = (e)=>{
      let text = e.results[0][0].transcript;
      document.getElementById('msg').value = text;
      send();
    };
    recognition.onend = ()=>{
      isRecording = false;
      document.getElementById('micBtn').classList.remove('rec');
      document.getElementById('micBtn').innerText = '🎤';
    };
    recognition.onerror = (e)=>{
      console.log(e);
      isRecording = false;
      document.getElementById('micBtn').classList.remove('rec');
      document.getElementById('micBtn').innerText = '🎤';
      if(e.error == 'not-allowed') alert('Dale permiso al micro arriba en el candadito 🔒');
    };
  }

  if(isRecording){ recognition.stop(); }
  else { try{ recognition.start(); }catch(e){ recognition.stop(); } }
}

function renderMath(){
  if(window.renderMathInElement){
    renderMathInElement(document.body, {delimiters: [{left: '$$', right: '$$', display: true}, {left: '$', right: '$', display: false}]});
  }
}
async function send(){
  let i=document.getElementById('msg'), t=i.value.trim(); if(!t)return;
  let b=document.getElementById('messages'); b.innerHTML+=`<div class="user">${t}</div>`; i.value='';
  let d=document.createElement('div'); d.className='ia'; d.innerText='⚡ pensando...'; b.appendChild(d); b.scrollTop=b.scrollHeight;
  try{
    let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:t})});
    let j=await r.json();
    d.innerHTML = marked.parse(j.reply);
    setTimeout(renderMath, 150);
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
        # PROMPT GENERAL, NO SOLO FORMULAS
        prompt = f"""Eres Sam 👽, alias 🌿🙃😎 Soy Sam - tu super ayudante digital.
Eres un asistente GENERAL para todo: tareas del colegio, historia, ingles, ciencias, cuentos, chistes, consejos, programacion, de todo lo que te pida Santi.

Reglas:
1. Si es pregunta normal, responde normal, amigable y corto.
2. SOLO si es una formula matematica, ahi si explicala con manzanas, en 3 pasos separados y con ejemplo con numeros.
3. Si hay formula usa $...$ para que se vea bonita.
4. Nunca pegues palabras, escribe con espacios.
5. Responde max 150 palabras, facil de entender.

Usuario: {msg}"""
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": 400, "temperature": 0.7}
        }
        r = sess.post(url, json=payload, timeout=15)
        text = r.json()['candidates'][0]['content']['parts'][0]['text']
        return jsonify({"reply": text})
    except Exception as e:
        print(e)
        return jsonify({"reply": "Se trabo un seg, dale enviar de nuevo 🙏"})

if __name__ == '__main__':
    app.run() 
