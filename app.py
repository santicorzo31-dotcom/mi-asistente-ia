from flask import Flask, request, jsonify
import os, requests, json
app = Flask(__name__)

HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SAM</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:system-ui}
body{background:#f5f5f5;display:flex;flex-direction:column;height:100vh}
header{background:#0f3d1f;color:#a7f3d0;padding:18px;text-align:center;font-weight:700;font-size:22px}
#chat{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:12px}
.msg{padding:14px 18px;border-radius:20px;max-width:85%;line-height:1.4}
.bot{background:#14532d;color:white;align-self:flex-start}
.user{background:#dcfce7;color:#14532d;align-self:flex-end}
#bar{background:white;padding:12px;display:flex;gap:10px;align-items:center;border-top:1px solid #e5e5e5}
#input{flex:1;background:#f5f5f5;border:1px solid #e5e5e5;padding:14px 18px;border-radius:30px;outline:none;font-size:16px}
#send{background:#14532d;color:white;border:0;width:50px;height:50px;border-radius:50%;font-size:20px;cursor:pointer}
</style>
</head>
<body>
<header>🌿 SAM 👽</header>
<div id="chat"><div class="msg bot">Hola Santi, ya quede 🙏</div></div>
<div id="bar"><input id="input" placeholder="Escribe..."><button id="send">➤</button></div>
<script>
const chat=document.getElementById('chat');
const input=document.getElementById('input');
const btn=document.getElementById('send');
async function send(){
 const t=input.value.trim();
 if(!t) return;
 chat.innerHTML+='<div class="msg user">'+t+'</div>';
 input.value='';
 chat.scrollTop=99999;
 const id='a'+Date.now();
 chat.innerHTML+='<div class="msg bot" id="'+id+'">Escribiendo...</div>';
 try{
  const r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:t})});
  const d=await r.json();
  document.getElementById(id).remove();
  chat.innerHTML+='<div class="msg bot">'+d.reply+'</div>';
 }catch(e){
  document.getElementById(id).remove();
  chat.innerHTML+='<div class="msg bot">Error de conexion</div>';
 }
 chat.scrollTop=99999;
}
btn.onclick=send;
input.addEventListener('keydown',e=>{if(e.key==='Enter') send();});
</script>
</body>
</html>
"""

@app.route('/')
def index(): return HTML

@app.route('/chat', methods=['POST'])
def chat_api():
    b=request.get_json()
    p=b.get('message','') if b else ''
    key=os.environ.get('GEMINI_API_KEY')
    if not key: return jsonify({'reply':'No hay KEY'})
    url=f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
    payload={"contents":[{"parts":[{"text":p}]}]}
    r=requests.post(url,json=payload,timeout=30)
    j=r.json()
    if 'candidates' in j:
        return jsonify({'reply':j['candidates'][0]['content']['parts'][0]['text']})
    return jsonify({'reply':'Error: '+json.dumps(j)[:400]})

if __name__=='__main__':
    app.run()
