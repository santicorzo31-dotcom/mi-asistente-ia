import os
import requests
import urllib.parse
import random
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
API_KEY = os.environ.get("GEMINI_API_KEY")
sess = requests.Session()

HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SAM - tu ayudante</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#fafafb;min-height:100vh;display:flex;flex-direction:column}
.header{padding:14px;text-align:center;background:white;border-bottom:1px solid #eee;display:flex;align-items:center;justify-content:center;gap:10px;position:sticky;top:0;z-index:10}
.logo{width:32px;height:32px;border-radius:10px;background:linear-gradient(135deg,#111,#444);display:flex;align-items:center;justify-content:center;color:white;font-size:14px;font-weight:800}
.ht{font-weight:700;color:#111;font-size:15px}
#chat{max-width:750px;width:95%;margin:12px auto;background:white;border-radius:24px;box-shadow:0 4px 24px rgba(0,0,0,0.06);display:flex;flex-direction:column;height:86vh;overflow:hidden;border:1px solid #f0f0f0}
#m{flex:1;overflow-y:auto;padding:24px;display:flex;flex-direction:column;gap:18px}
.row{display:flex;gap:10px;max-width:92%}
.row.user{align-self:flex-end;flex-direction:row-reverse}
.row.ia{align-self:flex-start}
.avatar{width:28px;height:28px;border-radius:8px;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:bold}
.user .avatar{background:#111;color:white}
.ia .avatar{background:#111;color:white}
.bubble{padding:12px 16px;border-radius:18px;line-height:1.6;font-size:15px;word-wrap:break-word;white-space:pre-wrap}
.user .bubble{background:#111;color:white;font-weight:600;border-bottom-right-radius:6px}
.ia .bubble{background:#f6f6f8;color:#1a1a1a;border-bottom-left-radius:6px;border:1px solid #f0f0f0}
.ia .bubble img{max-width:100%;border-radius:12px;margin-top:10px;display:block}
.bar{display:flex;padding:12px;gap:8px;border-top:1px solid #f0f0f0;background:white;align-items:center}
#q{flex:1;padding:12px 16px;border-radius:24px;border:1px solid #e5e5e5;outline:none;background:#f6f6f8;font-size:15px}
#q:focus{background:white;border-color:#111}
.icon{width:40px;height:40px;border-radius:20px;border:none;background:#f6f6f8;cursor:pointer;font-size:18px}
.send{width:40px;height:40px;border-radius:20px;border:none;background:#111;color:white;cursor:pointer;font-size:18px;font-weight:bold}
.speak{margin-top:8px;background:#f0f0f0;border:none;color:#111;cursor:pointer;font-size:12px;font-weight:700;padding:6px 10px;border-radius:12px}
.hint{text-align:center;color:#999;font-size:11px;padding:6px}
</style></head><body>
<div class="header"><div class="logo">S</div><div class="ht">SAM • tu asistente inteligente</div></div>
<div id="chat">
<div id="m">
<div class="row ia"><div class="avatar">S</div><div class="bubble">Hola, soy <b>SAM</b>. Tu asistente inteligente.

Tu mensaje va en <b>negro bold</b> y el mío en cajita clara elegante, bien diferenciado.

Tengo audio 🔊, archivos 📎 e imágenes realistas 🖼️ tipo ChatGPT.

¿En qué te colaboro hoy?</div></div>
</div>
<div class="bar">
<button class="icon" onclick="document.getElementById('file').click()">📎</button>
<button class="icon" onclick="toggleMic()">🎤</button>
<button class="icon" onclick="imgPrompt()">🖼️</button>
<input type="file" id="file" hidden>
<input id="q" placeholder="Pregunta lo que sea..." autofocus onkeypress="if(event.key==='Enter')sendMsg()">
<button class="send" onclick="sendMsg()">↑</button>
</div>
<div class="hint">Escribe: "crea una imagen realista de..." para generar</div>
</div>
<script>
let recognition=null;
function toggleMic(){
 let SR=window.SpeechRecognition||window.webkitSpeechRecognition;
 if(!SR){ alert('Usa Chrome'); return; }
 if(!recognition){
  recognition=new SR(); recognition.lang='es-ES';
  recognition.onresult=e=>{document.getElementById('q').value=e.results[0][0].transcript; sendMsg();}
 }
 try{recognition.start()}catch(e){recognition.stop(); setTimeout(()=>recognition.start(),200);}
}
function imgPrompt(){
 let p=prompt('¿Qué imagen quieres? Ej: una mujer realista en la playa, estilo foto profesional');
 if(p){document.getElementById('q').value='crea una imagen realista de '+p; sendMsg();}
}
document.getElementById('file').addEventListener('change', function(){
 if(this.files[0]){let n=this.files[0].name; let q=prompt('¿Qué quieres que haga con '+n+'?'); document.getElementById('q').value='Archivo '+n+': '+(q||'analizalo'); sendMsg();}
});
function speakText(t){
 let clean=t.replace(/!\\[.*?\\]\\(.*?\\)/g,'').replace(/[#*_`]/g,'');
 let u=new SpeechSynthesisUtterance(clean);
 u.lang='es-ES'; u.rate=1;
 speechSynthesis.cancel();
 speechSynthesis.speak(u);
}
async function sendMsg(){
 let i=document.getElementById('q'), t=i.value.trim(); if(!t)return;
 let b=document.getElementById('m');
 b.innerHTML+=`<div class="row user"><div class="avatar">S</div><div class="bubble">${t}</div></div>`;
 i.value=''; b.scrollTop=b.scrollHeight;
 let d=document.createElement('div'); d.className='row ia';
 d.innerHTML=`<div class="avatar">S</div><div class="bubble">⚡ Pensando...</div>`;
 b.appendChild(d); b.scrollTop=b.scrollHeight;
 try{
  let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:t})});
  let j=await r.json();
  let html=marked.parse(j.reply);
  d.innerHTML=`<div class="avatar">S</div><div class="bubble">${html}<br><button class="speak" onclick="speakText(this.parentElement.innerText)">🔊 Escuchar</button></div>`;
 }catch(e){ d.innerHTML=`<div class="avatar">S</div><div class="bubble">Error, dale de nuevo 🙏</div>`; }
 b.scrollTop=b.scrollHeight;
}
</script></body></html>"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        msg = request.get_json().get('message', 'Hola')
        low = msg.lower()

        # IMAGENES REALISTAS ESTILO CHATGPT
        img_words = ["crea una imagen", "crea imagen", "genera una imagen", "genera imagen", "dibuja", "haz una imagen", "imagen de", "foto de", "creame una imagen", "realista"]
        if any(w in low for w in img_words):
            clean = msg
            for w in img_words:
                clean = clean.lower().replace(w, "")
            clean = clean.replace("de", "").strip()
            if len(clean) < 4:
                clean = "professional portrait photo"
            prompt_realista = f"{clean}, realistic photo, ultra detailed, natural light, 8k, photorealistic, sharp focus"
            safe = urllib.parse.quote(prompt_realista)
            img_url = f"https://image.pollinations.ai/prompt/{safe}?width=768&height=768&model=flux&seed={random.randint(1,999999)}&nologo=true&enhance=true"
            reply = f"Aquí tienes tu imagen realista de **{clean}** ✨\n\n![imagen]({img_url})\n\n¿Quieres otra versión? Dime cómo la quieres."
            return jsonify({"reply": reply})

        # CHAT NORMAL PROFESIONAL
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key={API_KEY}"
        system_prompt = f"""Eres SAM, asistente inteligente de Norte de Santander, Colombia. Profesional, amable, claro, útil. Hablas en español neutro colombiano, con un toquecito muy suave santandereano solo si encaja, sin exagerar. Nunca haces chistes sobre estatura.

Reglas:
- Responde útil, elegante, breve max 150 palabras.
- Profesional y directo.
- Si es fórmula matemática usa $...$ bonito.

Usuario dice: {msg}"""

        payload = {
            "contents": [{"parts": [{"text": system_prompt}]}],
            "generationConfig": {"maxOutputTokens": 400, "temperature": 0.7}
        }
        r = sess.post(url, json=payload, timeout=20)
        data = r.json()
        text = data['candidates'][0]['content']['parts'][0]['text']
        return jsonify({"reply": text})

    except Exception as e:
        print("Error:", e)
        return jsonify({"reply": "Se trabó un segundo, dale a enviar de nuevo 🙏"})

if __name__ == '__main__':
    app.run() 
