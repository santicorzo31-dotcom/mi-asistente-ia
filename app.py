import os, requests, urllib.parse, random
from flask import Flask, request, jsonify, render_template_string
app = Flask(__name__)
K = os.environ.get("GEMINI_API_KEY")
S = requests.Session()
MODEL = "gemini-3.8-flash" # El que Google te pidió en la captura

H = """<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Sam Elegant</title><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
<style>
*{font-family:'Inter',sans-serif;box-sizing:border-box}
html,body{margin:0;padding:0;height:100%;overflow:hidden}
body{background:linear-gradient(135deg,#052e16,#0f172a);display:flex;flex-direction:column;height:100dvh;width:100vw}
.h{background:rgba(255,255,255,0.08);backdrop-filter:blur(20px);padding:14px;text-align:center;color:#ecfdf5;font-weight:600;letter-spacing:1px;border-bottom:1px solid rgba(255,255,255,0.1);flex-shrink:0}
#c{width:100%;max-width:750px;margin:0 auto;background:rgba(255,255,255,0.97);display:flex;flex-direction:column;flex:1;height:100%;overflow:hidden;border-radius:0}
@media(min-width:768px){#c{border-radius:28px;margin:10px auto;height:calc(100dvh - 20px)}}
#m{flex:1;overflow-y:auto;padding:24px;display:flex;flex-direction:column;gap:14px}
.u{align-self:flex-end;background:#14532d;color:white;padding:12px 16px;border-radius:20px 20px 4px 20px;max-width:80%;box-shadow:0 4px 12px rgba(0,0,0,0.1)}
.i{align-self:flex-start;background:#f8fafc;color:#0f172a;padding:16px 18px;border-radius:20px 20px 20px 4px;max-width:88%;line-height:1.6;border:1px solid #e2e8f0}
.i img{max-width:100%;border-radius:16px;margin-top:10px;box-shadow:0 8px 24px rgba(0,0,0,0.2)}
.b{display:flex;padding:12px 14px;padding-bottom:max(12px, env(safe-area-inset-bottom));gap:8px;border-top:1px solid #e2e8f0;background:white;align-items:center;flex-shrink:0}
#q{flex:1;padding:14px 18px;border-radius:30px;border:1.5px solid #bbf7d0;outline:none;background:#f8fafc}
#q:focus{border-color:#14532d;background:white}
.menu{position:relative}
.menu-btn{width:42px;height:42px;border-radius:50%;background:#f1f5f9;border:none;font-size:22px;cursor:pointer;display:flex;align-items:center;justify-content:center}
.dropdown{display:none;position:absolute;bottom:55px;left:0;background:white;border-radius:18px;box-shadow:0 10px 40px rgba(0,0,0,0.2);padding:8px;min-width:240px;z-index:20;border:1px solid #e2e8f0}
.dropdown.show{display:block}
.opt{display:flex;align-items:center;gap:12px;padding:12px 14px;border-radius:12px;cursor:pointer}
.opt:hover{background:#f0fdf4}
.s{width:46px;height:46px;border-radius:50%;background:#14532d;color:white;border:none;font-size:18px;cursor:pointer;box-shadow:0 4px 12px rgba(20,83,45,0.3)}
</style></head><body>
<div class="h">🌿 SAM • ELEGANT AI 👽</div>
<div id="c"><div id="m"><div class="i">Hola Santi 👽 Listo!<br><br>✨ Abre <b>⋮</b> para ver todo<br>📸 Fotos ultra rápidas<br>🖼️ Imágenes realistas 8K<br>🎤 Voz sin trabarse</div></div>
<div class="b">
<div class="menu">
<button class="menu-btn" onclick="toggleMenu()">⋮</button>
<div class="dropdown" id="dd">
<div class="opt" onclick="I();toggleMenu()">🖼️ Crear imagen realista</div>
<div class="opt" onclick="document.getElementById('cam').click();toggleMenu()">📷 Tomar foto / Escanear tarea</div>
<div class="opt" onclick="document.getElementById('file').click();toggleMenu()">📎 Subir archivo (PDF, etc)</div>
<div class="opt" onclick="V();toggleMenu()">🎤 Hablar con voz</div>
</div>
</div>
<input type="file" id="cam" accept="image/*" capture="environment" style="display:none" onchange="F(this,'image')">
<input type="file" id="file" accept=".pdf,.png,.jpg,.jpeg,.txt,.docx,.csv" style="display:none" onchange="F(this,'file')">
<input id="q" placeholder="Escribe algo..." onkeypress="if(event.key==='Enter')E()">
<button class="s" onclick="E()">➤</button>
</div></div>
<script>
let lastFile=null, lastType=null;
function toggleMenu(){document.getElementById('dd').classList.toggle('show')}
window.onclick=e=>{if(!e.target.closest('.menu')) document.getElementById('dd').classList.remove('show')}
function V(){let SR=window.SpeechRecognition||window.webkitSpeechRecognition;if(!SR)return alert('Usa Chrome');let rec=new SR();rec.lang='es-ES';rec.onresult=e=>{document.getElementById('q').value=e.results[0][0].transcript;E()};rec.start()}
function I(){let p=prompt("¿Qué imagen ultra realista quieres?");if(p){document.getElementById('q').value="crea una imagen de "+p;E()}}
function KX(){if(window.renderMathInElement)renderMathInElement(document.body,{delimiters:[{left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false}]})}
function F(input,kind){
 let file=input.files[0];if(!file)return;
 if(kind==='image'){
  let img=new Image(); img.onload=()=>{
   let c=document.createElement('canvas');let max=700;let w=img.width,h=img.height;
   if(w>h){if(w>max){h*=max/w;w=max}}else{if(h>max){w*=max/h;h=max}}
   c.width=w;c.height=h;c.getContext('2d').drawImage(img,0,0,w,h);
   lastFile=c.toDataURL('image/jpeg',0.6); lastType='image/jpeg';
   document.getElementById('m').innerHTML+=`<div class="u"><img src="${lastFile}" style="max-width:100%;border-radius:12px"><br>Analizando...</div>`;
   E(true);
  }; img.src=URL.createObjectURL(file);
 } else {
  let reader=new FileReader();
  reader.onload=e=>{
   lastFile=e.target.result; lastType=file.type||'application/pdf';
   document.getElementById('m').innerHTML+=`<div class="u">📄 ${file.name}<br>Analizando...</div>`;
   E(true);
  };
  reader.readAsDataURL(file);
 }
}
async function E(isFile=false){
 let i=document.getElementById('q'),t=i.value.trim();
 if(!t && !isFile)return; if(!t) t="Analiza este archivo";
 let b=document.getElementById('m'); if(!isFile) b.innerHTML+=`<div class="u">${t}</div>`;
 i.value=''; let d=document.createElement('div');d.className='i';d.innerText='⚡ Sam pensando...';b.appendChild(d);b.scrollTop=b.scrollHeight;
 try{
  let body={message:t}; if(lastFile){body.file=lastFile; body.mime=lastType; lastFile=null; lastType=null; document.getElementById('cam').value=''; document.getElementById('file').value='';}
  let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  let j=await r.json();d.innerHTML=marked.parse(j.reply);setTimeout(KX,100);
 }catch(e){d.innerText='Error, envia de nuevo'}b.scrollTop=b.scrollHeight
}
</script></body></html>"""

