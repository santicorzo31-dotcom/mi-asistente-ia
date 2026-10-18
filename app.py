import os
from flask import Flask, request, jsonify, render_template_string
from google import genai
import time

app = Flask(__name__)

HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mi Asistente IA</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
body{margin:0;font-family:-apple-system,sans-serif;background:#0f3d20;min-height:100vh;display:flex;flex-direction:column}
.header{background:#0a2e18;padding:15px;text-align:center} .header h1{margin:0;color:#a7f3d0;font-size:22px}
#chat{max-width:700px;width:95%;margin:15px auto;background:white;border-radius:20px;display:flex;flex-direction:column;overflow:hidden;height:80vh}
#messages{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:12px}
.msg{max-width:85%;padding:12px 16px;border-radius:18px;line-height:1.5}
.user{align-self:flex-end;background:#bbf7d0;color:#052e16}
.ia{align-self:flex-start;background:#14532d;color:white}
.input-area{display:flex;padding:12px;border-top:1px solid #eee;background:#f9fafb}
#msg{flex:1;padding:12px 16px;border:1px solid #bbf7d0;border-radius:25px;outline:none}
button{margin-left:8px;padding:12px 18px;background:#14532d;color:white;border:none;border-radius:25px;font-weight:bold}
</style></head><body>
<div class="header"><h1>🌿 Mi Asistente IA</h1></div>
<div id="chat"><div id="messages"><div class="msg ia">Hola, ¿qué más? Soy tu asistente personal 😎<br>Tareas, cuentos, historia... tú dirás.</div></div>
<div class="input-area"><input id="msg" placeholder="Escribe..." onkeypress="if(event.key==='Enter')send()"><button onclick="send()">Enviar</button></div></div>
<script>
async function send(){
 let input=document.getElementById('msg'); let text=input.value.trim(); if(!text) return;
 let box=document.getElementById('messages');
 box.innerHTML+=`<div class="msg user">${text}</div>`; input.value='';
 let tid='t'+Date.now(); box.innerHTML+=`<div id="${tid}" class="msg ia">Escribiendo... ⏳ (si Google está ocupado reintento solo)</div>`;
 box.scrollTop=box.scrollHeight;
 let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:text})});
 let d=await r.json(); document.getElementById(tid).remove();
 let html=marked.parse(d.reply);
 let div=document.createElement('div'); div.className='msg ia'; div.innerHTML=html;
 box.appendChild(div); box.scrollTop=box.scrollHeight;
}
</script></body></html>"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/chat', methods=['POST'])
def chat():
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    user_msg = request.get_json().get('message','Hola')
    prompt = f"Eres amigable. NUNCA uses $ o LaTeX. Escribe formulas como E = m x c^2. Pregunta: {user_msg}"

    modelos = ['gemini-2.0-flash-lite', 'gemini-1.5-flash', 'gemini-2.0-flash']
    
    for modelo in modelos:
        for intento in range(3): # 3 intentos por modelo
            try:
                resp = client.models.generate_content(model=modelo, contents=prompt)
                if resp.text:
                    return jsonify({'reply': resp.text})
            except Exception as e:
                err = str(e)
                # Si es 503, espera 2 seg y reintenta solo
                if "503" in err or "UNAVAILABLE" in err:
                    time.sleep(2)
                    continue
                time.sleep(1)
                continue
    
    return jsonify({'reply': 'Google sigue muy ocupado en este momento (es global). Dale a Enviar de nuevo en 15 segundos, ya casi entra 🙏'})

if __name__ == '__main__':
    app.run() 
