from flask import Flask, request, jsonify
import os, requests, json, base64, urllib.parse
app = Flask(__name__)

HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SAM</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@500;700&family=Geist:wght@400;500&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#fff;color:#111;font-family:'Geist',sans-serif;height:100vh;display:flex;flex-direction:column}
header{height:52px;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:16px;border-bottom:1px solid #f1f1f1;letter-spacing:-0.3px}
#chat{flex:1;overflow-y:auto;padding:28px 20px;max-width:760px;width:100%;margin:0 auto;display:flex;flex-direction:column;gap:24px}
.user-wrap{display:flex;justify-content:flex-end}
.msg-user{background:#111;color:#fff;padding:12px 18px;border-radius:22px;font-family:'Inter',sans-serif;font-weight:700;font-size:15px;letter-spacing:-0.2px;max-width:78%;line-height:1.4}
.bot-wrap{display:flex;gap:10px;align-items:flex-start}
.avatar{width:28px;height:28px;border-radius:50%;background:#e8f5e9;display:flex;align-items:center;justify-content:center;font-size:14px;flex-shrink:0;margin-top:2px}
.msg-bot{font-family:'Geist',sans-serif;font-weight:400;font-size:15.5px;color:#2a2a2a;line-height:1.7;letter-spacing:-0.1px;max-width:92%}
.msg-bot b{font-weight:600;color:#111}
#bottom{padding:14px 16px 20px 16px;background:#fff;position:sticky;bottom:0}
#box{max-width:760px;margin:0 auto;background:#f6f6f7;border:1.5px solid #efefef;border-radius:28px;padding:6px 10px 6px 14px;display:flex;align-items:flex-end;gap:6px}
#box:focus-within{border-color:#111;background:#fff;box-shadow:0 4px 20px rgba(0,0,0,.06)}
#input{flex:1;background:transparent;border:0;outline:none;font-size:16px;font-family:'Geist';padding:10px 0;resize:none;max-height:140px;line-height:1.5}
.icon{width:34px;height:34px;border-radius:50%;border:0;background:transparent;font-size:16px;cursor:pointer;color:#6b7280}
.icon:hover{background:#eee;color:#111}
#send{width:32px;height:32px;border-radius:50%;background:#111;color:#fff;border:0;font-size:16px;cursor:pointer}
#preview{max-width:760px;margin:0 auto 10px auto;display:none}
.loading{display:flex;gap:4px;padding:6px 0}
.loading span{width:5px;height:5px;background:#bbb;border-radius:50%;animation:bounce 1.4s infinite}
.loading span:nth-child(2){animation-delay:.2s}
.loading span:nth-child(3){animation-delay:.4s}
@keyframes bounce{0%,80%,100%{transform:translateY(0)}40%{transform:translateY(-5px)}}
</style>
</head>
<body>
<header>SAM • minimal</header>
<div id="chat"><div class="bot-wrap"><div class="avatar">🌿</div><div class="msg-bot">Quiubo Santi, parce. Soy SAM, ya quedé melo, minimalista y rápido. Tu mensaje va en negro bold, el mío suave. ¿Qué hacemos hoy, mi rey?</div></div></div>
<div id="preview"></div>
<div id="bottom">
<div id="box">
<button class="icon" id="btnFile" title="Subir archivo">📎</button>
<button class="icon" id="btnCam" title="Tomar foto">📷</button>
<textarea id="input" rows="1" placeholder="Pregunta lo que sea..."></textarea>
<button id="send">↑</button>
</div>
<div style="text-align:center;font-size:11px;color:#aaa;margin-top:8px">Di: "crea una imagen de..." para generar</div>
</div>
<input type="file" id="fileInput" accept="image/*,.pdf,.txt" hidden>
<input type="file" id="camInput" accept="image/*" capture="environment" hidden>
<script>
const chat=document.getElementById('chat'),input=document.getElementById('input'),send=document.getElementById('send');
const fileInput=document.getElementById('fileInput'),camInput=document.getElementById('camInput');
let selectedFile=null;
document.getElementById('btnFile').onclick=()=>fileInput.click();
document.getElementById('btnCam').onclick=()=>camInput.click();
fileInput.onchange=e=>{selectedFile=e.target.files[0];showPrev()};
camInput.onchange=e=>{selectedFile=e.target.files[0];showPrev()};
function showPrev(){if(!selectedFile) return;document.getElementById('preview').style.display='block';document.getElementById('preview').innerHTML='<div style="background:#f6f6f7;padding:8px 12px;border-radius:12px;font-size:13px;display:flex;justify-content:space-between">📎 '+selectedFile.name+' <span onclick="clearF()" style="cursor:pointer">✕</span></div>'}
window.clearF=()=>{selectedFile=null;document.getElementById('preview').style.display='none';fileInput.value='';camInput.value='';}
input.addEventListener('input',()=>{input.style.height='auto';input.style.height=input.scrollHeight+'px'});
async function sendMsg(){
 const txt=input.value.trim();
 if(!txt && !selectedFile) return;
 if(txt){chat.innerHTML+='<div class="user-wrap"><div class="msg-user">'+txt.replace(/</g,'&lt;')+'</div></div>'}
 if(selectedFile && selectedFile.type.startsWith('image/')){const u=URL.createObjectURL(selectedFile);chat.innerHTML+='<div class="user-wrap"><img src="'+u+'" style="max-width:180px;border-radius:16px;margin-top:8px"></div>'}
 const id='a'+Date.now();
 chat.innerHTML+='<div class="bot-wrap"><div class="avatar">🌿</div><div class="msg-bot loading" id="'+id+'"><span></span><span></span><span></span></div></div>';
 const textToSend=txt; const fileToSend=selectedFile;
 input.value=''; clearF(); input.style.height='auto'; chat.scrollTop=999999;
 try{
  const fd=new FormData(); fd.append('message',textToSend); if(fileToSend) fd.append('file',fileToSend);
  const r=await fetch('/chat',{method:'POST',body:fd}); const d=await r.json();
  document.getElementById(id).classList.remove('loading');
  document.getElementById(id).innerHTML=(d.reply||'').replace(/\\n/g,'<br>');
  if(d.image_url){document.getElementById(id).innerHTML+='<br><img src="'+d.image_url+'" style="width:100%;border-radius:16px;margin-top:12px">'}
 }catch(e){document.getElementById(id).innerHTML='Paila parce, se cayó la conexión'}
 chat.scrollTop=999999;
}
send.onclick=sendMsg;
input.addEventListener('keydown',e=>{if(e.key==='Enter' && !e.shiftKey){e.preventDefault();sendMsg()}});
</script>
</body>
</html>
"""

@app.route('/')
def home(): 
    return HTML

@app.route('/chat', methods=['POST'])
def chat_api():
    try:
        msg = request.form.get('message','') or (request.get_json(silent=True) or {}).get('message','') or ''
        file = request.files.get('file')
        key = os.environ.get('GEMINI_API_KEY')
        if not key: 
            return jsonify({'reply':'Parce, falta la API KEY en Vercel > Settings > Env Variables'})

        # 1. Generar imagen
        low = msg.lower()
        if any(x in low for x in ['crea una imagen','genera una imagen','haz una imagen','imagen de']):
            prompt_img = msg.replace('crea una imagen de','').replace('crea una imagen','').replace('genera una imagen de','').replace('haz una imagen de','').strip()
            if not prompt_img: prompt_img = "imagen cool"
            enc = urllib.parse.quote(prompt_img)
            img_url = f"https://image.pollinations.ai/prompt/{enc}?width=1024&height=1024&nologo=true&enhance=true&seed={os.urandom(2).hex()}"
            return jsonify({'reply':f'Listo mi rey, chimba de imagen: <b>{prompt_img}</b>','image_url':img_url})

        # 2. Modelo que SI sirve - 3.8 que te pide el error
        system_prompt = f"""Eres SAM, asistente de Santi, de Norte de Santander, Colombia.
        Habla 100% juvenil colombiano casual: usa parce, mi rey, quiubo, melo, chimba, paila, breve, sisas.
        Eres minimalista, elegante, directo, sin rodeos. Respuestas cortas y útiles.
        Si te preguntan algo, responde como un amigo del barrio pero inteligente.
        Usuario: {msg}"""

        parts = [{"text": system_prompt}]
        if file and file.filename:
            b = file.read()
            if len(b) < 4*1024*1024:
                parts.append({"inline_data":{"mime_type":file.mimetype or 'image/jpeg',"data":base64.b64encode(b).decode()}})

        payload = {"contents":[{"parts":parts}]}

        # Intentar modelos en orden, empezando por el 3.8 que te pide Google
        modelos = ["gemini-3.8-flash", "gemini-3.5-flash", "gemini-2.5-flash"]
        last_error = ""
        for modelo in modelos:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={key}"
                r = requests.post(url, json=payload, timeout=30)
                j = r.json()
                if 'candidates' in j and j['candidates']:
                    return jsonify({'reply': j['candidates'][0]['content']['parts'][0]['text']})
                else:
                    last_error = json.dumps(j)[:400]
                    if '404' in last_error or 'not found' in last_error.lower():
                        continue
                    else:
                        break
            except Exception as e:
                last_error = str(e)
                continue
        
        return jsonify({'reply': f"Paila parce, Google dice: {last_error[:300]}. Verifica tu API KEY en aistudio.google.com"})

    except Exception as e:
        return jsonify({'reply':f"Uy parce, error interno: {str(e)[:200]}"})

if __name__=='__main__':
    app.run() 
