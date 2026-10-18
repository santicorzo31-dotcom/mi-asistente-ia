from flask import Flask, request, jsonify, render_template_string
import os, requests, urllib.parse, random

app = Flask(__name__)

HTML = """<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sam</title><script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>body{margin:0;background:#052e16;font-family:sans-serif;display:flex;flex-direction:column;height:100dvh}
.h{background:#0a2e18;color:#a7f3d0;padding:12px;text-align:center;font-weight:bold}
#c{max-width:700px;width:100%;margin:0 auto;background:#fff;flex:1;display:flex;flex-direction:column;overflow:hidden}
#m{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:10px}
.u{align-self:flex-end;background:#bbf7d0;padding:10px 14px;border-radius:18px;max-width:80%}
.i{align-self:flex-start;background:#14532d;color:#fff;padding:14px;border-radius:18px;max-width:88%;white-space:pre-wrap}
.i img{max-width:100%;border-radius:12px}
.b{display:flex;padding:12px;gap:8px;border-top:1px solid #eee}
#q{flex:1;padding:12px;border-radius:25px;border:1px solid #ccc;outline:none}
button{border:none;border-radius:50%;width:42px;height:42px;cursor:pointer}
.s{background:#14532d;color:#fff}</style></head><body>
<div class="h">🌿 SAM 👽</div><div id="c"><div id="m"><div class="i">Hola Santi, ya quedé 🙏</div></div>
<div class="b"><button onclick="document.getElementById('cam').click()">📷</button>
<input type="file" id="cam" accept="image/*" style="display:none" onchange="up(this)">
<button onclick="let p=prompt('¿Qué imagen?');if(p){document.getElementById('q').value='crea una imagen de '+p;send()}">🖼️</button>
<input id="q" placeholder="Escribe..." onkeypress="if(event.key=='Enter')send()">
<button class="s" onclick="send()">➤</button></div></div>
<script>
let last=null;
function up(i){let f=i.files[0];let r=new FileReader();r.onload=e=>{last=e.target.result;document.getElementById('m').innerHTML+=`<div class="u"><img src="${last}"></div>`;send(true)};r.readAsDataURL(f)}
async function send(photo=false){
 let q=document.getElementById('q'),t=q.value.trim();if(!t&&!photo)return;if(!t)t="que ves?";
 let m=document.getElementById('m');if(!photo)m.innerHTML+=`<div class="u">${t}</div>`;q.value='';
 let d=document.createElement('div');d.className='i';d.innerText='⚡...';m.appendChild(d);m.scrollTop=m.scrollHeight;
 let body={message:t};if(last){body.image=last;last=null}
 let res=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
 let j=await res.json();d.innerHTML=marked.parse(j.reply);m.scrollTop=m.scrollHeight
}
</script></body></html>"""

def call_gemini(prompt, image_b64=None):
    K = os.environ.get("GEMINI_API_KEY")
    if not K:
        return "Falta GEMINI_API_KEY en Vercel > Settings > Environment Variables"
    
    # Modelos nuevos 2026 - probamos en orden
    models = ["gemini-2.0-flash", "gemini-2.5-flash", "gemini-flash-latest", "gemini-1.5-flash-latest"]
    
    for model in models:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={K}"
            parts = [{"text": prompt}]
            if image_b64:
                b64 = image_b64.split(",")[1] if "," in image_b64 else image_b64
                parts.append({"inline_data": {"mime_type": "image/jpeg", "data": b64}})
            
            r = requests.post(url, json={"contents": [{"parts": parts}]}, timeout=25)
            j = r.json()
            if 'candidates' in j and j['candidates']:
                return j['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            continue
    return f"No se pudo conectar a Gemini. Respuesta: {str(j)[:400]}"

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        msg = data.get('message','Hola')
        img = data.get('image')

        # Imagen realista con Pollinations (gratis y no falla)
        if "imagen" in msg.lower() and len(msg) > 5 and not img:
            p = msg.lower().replace("crea una imagen de","").replace("crea imagen","").replace("imagen de","").replace("crea","").strip() or "alien cute"
            prompt = f"{p}, photorealistic, 8k, ultra detailed, cinematic lighting"
            url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=1024&height=1024&model=flux&seed={random.randint(1,999999)}"
            return jsonify({"reply": f"Aquí tienes **{p}** 👽\n\n![imagen]({url})"})

        reply = call_gemini(msg, img)
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"})

if __name__ == '__main__':
    app.run() 