@app.route('/')
def home(): return render_template_string(H)

@app.route('/chat', methods=['POST'])
def chat():
 try:
  data=request.get_json()
  m=data.get('message','Hola'); file_data=data.get('file'); mime=data.get('mime','image/jpeg'); l=m.lower()

  if any(x in l for x in ["crea una imagen","crea imagen","genera imagen","dibuja","imagen de"]) and not file_data:
   p=m.lower()
   for x in ["crea una imagen","crea imagen","genera una imagen","genera imagen","dibuja","haz una imagen","imagen de","de","una","crea","genera"]: p=p.replace(x,"")
   p=p.strip() or "cute alien"
   realistic = f"{p}, photorealistic, ultra realistic, 8k, highly detailed, professional photography, cinematic lighting, sharp focus"
   url=f"https://image.pollinations.ai/prompt/{urllib.parse.quote(realistic)}?width=1024&height=1024&model=flux&enhance=true&seed={random.randint(1,999999)}"
   return jsonify({"reply":f"Listo Santi! 👽📸 **{p}**\n\n![imagen]({url})\n\n_Realista 8K flux_" })

  models = [MODEL, "gemini-3.8-flash", "gemini-2.5-flash", "gemini-flash-latest", "gemini-2.0-flash", "gemini-1.5-flash"]

  if file_data:
   b64=file_data.split(",")[1] if "," in file_data else file_data
   mtype = "image/jpeg"
   if "pdf" in mime.lower(): mtype="application/pdf"
   elif "png" in mime.lower(): mtype="image/png"
   for mod in models:
    try:
     url=f"https://generativelanguage.googleapis.com/v1beta/models/{mod}:generateContent?key={K}"
     payload={"contents":[{"parts":[{"text": f"Eres Sam elegante. Analiza. Usuario: {m}. Si es tarea resuelve paso a paso. Usa $...$ para formulas. Max 200 palabras."},{"inline_data":{"mime_type":mtype,"data":b64}}]}],"generationConfig":{"maxOutputTokens":600}}
     r=S.post(url, json=payload, timeout=30)
     jr=r.json()
     if 'candidates' in jr:
      return jsonify({"reply": jr['candidates'][0]['content']['parts'][0]['text']})
    except: continue
   return jsonify({"reply": f"Error modelos: {str(jr)[:300]}"})

  for mod in models:
   try:
    url=f"https://generativelanguage.googleapis.com/v1beta/models/{mod}:generateContent?key={K}"
    r=S.post(url, json={"contents":[{"parts":[{"text":f"Eres Sam elegante 👽 Max 200 palabras. Usuario: {m}"}]}],"generationConfig":{"maxOutputTokens":400}}, timeout=15)
    jr=r.json()
    if 'candidates' in jr:
     return jsonify({"reply": jr['candidates'][0]['content']['parts'][0]['text']})
   except: continue

  return jsonify({"reply":"Error API key"})
 except Exception as e:
  return jsonify({"reply": f"Error: {str(e)}"}) 
