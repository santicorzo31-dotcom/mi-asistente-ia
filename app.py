from flask import Flask, request, jsonify
import os, requests, json, base64

app = Flask(__name__)

HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SAM - ChatGPT Style</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:Inter,system-ui,sans-serif}
body{background:#ffffff;color:#0f172a;height:100vh;display:flex;flex-direction:column}
header{height:56px;border-bottom:1px solid #e5e7eb;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:18px;background:white;position:sticky;top:0;z-index:10}
header span{background:linear-gradient(90deg,#0f3d1f,#16a34a);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
#chat{flex:1;overflow-y:auto;padding:24px 16px;max-width:800px;width:100%;margin:0 auto;display:flex;flex-direction:column;gap:20px}
.msg{line-height:1.6;font-size:15px;max-width:100%;word-wrap:break-word;white-space:pre-wrap}
.msg.user{background:#f4f4f5;padding:12px 18px;border-radius:20px;align-self:flex-end;max-width:80%}
.msg.bot{align-self:flex-start;max-width:95%;padding:8px 0}
.msg.bot img{max-width:100%;border-radius:16px;margin-top:12px;border:1px solid #e5e7eb}
.loading span{width:6px;height:6px;background:#999;border-radius:50%;display:inline-block;animation:bounce 1.4s infinite}
.loading span:nth-child(2){animation-delay:.2s}
.loading span:nth-child(3){animation-delay:.4s}
@keyframes bounce{0%,80%,100%{transform:scale(0)}40%{transform:scale(1)}}
#bottom{padding:16px;background:white;border-top:1px solid #f0f0f0;position:sticky;bottom:0}
#box{max-width:800px;margin:0 auto;background:#f4f4f5;border-radius:28px;padding:8px 12px;display:flex;align-items:center;gap:8px;box-shadow:0 1px 2px rgba(0,0,0,.05)}
.icon{width:36px;height:36px;border-radius:50%;border:0;background:transparent;font-size:18px;cursor:pointer;display:flex;align-items:center;justify-content:center}
.icon:hover{background:#e4e4e7}
#input{flex:1;background:transparent;border:0;outline:none;font-size:16px;padding:10px 4px;resize:none;max-height:120px}
#send{width:36px;height:36px;border-radius:50%;background:#0f172a;color:white;border:0;font-size:18px;cursor:pointer}
#preview{max-width:800px;margin:0 auto 10px auto;display:none}
#preview img{max-height:80px;border-radius:12px}
#fileInput,#cameraInput{display:none}
</style>
</head>
<body>
<header><span>🌿 SAM • Elegante</span></header>
<div id="chat"><div class="msg bot">Hola Santi, soy SAM. Ya tengo todo: fotos, audio, archivos e imágenes. ¿Qué hacemos hoy?</div></div>
<div id="preview"></div>
<div id="bottom">
<div id="box">
<input type="file" id="fileInput" accept="image/*,application/pdf,.txt,.doc,.docx">
<input type="file" id="cameraInput" accept="image/*" capture="environment">
<button class="icon" id="btnFile" title="Subir archivo">📎</button>
<button class="icon" id="btnCam" title="Tomar foto">📷</button>
<button class="icon" id="btnMic" title="Grabar audio">🎤</button>
<textarea id="input" rows="1" placeholder="Escribe un mensaje..."></textarea>
<button id="send">↑</button>
</div>
<div style="text-align:center;font-size:11px;color:#9ca3af;margin-top:8px">SAM puede crear imágenes. Di: "crea una imagen de..."</div>
</div>
<script>
const chat=document.getElementById('chat');
const input=document.getElementById('input');
const send=document.getElementById('send');
const fileInput=document.getElementById('fileInput');
const cameraInput=document.getElementById('cameraInput');
const preview=document.getElementById('preview');
let selectedFile=null;
let mediaRecorder=null;
let audioChunks=[];

document.getElementById('btnFile').onclick=()=>fileInput.click();
document.getElementById('btnCam').onclick=()=>cameraInput.click();

function showPreview(file){
 selectedFile=file;
 preview.style.display='block';
 if(file.type.startsWith('image/')){
   const url=URL.createObjectURL(file);
   preview.innerHTML='<div style="display:flex;align-items:center;gap:8px;background:#f4f4f5;padding:8px;border-radius:12px"><img src="'+url+'"><span style="font-size:13px">'+file.name+'</span><button onclick="clearFile()" style="margin-left:auto">✕</button></div>';
 } else {
   preview.innerHTML='<div style="display:flex;align-items:center;gap:8px;background:#f4f4f5;padding:8px;border-radius:12px"><span>📄 '+file.name+'</span><button onclick="clearFile()" style="margin-left:auto">✕</button></div>';
 }
}
function clearFile(){selectedFile=null;preview.innerHTML='';preview.style.display='none';fileInput.value='';cameraInput.value='';}
window.clearFile=clearFile;

fileInput.onchange=e=>{if(e.target.files[0]) showPreview(e.target.files[0])};
cameraInput.onchange=e=>{if(e.target.files[0]) showPreview(e.target.files[0])};

input.addEventListener('input',()=>{input.style.height='auto';input.style.height=input.scrollHeight+'px'});

document.getElementById('btnMic').onclick=async()=>{
 if(mediaRecorder && mediaRecorder.state==='recording'){
   mediaRecorder.stop();
   document.getElementById('btnMic').textContent='🎤';
   return;
 }
 try{
   const stream=await navigator.mediaDevices.getUserMedia({audio:true});
   mediaRecorder=new MediaRecorder(stream);
   audioChunks=[];
   mediaRecorder.ondataavailable=e=>audioChunks.push(e.data);
   mediaRecorder.onstop=async()=>{
     const blob=new Blob(audioChunks,{type:'audio/webm'});
     const file=new File([blob],'audio.webm',{type:'audio/webm'});
     await sendMessage(file,'Transcribe este audio y responde');
   };
   mediaRecorder.start();
   document.getElementById('btnMic').textContent='⏹️';
 }catch(e){alert('No se pudo acceder al micrófono')}
};

async function sendMessage(fileOverride=null,textOverride=null){
 const text=textOverride || input.value.trim();
 const file=fileOverride || selectedFile;
 if(!text && !file) return;
 let html='';
 if(text) html+=text;
 chat.innerHTML+='<div class="msg user">'+(html||'📎 Archivo')+'</div>';
 input.value='';
 clearFile();
 input.style.height='auto';
 chat.scrollTop=chat.scrollHeight;
 const id='a'+Date.now();
 chat.innerHTML+='<div class="msg bot loading" id="'+id+'"><span></span><span></span><span></span></div>';
 chat.scrollTop=chat.scrollHeight;
 try{
   const fd=new FormData();
   fd.append('message',text);
   if(file) fd.append('file',file);
   const r=await fetch('/chat',{method:'POST',body:fd});
   const d=await r.json();
   document.getElementById(id).remove();
   let reply=d.reply || 'Sin respuesta';
   let imgHtml='';
   if(d.image_url){
     imgHtml='<br><img src="'+d.image_url+'" alt="imagen generada">';
   }
   chat.innerHTML+='<div class="msg bot">'+reply+imgHtml+'</div>';
 }catch(e){
   document.getElementById(id).remove();
   chat.innerHTML+='<div class="msg bot">❌ Error de conexión</div>';
 }
 chat.scrollTop=chat.scrollHeight;
}

send.onclick=()=>sendMessage();
input.addEventListener('keydown',e=>{if(e.key==='Enter' && !e.shiftKey){e.preventDefault();sendMessage()}});
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return HTML

@app.route('/chat', methods=['POST'])
def chat_route():
    try:
        message = request.form.get('message','') or (request.get_json(silent=True) or {}).get('message','')
        file = request.files.get('file')
        
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            return jsonify({'reply':'❌ Falta GEMINI_API_KEY en Vercel'})

        # 1. Si pide crear imagen
        lower_msg = message.lower()
        if any(x in lower_msg for x in ['crea una imagen', 'genera una imagen', 'haz una imagen', 'create image', 'imagen de']):
            # Extraer prompt de imagen
            prompt_img = message.replace('crea una imagen de','').replace('crea una imagen','').replace('genera una imagen de','').strip()
            if not prompt_img:
                prompt_img = message
            # Usar Pollinations (gratis, rápido, sin key)
            import urllib.parse
            encoded = urllib.parse.quote(prompt_img)
            image_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&nologo=true&enhance=true"
            return jsonify({'reply': f'🖼️ Imagen creada: "{prompt_img}"', 'image_url': image_url})

        # 2. Llamada a Gemini 2.0 Flash (modelo que SI existe)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        
        parts = []
        if message:
            parts.append({"text": message})
        else:
            parts.append({"text": "Hola"})
        
        # Si hay archivo de imagen, enviarlo a Gemini Vision
        if file and file.filename:
            file_bytes = file.read()
            b64 = base64.b64encode(file_bytes).decode('utf-8')
            mime = file.mimetype or 'image/jpeg'
            # Limitar tamaño a 4MB para Gemini
            if len(file_bytes) < 4*1024*1024:
                parts.append({"inline_data": {"mime_type": mime, "data": b64}})

        payload = {"contents": [{"parts": parts}]}

        r = requests.post(url, json=payload, timeout=40)
        data = r.json()

        if 'candidates' in data and data['candidates']:
            text = data['candidates'][0]['content']['parts'][0]['text']
            return jsonify({'reply': text})
        else:
            # Error detallado pero limpio
            if 'error' in data:
                msg = data['error'].get('message','Error desconocido')
                if 'API_KEY' in str(data):
                    return jsonify({'reply': '❌ API KEY inválida. Crea una nueva en aistudio.google.com/apikey'})
                return jsonify({'reply': f'Error Gemini: {msg[:300]}'})
            return jsonify({'reply': f'Error: {json.dumps(data)[:400]}'})

    except Exception as e:
        return jsonify({'reply': f'Error servidor: {str(e)[:300]}'})

if __name__ == '__main__':
    app.run()
