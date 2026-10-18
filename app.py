import os, requests, urllib.parse, random
from flask import Flask, request, jsonify, render_template_string
app = Flask(__name__)
K = os.environ.get("GEMINI_API_KEY")
S = requests.Session()
H = """<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sam</title><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
<style>body{margin:0;font-family:sans-serif;background:#0f3d20;display:flex;flex-direction:column;min-height:100vh}
.h{background:#0a2e18;padding:12px;text-align:center;color:#a7f3d0;font-weight:bold}
#c{max-width:700px;width:95%;margin:10px auto;background:#fff;border-radius:20px;display:flex;flex-direction:column;height:85vh;overflow:hidden}
#m{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:12px}
.u{align-self:flex-end;background:#bbf7d0;padding:10px 14px;border-radius:18px;max-width:85%}
.i{align-self:flex-start;background:#14532d;color:#fff;padding:14px 16px;border-radius:18px;max-width:88%;line-height:1.5}
.i img{max-width:100%;border-radius:12px;margin-top:8px;display:block}
.b{display:flex;padding:10px;gap:6px;border-top:1px solid #eee;background:#f9fafb}
#q{flex:1;padding:12px 16px;border-radius:25px;border:1px solid #bbf7d0;outline:none}
button{border:none;border-radius:25px;padding:10px 12px;font-weight:bold;cursor:pointer}
.s{background:#14532d;color:#fff}</style></head><body>
<div class="h">🌿🙃😎 Soy Sam 👽</div><div id="c"><div id="m"><div class="i">Soy Sam 👽 Escribe "crea una imagen de un perro astronauta" 🖼️</div></div>
<div class="b"><button onclick="V()">🎤</button><button onclick="I()">🖼️</button><input id="q" placeholder="Escribe..." onkeypress="if(event.key==='Enter')E()"><button class="s" onclick="E()">Enviar</button></div></div>
<script>
let R=null;function V(){let SR=window.SpeechRecognition||window.webkitSpeechRecognition;if(!SR)return alert('Usa Chrome');if(!R){R=new SR();R.lang='es-ES';R.onresult=e=>{document.getElementById('q').value=e.results[0][0].transcript;E()}}try{R.start()}catch(e){}}
function I(){let p=prompt("¿Qué imagen?");if(p){document.getElementById('q').value="crea una imagen de "+p;E()}}
function KX(){if(window.renderMathInElement)renderMathInElement(document.body,{delimiters:[{left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false}]})}
async function E(){let i=document.getElementById('q'),t=i.value.trim();if(!t)return;let b=document.getElementById('m');b.innerHTML+=`<div class="u">${t}</div>`;i.value='';let d=document.createElement('div');d.className='i';d.innerText='⚡...';b.appendChild(d);b.scrollTop=b.scrollHeight;
try{let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:t})});let j=await r.json();d.innerHTML=marked.parse(j.reply);setTimeout(KX,100)}catch(e){d.innerText='Error, envia de nuevo'}b.scrollTop=b.scrollHeight}
</script></body></html>"""
@app.route('/')
def home(): return render_template_string(H)
@app.route('/chat', methods=['POST'])
def chat():
 try:
  m=request.get_json().get('message','Hola');l=m.lower()
  if any(x in l for x in ["crea una imagen","crea imagen","genera imagen","dibuja","haz una imagen","imagen de"]):
   p=m.lower()
   for x in ["crea una imagen","crea imagen","genera una imagen","genera imagen","dibuja","haz una imagen","imagen de","de"]: p=p.replace(x,"")
   p=p.strip() or "alien cute"
   url=f"https://image.pollinations.ai/prompt/{urllib.parse.quote(p)}?width=512&height=512&model=turbo&seed={random.randint(1,999999)}"
   return jsonify({"reply":f"Listo! 👽🖼️ **{p}**\n\n![imagen]({url})"})
  u=f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key={K}"
  pr=f"Eres Sam 👽 general. Si es formula usa $...$ y explica con manzanas. Max 150 palabras. Usuario: {m}"
  r=S.post(u, json={"contents":[{"parts":[{"text":pr}]}], "generationConfig":{"maxOutputTokens":350}}, timeout=15)
  t=r.json()['candidates'][0]['content']['parts'][0]['text']
  return jsonify({"reply":t})
 except: return jsonify({"reply":"Dale enviar de nuevo 🙏"}) 
