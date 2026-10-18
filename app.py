from flask import Flask, request, jsonify, render_template_string
import os, requests, urllib.parse, random, time

app = Flask(__name__)

HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SAM</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600&display=swap" rel="stylesheet">
<style>
*{font-family:'Outfit',sans-serif;box-sizing:border-box}
body{margin:0;background:linear-gradient(135deg,#052e16,#14532d);height:100dvh;display:flex;justify-content:center;align-items:center}
#app{width:100%;max-width:480px;height:100dvh;background:#f8fafc;display:flex;flex-direction:column;box-shadow:0 20px 60px rgba(0,0,0,.4);overflow:hidden}
@media(min-width:600px){#app{height:92dvh;border-radius:24px}}
.h{background:linear-gradient(90deg,#052e16,#14532d);color:#bbf7d0;padding:14px 20px;display:flex;align-items:center;justify-content:space-between}
.h b{font-size:20px;letter-spacing:1px}
#m{flex:1;overflow-y:auto;padding:18px;display:flex;flex-direction:column;gap:12px;background:#f1f5f9}
.u{align-self:flex-end;background:#fff;color:#052e16;padding:12px 16px;border-radius:18px 18px 4px 18px;max-width:82%;box-shadow:0 2px 8px rgba(0,0,0,.08);font-weight:500}
.i{align-self:flex-start;background:#14532d;color:#ecfdf5;padding:14px 16px;border-radius:18px 18px 18px 4px;max-width:88%;line-height:1.5;box-shadow:0 4px 12px rgba(0,0,0,.15)}
.i img{width:100%;border-radius:14px;margin-top:10px;display:block}
.i a{color:#bbf7d0}
.b{display:flex;align-items:center;gap:8px;padding:12px;background:#fff;border-top:1px solid #e2e8f0}
#q{flex:1;padding:12px 16px;border-radius:24px;border:1px solid #cbd5e1;outline:none;font-size:15px}
#q:focus{border-color:#14532d}
.icon{width:40px;height:40px;border-radius:50%;border:none;cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:18px;transition:.2s}
.icon:active{transform:scale(.9)}
.mic{background:#fef3c7}
.cam{background:#e0f2fe}
.img{background:#fce7f3}
.send{background:#14532d;color:#fff;width:44px;height:44px}
.typing{opacity:.7;font-style:italic}
</style></head><body>
<div id="app">
<div class="h"><b>🌿 SAM 👽</b><span style="font-size:12px;opacity:.7">elegant v2</span></div>
<div id="m"><div class="i">Hola Santi, ya quedé elegante y rápido 🙏✨<br><br>Ya tengo:<br>🎤 micrófono para hablar<br>📷 cámara<br>🖼️ imágenes ultra realistas<br>⚡ respuesta rápida</div></div>
<div class="b">
<button class="icon mic" id="micBtn" onclick="toggleMic()">🎤</button>
<button class="icon cam" onclick="document.getElementById('cam').click()">📷</button>
<input type="file" id="cam" accept="image/*" capture="environment" style="display:none" onchange="up(this)">
<button class="icon img" onclick="askImg()">🖼️</button>
<input id="q" placeholder="Escribe o habla..." onkeypress="if(event.key=='Enter')send()">
<button class="icon send" onclick="send()">➤</button>
</div>
</div>
<script>
let lastImg=null, rec=null, isRec=false;
function askImg(){let p=prompt('¿Qué imagen realista quieres? Ej: perro labrador en la playa'); if(p){document.getElementById('q').value='crea una imagen realista de '+p; send();}}

function up(input){
 let f=input.files[0]; if(!f) return;
 let r=new FileReader(); r.onload=e=>{lastImg=e.target.result; document.getElementById('m').innerHTML+=`<div class="u"><img src="${lastImg}" style="width:100%;border-radius:12px"></div>`; send(true);}; r.readAsDataURL(f);
}

function toggleMic(){
 if(!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)){alert('Tu navegador no soporta voz, usa Chrome'); return;}
 const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
 if(!rec){rec=new SR(); rec.lang='es-CO'; rec.continuous=false; rec.onresult=e=>{document.getElementById('q').value=e.results[0][0].transcript; send();}; rec.onend=()=>{isRec=false; document.getElementById('micBtn').innerText='🎤';};}
 if(isRec){rec.stop(); return;}
 rec.start(); isRec=true; document.getElementById('micBtn').innerText='🔴';
}

async function send(isPhoto=false){
 let q=document.getElementById('q'), txt=q.value.trim();
 if(!txt && !isPhoto) return;
 if(isPhoto && !txt) txt='que ves en la imagen? descríbela';
 let box=document.getElementById('m');
 if(!isPhoto){box.innerHTML+=`<div class="u">${txt}</div>`;}
 q.value=''; box.scrollTop=box.scrollHeight;
 let div=document.createElement('div'); div.className='i typing'; div.innerText='SAM está pensando...⚡'; box.appendChild(div); box.scrollTop=box.scrollHeight;
 try{
   let body={message:txt}; if(lastImg){body.image=lastImg; lastImg=null;}
   let res=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
   let j=await res.json();
   div.classList.remove('typing');
   div.innerHTML=marked.parse(j.reply);
 }catch(e){div.innerText='Error de conexión, reintenta';}
 box.scrollTop=box.scrollHeight;
}
</script></body></html>
"""

def call_gemini_fast(prompt, image_b64=None):
    K = os.environ.get("GEMINI_API_KEY")
    if not K:
        return "Falta GEMINI_API_KEY"
    
    # MODELO TURBO - el más rápido
    models = ["gemini-2.0-flash-lite", "gemini-2.0-flash", "gemini-flash-latest"]
    
    for model in models:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={K}"
            parts = [{"text": f"Eres SAM, asistente de Santi. Responde corto, rápido, elegante, en español colombiano. Pregunta: {prompt}"}]
            if image_b64:
                b64 = image_b64.split(",")[1] if "," in image_b64 else image_b64
                parts.append({"inline_data": {"mime_type": "image/jpeg", "data": b64}})
            
            r = requests.post(url, json={
                "contents": [{"parts": parts}],
                "generationConfig": {"maxOutputTokens": 600, "temperature": 0.7}
            }, timeout=20)
            
            j = r.json()
            if 'candidates' in j and j['candidates']:
                return j['candidates'][0]['content']['parts'][0]['text']
        except:
            continue
    return "SAM está tardando, reintenta en 3 seg"

@app.route('/')
def home(): return render_template_string(HTML)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    msg = data.get('message','Hola')
    img = data.get('image')

    # IMAGEN ULTRA REALISTA
    if "imagen" in msg.lower() and "realista" in msg.lower() or ("imagen" in msg.lower() and not img and len(msg)>8):
        txt = msg.lower()
        for w in ["crea una imagen realista de","crea imagen realista de","crea una imagen de","imagen realista de","imagen de","crea","realista","crea una imagen","genera"]:
            txt = txt.replace(w,"")
        p = txt.strip() or "perro"
        # Prompt pro para realismo
        prompt = f"professional photograph of {p}, ultra realistic, 8k, DSLR, natural skin texture, cinematic lighting, highly detailed, photorealism"
        seed = random.randint(1, 9999999)
        # Usamos flux + enhance para máximo realismo
        url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=1024&height=1024&model=flux&enhance=true&nologo=true&seed={seed}"
        return jsonify({"reply": f"Aquí tienes **{p}** ultra realista 👽📸\n\n![{p}]({url})\n\n_Dale clic a la imagen para verla grande. Si dice 'free limit', espera 45s_"})

    reply = call_gemini_fast(msg, img)
    return jsonify({"reply": reply})

if __name__ == '__main__':
    app.run()
