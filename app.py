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
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,sans-serif;background:#fafafb;min-height:100vh;display:flex;flex-direction:column}
.header{padding:14px;background:white;border-bottom:1px solid #eee;display:flex;align-items:center;justify-content:center;gap:10px}
.logo{width:32px;height:32px;border-radius:10px;background:#111;color:white;display:flex;align-items:center;justify-content:center;font-weight:800}
#chat{max-width:750px;width:95%;margin:12px auto;background:white;border-radius:24px;box-shadow:0 4px 24px rgba(0,0,0,.06);display:flex;flex-direction:column;height:86vh;overflow:hidden;border:1px solid #f0f0f0;position:relative}
#m{flex:1;overflow-y:auto;padding:24px;display:flex;flex-direction:column;gap:18px}
.row{display:flex;gap:10px;max-width:92%}
.row.user{align-self:flex-end;flex-direction:row-reverse}
.row.ia{align-self:flex-start}
.avatar{width:28px;height:28px;border-radius:8px;background:#111;color:white;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:bold;flex-shrink:0}
.bubble{padding:12px 16px;border-radius:18px;line-height:1.6;font-size:15px;word-wrap:break-word}
.user .bubble{background:#111;color:white;font-weight:600;border-bottom-right-radius:6px}
.ia .bubble{background:#f6f6f8;color:#1a1a1a;border-bottom-left-radius:6px;border:1px solid #f0f0f0}
.ia .bubble img{max-width:100%;border-radius:12px;margin-top:10px;display:block}
.bar{display:flex;padding:12px;gap:8px;border-top:1px solid #f0f0f0;background:white;align-items:center;position:relative}
#q{flex:1;padding:12px 16px;border-radius:24px;border:1px solid #e5e5e5;outline:none;background:#f6f6f8;font-size:15px}
.icon{width:40px;height:40px;border-radius:20px;border:none;background:#f6f6f8;cursor:pointer;font-size:18px;display:flex;align-items:center;justify-content:center}
.send{width:40px;height:40px;border-radius:20px;border:none;background:#111;color:white;cursor:pointer;font-size:18px}
.menu{position:absolute;bottom:70px;left:12px;background:white;border:1px solid #eee;border-radius:16px;box-shadow:0 8px 24px rgba(0,0,0,.12);padding:8px;display:none;flex-direction:column;gap:4px;z-index:20;min-width:190px}
.menu.show{display:flex}
.menu button{border:none;background:white;text-align:left;padding:12px;border-radius:10px;cursor:pointer;font-size:14px;display:flex;gap:10px;align-items:center}
.menu button:hover{background:#f6f6f8}
.speak{margin-top:8px;background:#f0f0f0;border:none;color:#111;cursor:pointer;font-size:12px;font-weight:700;padding:6px 10px;border-radius:12px}
</style></head><body>
<div class="header"><div class="logo">S</div><div style="font-weight:700">SAM</div></div>
<div id="chat">
<div id="m"><div class="row ia"><div class="avatar">S</div><div class="bubble">Hola, soy SAM. Ahora con fotos super realistas y menu elegante.</div></div></div>

<div class="menu" id="menu">
<button onclick="openFile()">📎 Subir archivo</button>
<button onclick="openCamera()"></button>
<button onclick="createImg()">🖼️ Crear imagen realista</button>
<button onclick="closeMenu()">✖ Cerrar</button>
</div>

<div class="bar">
<button class="icon" onclick="toggleMenu()">⋮</button>
<button class="icon" onclick="mic()">🎤</button>
<input type="file" id="file" hidden>
<input type="file" id="camera" accept="image/*" capture="environment" hidden>
<input id="q" placeholder="Pregunta lo que sea..." autofocus onkeypress="if(event.key==='Enter')send()">
<button class="send" onclick="send()">↑</button>
</div>
<div style="text-align:center;color:#999;font-size:11px;padding:6px">Menu ⋮ para archivos y fotos</div>
</div>
<script>
let R=null;
function toggleMenu(){document.getElementById('menu').classList.toggle('show')}
function closeMenu(){document.getElementById('menu').classList.remove('show')}
function openFile(){closeMenu();document.getElementById('file').click()}
function openCamera(){closeMenu();document.getElementById('camera').click()}
function createImg(){closeMenu();let p=prompt('Que imagen quieres? Ej: mujer colombiana en la playa con vestido blanco, foto profesional');if(p){document.getElementById('q').value='crea una imagen realista de '+p;send()}}
function mic(){let SR=window.SpeechRecognition||window.webkitSpeechRecognition;if(!SR)return alert('Usa Chrome en el celular');if(!R){R=new SR();R.lang='es-ES';R.onresult=e=>{document.getElementById('q').value=e.results[0][0].transcript;send()}}try{R.start()}catch(e){}}
document.getElementById('file').addEventListener('change',function(){if(this.files[0]){let n=this.files[0].name;let q=prompt('Que hacer con '+n+'?');document.getElementById('q').value='Archivo '+n+': '+(q||'analizalo');send()}})
document.getElementById('camera').addEventListener('change',function(){if(this.files[0]){let n=this.files[0].name||'foto.jpg';let q=prompt('Que ves en esta foto?');document.getElementById('q').value='[Foto tomada: '+n+'] '+(q||'que hay aqui?');send()}})
function speak(t){let u=new SpeechSynthesisUtterance(t);u.lang='es-ES';speechSynthesis.cancel();speechSynthesis.speak(u)}
async function send(){let i=document.getElementById('q'),t=i.value.trim();if(!t)return;let b=document.getElementById('m');b.innerHTML+=`<div class="row user"><div class="avatar">S</div><div class="bubble">${t}</div></div>`;i.value='';b.scrollTop=b.scrollHeight;let d=document.createElement('div');d.className='row ia';d.innerHTML=`<div class="avatar">S</div><div class="bubble">Pensando...</div>`;b.appendChild(d);b.scrollTop=b.scrollHeight;try{let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:t})});let j=await r.json();d.innerHTML=`<div class="avatar">S</div><div class="bubble">${marked.parse(j.reply)}<br><button class="speak" onclick="speak(this.parentElement.innerText)">🔊 Escuchar</button></div>`;renderMathInElement(d,{delimiters:[{left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false}]}); }catch(e){d.innerHTML=`<div class="avatar">S</div><div class="bubble">Error, dale de nuevo</div>`}b.scrollTop=b.scrollHeight}
</script></body></html>"""

@app.route('/')
def home(): return render_template_string(H)

@app.route('/chat', methods=['POST'])
def chat():
 try:
  m=request.get_json().get('message','Hola')
  low=m.lower()
  if any(w in low for w in ["crea una imagen","crea imagen","genera","dibuja","imagen de","foto de"]):
    clean=m.lower()
    for w in ["crea una imagen","crea imagen","genera una imagen","genera imagen","dibuja","haz una imagen","imagen de","foto de","creame una imagen","realista","de","por favor","porfa"]:
      clean=clean.replace(w,"")
    clean=clean.strip()
    if len(clean)<3: clean="colombian woman at beach"
    # MEJOR REALISMO - FOTO TIPO DSLR
    prompt_real = f"{clean}, beautiful woman wearing elegant summer dress, photorealistic, ultra realistic skin texture, natural lighting, DSLR photo, 85mm lens, sharp focus, highly detailed, beach background realistic, 8k"
    safe=urllib.parse.quote(prompt_real)
    # Usamos flux con enhance para mas realismo
    url=f"https://image.pollinations.ai/prompt/{safe}?width=1024&height=1024&model=flux&seed={random.randint(1,9999999)}&enhance=true&nologo=true"
    return jsonify({"reply": f"Aqui tienes tu foto super realista de **{clean}** 📸\n\n![foto real]({url})\n\nQuedo mas realista ahora? Si quieres otro estilo dime."})
  
  url=f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key={K}"
  prompt=f"Eres SAM, asistente profesional, breve max 150 palabras, usa $ para formulas. Usuario: {m}"
  r=S.post(url, json={"contents":[{"parts":[{"text":prompt}]}], "generationConfig":{"maxOutputTokens":500}}, timeout=20)
  txt=r.json()['candidates'][0]['content']['parts'][0]['text']
  return jsonify({"reply":txt})
 except Exception as e:
  print(e)
  return jsonify({"reply":"Se trabo, dale de nuevo"})

if __name__ == '__main__':
    app.run() 
