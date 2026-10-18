import os, requests, urllib.parse, random
from flask import Flask, request, jsonify, render_template_string
app = Flask(__name__)
K = os.environ.get("GEMINI_API_KEY")
S = requests.Session()

H = """<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SAM</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
body{margin:0;font-family:sans-serif;background:#fafafb;min-height:100vh;display:flex;flex-direction:column}
.header{padding:14px;background:white;border-bottom:1px solid #eee;display:flex;align-items:center;justify-content:center;gap:10px}
.logo{width:32px;height:32px;border-radius:10px;background:#111;color:white;display:flex;align-items:center;justify-content:center;font-weight:800}
#chat{max-width:750px;width:95%;margin:12px auto;background:white;border-radius:24px;box-shadow:0 4px 24px rgba(0,0,0,.06);display:flex;flex-direction:column;height:86vh;overflow:hidden;border:1px solid #f0f0f0}
#m{flex:1;overflow-y:auto;padding:24px;display:flex;flex-direction:column;gap:18px}
.row{display:flex;gap:10px;max-width:92%}
.row.user{align-self:flex-end;flex-direction:row-reverse}
.row.ia{align-self:flex-start}
.avatar{width:28px;height:28px;border-radius:8px;background:#111;color:white;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:bold;flex-shrink:0}
.bubble{padding:12px 16px;border-radius:18px;line-height:1.6;font-size:15px;word-wrap:break-word}
.user .bubble{background:#111;color:white;font-weight:600;border-bottom-right-radius:6px}
.ia .bubble{background:#f6f6f8;color:#1a1a1a;border-bottom-left-radius:6px;border:1px solid #f0f0f0}
.ia .bubble img{max-width:100%;border-radius:12px;margin-top:10px;display:block}
.bar{display:flex;padding:12px;gap:8px;border-top:1px solid #f0f0f0;background:white;align-items:center}
#q{flex:1;padding:12px 16px;border-radius:24px;border:1px solid #e5e5e5;outline:none;background:#f6f6f8}
.icon{width:40px;height:40px;border-radius:20px;border:none;background:#f6f6f8;cursor:pointer;font-size:18px}
.send{width:40px;height:40px;border-radius:20px;border:none;background:#111;color:white;cursor:pointer;font-size:18px}
.speak{margin-top:8px;background:#f0f0f0;border:none;color:#111;cursor:pointer;font-size:12px;font-weight:700;padding:6px 10px;border-radius:12px}
</style></head><body>
<div class="header"><div class="logo">S</div><div style="font-weight:700">SAM - tu asistente</div></div>
<div id="chat"><div id="m"><div class="row ia"><div class="avatar">S</div><div class="bubble">Hola, soy <b>SAM</b>. Ahora ya muestro formulas bonitas, imagenes realistas y todo elegante. Preguntame!</div></div></div>
<div class="bar">
<button class="icon" onclick="document.getElementById('file').click()">📎</button>
<button class="icon" onclick="mic()">🎤</button>
<button class="icon" onclick="img()">🖼️</button>
<input type="file" id="file" hidden>
<input id="q" placeholder="Pregunta lo que sea..." autofocus onkeypress="if(event.key==='Enter')send()">
<button class="send" onclick="send()">↑</button>
</div>
<div style="text-align:center;color:#999;font-size:11px;padding:6px">Escribe: "crea una imagen realista de..." para generar</div>
</div>
<script>
let R=null;
function mic(){let SR=window.SpeechRecognition||window.webkitSpeechRecognition;if(!SR)return alert('Usa Chrome');if(!R){R=new SR();R.lang='es-ES';R.onresult=e=>{document.getElementById('q').value=e.results[0][0].transcript;send()}}try{R.start()}catch(e){}}
function img(){let p=prompt('Que imagen quieres? Ej: mujer realista en la playa');if(p){document.getElementById('q').value='crea una imagen realista de '+p;send()}}
document.getElementById('file').addEventListener('change',function(){if(this.files[0]){let n=this.files[0].name;let q=prompt('Que hacer con '+n+'?');document.getElementById('q').value='Archivo '+n+': '+(q||'analizalo');send()}})
function speak(t){let u=new SpeechSynthesisUtterance(t);u.lang='es-ES';speechSynthesis.cancel();speechSynthesis.speak(u)}
async function send(){let i=document.getElementById('q'),t=i.value.trim();if(!t)return;let b=document.getElementById('m');b.innerHTML+=`<div class="row user"><div class="avatar">S</div><div class="bubble">${t}</div></div>`;i.value='';b.scrollTop=b.scrollHeight;let d=document.createElement('div');d.className='row ia';d.innerHTML=`<div class="avatar">S</div><div class="bubble">Pensando...</div>`;b.appendChild(d);b.scrollTop=b.scrollHeight;try{let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:t})});let j=await r.json();d.innerHTML=`<div class="avatar">S</div><div class="bubble">${marked.parse(j.reply)}<br><button class="speak" onclick="speak(this.parentElement.innerText)">Escuchar</button></div>`;renderMathInElement(d,{delimiters:[{left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false}]}); }catch(e){d.innerHTML=`<div class="avatar">S</div><div class="bubble">Error, dale de nuevo</div>`}b.scrollTop=b.scrollHeight}
</script></body></html>"""

@app.route('/')
def home(): return render_template_string(H)

@app.route('/chat', methods=['POST'])
def chat():
 try:
  m=request.get_json().get('message','Hola')
  low=m.lower()
  if any(w in low for w in ["crea una imagen","crea imagen","genera","dibuja","imagen de","foto de","realista"]):
    clean=m
    for w in ["crea una imagen","crea imagen","genera una imagen","genera imagen","dibuja","haz una imagen","imagen de","foto de","creame una imagen","realista","de"]:
      clean=clean.lower().replace(w,"")
    clean=clean.strip()
    if len(clean)<3: clean="professional photo"
    safe=urllib.parse.quote(f"{clean}, realistic photo, 8k, photorealistic")
    url=f"https://image.pollinations.ai/prompt/{safe}?width=768&height=768&model=flux&seed={random.randint(1,999999)}&nologo=true"
    return jsonify({"reply": f"Aqui tienes tu imagen realista de **{clean}** \n\n![imagen]({url})\n\nQuieres otra?"})
  url=f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key={K}"
  prompt=f"Eres SAM, asistente profesional colombiano, breve max 150 palabras, usa $ para formulas inline y $$ para grandes. Usuario: {m}"
  r=S.post(url, json={"contents":[{"parts":[{"text":prompt}]}], "generationConfig":{"maxOutputTokens":500}}, timeout=20)
  txt=r.json()['candidates'][0]['content']['parts'][0]['text']
  return jsonify({"reply":txt})
 except Exception as e:
  print(e)
  return jsonify({"reply":"Se trabo un segundo, dale enviar de nuevo"})

if __name__ == '__main__':
    app.run()
