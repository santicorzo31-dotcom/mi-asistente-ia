import os, json, requests
from flask import Flask, request, Response, render_template_string

app = Flask(__name__)

API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL = "gemini-flash-lite-latest"

# ESTO ES LA CLAVE: guarda la conexión abierta, no la cierra nunca
session = requests.Session()
session.headers.update({"Content-Type": "application/json"})

HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>🌿🙃😎 Soy Sam - tu super ayudante digital 👽</title>
<style>
body{margin:0;font-family:-apple-system,sans-serif;background:#0f3d20;min-height:100vh;display:flex;flex-direction:column}
.header{background:#0a2e18;padding:15px;text-align:center} .header h1{margin:0;color:#a7f3d0;font-size:17px}
#chat{max-width:700px;width:95%;margin:15px auto;background:white;border-radius:20px;display:flex;flex-direction:column;overflow:hidden;height:80vh}
#messages{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:12px}
.msg{max-width:85%;padding:12px 16px;border-radius:18px;line-height:1.5;white-space:pre-wrap}
.user{align-self:flex-end;background:#bbf7d0;color:#052e16}
.ia{align-self:flex-start;background:#14532d;color:white}
.input-area{display:flex;align-items:center;padding:10px;border-top:1px solid #eee;background:#f9fafb;gap:6px}
#msg{flex:1;padding:12px 16px;border:1px solid #bbf7d0;border-radius:25px;outline:none}
.btn{padding:12px 14px;border:none;border-radius:25px;font-weight:bold;cursor:pointer}
.mic{background:#e8f5e9;font-size:18px}
.send{background:#14532d;color:white}
</style></head><body>
<div class="header"><h1>🌿🙃😎 Soy Sam - tu super ayudante digital 👽</h1></div>
<div id="chat"><div id="messages"><div class="msg ia">Soy Sam 👽 modo ultra rápido ⚡ ¿Qué necesitas?</div></div>
<div class="input-area">
<button class="btn mic" onclick="toggleVoice()">🎤</button>
<input id="msg" placeholder="Escribe..." autofocus onkeypress="if(event.key==='Enter')send()">
<button class="btn send" onclick="send()">Enviar</button>
</div></div>
<script>
let recognition;
function toggleVoice(){
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if(!SR){ alert('Usa Chrome'); return; }
  if(!recognition){ recognition = new SR(); recognition.lang='es-ES'; recognition.onresult = e=>{ document.getElementById('msg').value=e.results[0][0].transcript; send(); }; }
  recognition.start();
}
async function send(){
  let input=document.getElementById('msg'); let text=input.value.trim(); if(!text) return;
  let box=document.getElementById('messages');
  box.innerHTML+=`<div class="msg user">${text}</div>`; input.value='';
  let div=document.createElement('div'); div.className='msg ia'; div.id='curr'+Date.now(); box.appendChild(div);
  let currId = div.id;
  box.scrollTop=box.scrollHeight;
  
  let resp = await fetch('/chat_stream', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({message:text})});
  let reader = resp.body.getReader(); let decoder = new TextDecoder(); let full='';
  while(true){
    let {done, value} = await reader.read(); if(done) break;
    let chunk = decoder.decode(value);
    chunk.split('\\n').forEach(line=>{
      if(line.startsWith('data: ')){
        try{ let d=JSON.parse(line.slice(6)); if(d.text){ full+=d.text; document.getElementById(currId).innerText=full; box.scrollTop=box.scrollHeight; } }catch(e){}
      }
    });
  }
}
</script></body></html>"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/chat_stream', methods=['POST'])
def chat_stream():
    user_msg = request.get_json().get('message','Hola')
    prompt = f"Responde corto y directo: {user_msg}"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:streamGenerateContent?alt=sse&key={API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 250, "temperature": 0.6}
    }

    def generate():
        try:
            with session.post(url, json=payload, stream=True, timeout=15) as r:
                for line in r.iter_lines():
                    if not line: continue
                    s = line.decode('utf-8')
                    if '"text"' not in s: continue
                    try:
                        j = json.loads(s.replace('data: ',''))
                        txt = j['candidates'][0]['content']['parts'][0].get('text','')
                        if txt:
                            yield f"data: {json.dumps({'text': txt})}\n\n"
                    except:
                        pass
        except Exception as e:
            yield f"data: {json.dumps({'text': 'Dale enviar de nuevo, se trabó un segundo'})}\n\n"

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run() 
