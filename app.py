from flask import Flask, request, jsonify, render_template_string
import os, requests, urllib.parse, random

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SAM</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
body{margin:0;background:#052e16;font-family:sans-serif;display:flex;justify-content:center;height:100dvh}
#app{width:100%;max-width:500px;background:#fff;display:flex;flex-direction:column}
.h{background:#052e16;color:#bbf7d0;padding:14px;text-align:center;font-weight:bold;font-size:20px}
#m{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:10px;background:#f1f5f9}
.u{align-self:flex-end;background:#bbf7d0;padding:10px 14px;border-radius:18px;max-width:80%}
.i{align-self:flex-start;background:#14532d;color:#fff;padding:12px;border-radius:18px;max-width:90%}
.i img{width:100%;border-radius:12px;margin-top:8px}
.b{display:flex;gap:8px;padding:12px;border-top:1px solid #ddd;background:#fff}
#q{flex:1;padding:12px;border-radius:24px;border:1px solid #ccc;outline:none}
button{border:none;border-radius:50%;width:42px;height:42px;cursor:pointer}
.send{background:#14532d;color:#fff}
</style>
</head><body>
<div id="app">
<div class="h">🌿 SAM 👽</div>
<div id="m"><div class="i">Hola Santi, ya quedé 🙏 Elegante y rápido</div></div>
<div class="b">
<button onclick="document.getElementById('cam').click()">📷</button>
<input type="file" id="cam" accept="image/*" style="display:none" onchange="up(this)">
<button onclick="ask()">🖼️</button>
<button id="mic" onclick="mic()">🎤</button>
<input id="q" placeholder="Escribe..." onkeypress="if(event.key=='Enter')send()">
<button class="send" onclick="send()">➤</button>
</div>
</div>
<script>
let last=null;
function ask(){let p=prompt('Que imagen?'); if(p){document.getElementById('q').value='crea una imagen realista de '+p; send();}}
function up(i){let f=i.files[0]; let r=new FileReader(); r.onload=e=>{last=e.target.result; document.getElementById('m').innerHTML+=`<div class="u"><img src="${last}"></div>`; send(true);}; r.readAsDataURL(f);}
function mic(){
 let SR=window.SpeechRecognition||window.webkitSpeechRecognition;
 let rec=new SR(); rec.lang='es-CO';
 rec.onresult=e=>{document.getElementById('q').value=e.results[0][0].transcript; send();}
 rec.start();
}
async function send(photo=false){
 let q=document.getElementById('q'), t=q.value.trim();
 if(!t && !photo) return;
 if(photo && !t) t='que ves?';
 let m=document.getElementById('m');
 if(!photo) m.innerHTML+=`<div class="u">${t}</div>`;
 q.value='';
 let d=document.createElement('div'); d.className='i'; d.innerText='⚡...'; m.appendChild(d); m.scrollTop=m.scrollHeight;
 let body={message:t}; if(last){body.image=last; last=null;}
 let res=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
 let j=await res.json(); d.innerHTML=marked.parse(j.reply); m.scrollTop=m.scrollHeight;
}
</script></body></html>
"""

def call_gemini(prompt, image_b64=None):
    K = os.environ.get("GEMINI_API_KEY")
    if not K:
        return "Falta GEMINI_API_KEY en Vercel"
    models = ["gemini-2.0-flash", "gemini-flash-latest"]
    for model in models:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={K}"
            parts = [{"text": prompt}]
            if image_b64:
                b64 = image_b64.split(",")[1] if "," in image_b64 else image_b64
                parts.append({"inline_data": {"mime_type": "image/jpeg", "data": b64}})
            r = requests.post(url, json={"contents": [{"parts": parts}], "generationConfig": {"maxOutputTokens": 600}}, timeout=20)
            j = r.json()
            if 'candidates' in j:
                return j['candidates'][0]['content']['parts'][0]['text']
        except:
            continue
    return "Error de Gemini, reintenta"

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    msg = data.get('message','Hola')
    img = data.get('image')
    if "imagen" in msg.lower() and not img:
        p = msg.lower().replace("crea una imagen realista de","").replace("crea una imagen de","").replace("imagen de","").replace("crea","").strip()
        if not p: p = "perro"
        prompt = f"professional photo of {p}, photorealistic, 8k, ultra detailed"
        url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=1024&height=1024&model=flux&nologo=true&seed={random.randint(1,9999999)}"
        return jsonify({"reply": f"Aqui tienes **{p}** realista 👽\n\n![imagen]({url})\n\nSi sale 'free limit', espera 45s"})
    reply = call_gemini(msg, img)
    return jsonify({"reply": reply}) 
