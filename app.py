import os
from flask import Flask, request, jsonify, render_template_string
from google import genai

app = Flask(__name__)

HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mi Asistente IA</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0f3d20;min-height:100vh;display:flex;flex-direction:column}
.header{background:#0a2e18;padding:15px;text-align:center;box-shadow:0 2px 10px rgba(0,0,0,0.3)} .header h1{margin:0;color:#a7f3d0;font-size:22px}
#chat{flex:1;max-width:700px;width:100%;margin:20px auto;background:white;border-radius:20px;box-shadow:0 10px 40px rgba(0,0,0,0.3);display:flex;flex-direction:column;overflow:hidden;height:75vh}
#messages{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:12px;background:white}
.msg{max-width:80%;padding:12px 16px;border-radius:18px;line-height:1.5;word-wrap:break-word}
.user{align-self:flex-end;background:#bbf7d0;color:#052e16;border-bottom-right-radius:4px;border:1px solid #86efac;font-weight:500}
.ia{align-self:flex-start;background:#14532d;color:white;border-bottom-left-radius:4px}
.ia h1,.ia h2,.ia h3{margin:10px 0 5px 0;color:#bbf7d0}
.ia ul{margin:5px 0;padding-left:20px}
.ia strong{color:#bbf7d0}
.input-area{display:flex;padding:15px;border-top:1px solid #e5e7eb;background:#f9fafb}
#msg{flex:1;padding:12px 16px;border:1px solid #bbf7d0;border-radius:25px;outline:none;font-size:15px}
#msg:focus{border-color:#14532d}
button{margin-left:10px;padding:12px 20px;background:#14532d;color:white;border:none;border-radius:25px;cursor:pointer;font-weight:bold}
button:disabled{opacity:0.5}
.typing{font-style:italic;color:#a7f3d0}
</style></head><body>
<div class="header"><h1>🌿 Mi Asistente IA</h1></div>
<div id="chat"><div id="messages"><div class="msg ia">¡Yoo! 👋 ¿Qué más? Soy tu asistente, me puedes preguntar lo que sea 😎<br><br>Tareas, cuentos, historia... tú dirás.</div></div>
<div class="input-area"><input id="msg" placeholder="Escribe tu pregunta..." onkeypress="if(event.key==='Enter')send()"><button id="btn" onclick="send()">Enviar</button></div></div>
<script>
let sending=false;
async function send(){
 if(sending) return;
 let input=document.getElementById('msg');
 let text=input.value.trim(); if(!text) return;
 let box=document.getElementById('messages');
 box.innerHTML+=`<div class="msg user">${text}</div>`;
 input.value=''; sending=true;
 document.getElementById('btn').disabled=true;
 let typingId='typing-'+Date.now();
 box.innerHTML+=`<div id="${typingId}" class="msg ia typing">Escribiendo... ⏳</div>`;
 box.scrollTop=box.scrollHeight;
 try{
   let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:text})});
   let d=await r.json();
   document.getElementById(typingId).remove();
   let html=marked.parse(d.reply);
   box.innerHTML+=`<div class="msg ia">${html}</div>`;
 }catch(e){ document.getElementById(typingId).innerHTML='Error, intenta de nuevo'; }
 sending=false; document.getElementById('btn').disabled=false; box.scrollTop=box.scrollHeight;
}
</script></body></html>"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        client = genai.Client(api_key=api_key)
        msg = request.get_json().get('message','Hola')
        resp = client.models.generate_content(model='gemini-3.8-flash', contents=msg)
        return jsonify({'reply': resp.text})
    except Exception as e:
        return jsonify({'reply': f'Error: {str(e)}'})

if __name__ == '__main__':
    app.run()
