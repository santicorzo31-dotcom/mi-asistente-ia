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
.ia p{margin:8px 0}
.ia strong{color:#a7f3d0}
.bar{display:flex;padding:10px;gap:6px;border-top:1px solid #eee;background:#f9fafb;align-items:center}
#msg{flex:1;padding:12px 16px;border-radius:25px;border:1px solid #bbf7d0;outline:none}
button{border:none;border-radius:25px;padding:10px 14px;font-weight:bold;cursor:pointer}
.send{background:#14532d;color:white}
.mic{background:#e8f5e9}
</style></head><body>
<div class="header">🌿🙃😎 Soy Sam - tu super ayudante digital 👽</div>
<div id="chat"><div id="messages"><div class="ia">Soy Sam 👽 tu super ayudante digital. Si me pides fórmulas te las explico con manzanas 🍎 para que entiendas de una.</div></div>
<div class="bar">
<button class="mic" onclick="voice()">🎤</button>
<input id="msg" placeholder="Ej: explícame A = pi r²..." onkeypress="if(event.key==='Enter')send()">
<button class="send" onclick="send()">Enviar</button>
</div></div>
<script>
let rec;
function voice(){
  let SR=window.SpeechRecognition||window.webkitSpeechRecognition;
  if(!SR) return alert('Usa Chrome');
  rec=new SR(); rec.lang='es-ES'; rec.onresult=e=>{document.getElementById('msg').value=e.results[0][0].transcript; send();}; rec.start();
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
    setTimeout(renderMath, 100);
  }catch(e){ d.innerText='Dale enviar de nuevo'; }
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
        prompt = f"""Eres Sam, super ayudante.
INSTRUCCIONES IMPORTANTES:
- NUNCA pegues palabras: escribe "como una pizza entera" no "comounapizzaentera".
- Usa lista con saltos de linea, no todo pegado.
- NO uses ** ni * excesivo, usa texto normal limpio.
- Si es formula, ponla asi: $A = \\pi r^2$ en una linea separada.
- Explica en 3 puntos cortos: 1) Que es cada letra 2) Ejemplo con numeros 3) Truco.
- Max 120 palabras, facil de entender.

Usuario: {msg}"""
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": 300, "temperature": 0.6}
        }
        r = sess.post(url, json=payload, timeout=12)
        text = r.json()['candidates'][0]['content']['parts'][0]['text']
        return jsonify({"reply": text})
    except Exception as e:
        print(e)
        return jsonify({"reply": "Dale enviar de nuevo 🙏"})

if __name__ == '__main__':
    app.run() 
