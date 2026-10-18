import os, requests, urllib.parse, random
from flask import Flask, request, jsonify, render_template_string
app = Flask(__name__)

K = os.environ.get("GEMINI_API_KEY", "")
S = requests.Session()

HTML = """<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Sam</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
*{box-sizing:border-box;font-family:sans-serif}
html,body{margin:0;padding:0;height:100%;overflow:hidden}
body{background:#052e16;display:flex;flex-direction:column;height:100dvh}
.h{background:#0a2e18;padding:12px;text-align:center;color:#a7f3d0;font-weight:bold;flex-shrink:0}
#c{width:100%;max-width:750px;margin:0 auto;background:#fff;display:flex;flex-direction:column;flex:1;height:100%;overflow:hidden}
@media(min-width:768px){#c{margin:10px auto;border-radius:20px;height:calc(100dvh - 20px)}}
#m{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:12px}
.u{align-self:flex-end;background:#bbf7d0;padding:10px 14px;border-radius:18px;max-width:80%}
.i{align-self:flex-start;background:#14532d;color:#fff;padding:14px;border-radius:18px;max-width:88%;line-height:1.5}
.i img{max-width:100%;border-radius:12px;margin-top:8px}
.b{display:flex;padding:12px;gap:8px;border-top:1px solid #eee;background:#fff;align-items:center;flex-shrink:0}
#q{flex:1;padding:12px 16px;border-radius:25px;border:1px solid #bbf7d0;outline:none}
.menu{position:relative}
.menu-btn{width:42px;height:42px;border-radius:50%;background:#f1f5f9;border:none;font-size:20px}
.dropdown{display:none;position:absolute;bottom:50px;left:0;background:white;border-radius:12px;box-shadow:0 10px 30px rgba(0,0,0,.2);padding:6px;min-width:220px;z-index:10}
.dropdown.show{display:block}
.opt{padding:10px;border-radius:8px;cursor:pointer}
.opt:hover{background:#f0fdf4}
.s{width:44px;height:44px;border-radius:50%;background:#14532d;color:white;border:none}
</style></head><body>
<div class="h">🌿 SAM 👽</div>
<div id="c"><div id="m"><div class="i">Hola Santi! Ya estoy arreglado 👽<br>Abre ⋮ para fotos e imágenes</div></div>
<div class="b">
<div class="menu"><button class="menu-btn" onclick="document.getElementById('dd').classList.toggle('show')">⋮</button>
<div class="dropdown" id="dd">
<div class="opt" onclick="askImg()">🖼️ Crear imagen realista</div>
<div class="opt" onclick="document.getElementById('cam').click()">📷 Tomar foto</div>
<div class="opt" onclick="doVoice()">🎤 Voz</div>
</div></div>
<input type="file" id="cam" accept="image/*" capture="environment" style="display:none" onchange="compress(this)">
<input id="q" placeholder="Escribe..." onkeypress="if(event.key==='Enter')send()">
<button class="s" onclick="send()">➤</button>
</div></div>
<script>
let lastImg=null;
function askImg(){let p=prompt("¿Qué imagen?");if(p){document.getElementById('q').value="crea una imagen de "+p;send()}}
function doVoice(){let SR=window.SpeechRecognition||window.webkitSpeechRecognition;if(!SR)return alert('Usa Chrome');let r=new SR();r.lang='es-ES';r.onresult=e=>{document.getElementById('q').value=e.results[0][0].transcript;send()};r.start()}
function compress(inp){
 let f=inp.files[0];if(!f)return;
 let img=new Image();img.onload=()=>{
  let c=document.createElement('canvas');let max=700,w=img.width,h=img.height;
  if(w>h){if(w>max){h*=max/w;w=max}}else{if(h>max){w*=max/h;h=max}}
  c.width=w;c.height=h;c.getContext('2d').drawImage(img,0,0,w,h);
  lastImg=c.toDataURL('image/jpeg',0.6);
  document.getElementById('m').innerHTML+=`<div class="u"><img src="${lastImg}"></div>`;
  send(true);
 };img.src=URL.createObjectURL(f);
}
async function send(isPhoto=false){
 let q=document.getElementById('q'),t=q.value.trim();
 if(!t && !isPhoto)return; if(!t)t="Que ves en la foto?";
 let m=document.getElementById('m');
 if(!isPhoto)m.innerHTML+=`<div class="u">${t}</div>`;
 q.value='';let d=document.createElement('div');d.className='i';d.innerText='⚡...';m.appendChild(d);m.scrollTop=m.scrollHeight;
 try{
  let body={message:t};if(lastImg){body.image=lastImg;lastImg=null}
  let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  let j=await r.json();d.innerHTML=marked.parse(j.reply);
 }catch(e){d.innerText='Error, reintenta'}m.scrollTop=m.scrollHeight
}
</script></body></html>"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json(force=True)
        msg = data.get('message','Hola')
        img = data.get('image')
        l = msg.lower()

        # 1. IMAGEN REALISTA - Pollinations flux
        if any(x in l for x in ["crea una imagen","crea imagen","genera imagen","imagen de","dibuja"]) and not img:
            p = msg
            for x in ["crea una imagen","crea imagen","genera una imagen","genera imagen","imagen de","dibuja","haz una imagen"]:
                p = p.lower().replace(x,"")
            p = p.strip() or "alien cute"
            prompt = f"{p}, photorealistic, 8k, ultra detailed, cinematic lighting"
            url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=1024&height=1024&model=flux&seed={random.randint(1,999999)}"
            return jsonify({"reply": f"Listo! 👽 **{p}**\n\n![foto]({url})"})

        # 2. ANALIZAR FOTO - modelos que SI existen
        if img:
            b64 = img.split(",")[1] if "," in img else img
            # Usamos gemini-1.5-flash que si funciona en v1
            for model in ["gemini-1.5-flash","gemini-2.0-flash","gemini-flash-latest"]:
                for version in ["v1beta","v1"]:
                    try:
                        u = f"https://generativelanguage.googleapis.com/{version}/models/{model}:generateContent?key={K}"
                        payload = {"contents":[{"parts":[{"text":f"Eres Sam. Analiza foto. Usuario: {msg}. Max 150 palabras."},{"inline_data":{"mime_type":"image/jpeg","data":b64}}]}]}
                        r = S.post(u, json=payload, timeout=20)
                        j = r.json()
                        if 'candidates' in j:
                            return jsonify({"reply": j['candidates'][0]['content']['parts'][0]['text']})
                    except:
                        continue
            return jsonify({"reply": "No pude leer la foto, reintenta 🙏"})

        # 3. TEXTO
        if not K:
            return jsonify({"reply":"Falta GEMINI_API_KEY en Vercel > Settings > Environment Variables"})

        for model in ["gemini-1.5-flash","gemini-2.0-flash","gemini-flash-latest"]:
            for version in ["v1beta","v1"]:
                try:
                    u = f"https://generativelanguage.googleapis.com/{version}/models/{model}:generateContent?key={K}"
                    r = S.post(u, json={"contents":[{"parts":[{"text":msg}]}]}, timeout=15)
                    j = r.json()
                    if 'candidates' in j:
                        return jsonify({"reply": j['candidates'][0]['content']['parts'][0]['text']})
                except:
                    continue
        
        return jsonify({"reply": "Error de API, revisa tu key"})

    except Exception as e:
        return jsonify({"reply": f"Error interno: {str(e)[:200]}"})

# Para Vercel
if __name__ == '__main__':
    app.run() 
