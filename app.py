from flask import Flask, request, jsonify
import os, requests, json

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SAM - Tu Asistente</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:system-ui,-apple-system,sans-serif}
body{background:#f5f5f5;display:flex;flex-direction:column;height:100vh;height:100dvh}
header{background:#0f3d1f;color:#a7f3d0;padding:18px;text-align:center;font-weight:700;font-size:22px;letter-spacing:1px}
#chat{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:12px}
.msg{padding:14px 18px;border-radius:20px;max-width:85%;line-height:1.4;word-wrap:break-word}
.bot{background:#14532d;color:white;align-self:flex-start;border-bottom-left-radius:6px}
.user{background:#dcfce7;color:#14532d;align-self:flex-end;border-bottom-right-radius:6px}
#bar{background:white;padding:12px;display:flex;gap:10px;align-items:center;border-top:1px solid #e5e5e5}
.icon-btn{background:#f0f0f0;border:0;width:44px;height:44px;border-radius:50%;font-size:20px;cursor:pointer}
#input{flex:1;background:#f5f5f5;border:1px solid #e5e5e5;padding:14px 18px;border-radius:30px;outline:none;font-size:16px}
#send{background:#14532d;color:white;border:0;width:50px;height:50px;border-radius:50%;font-size:20px;cursor:pointer}
.loading{opacity:0.6;font-style:italic}
</style>
</head>
<body>
<header>🌿 SAM 👽</header>
<div id="chat">
<div class="msg bot">Hola Santi, ya quedé 🙏 Elegante y rápido</div>
</div>
<div id="bar">
<button class="icon-btn">📷</button>
<button class="icon-btn">🖼️</button>
<button class="icon-btn">🎤</button>
<input id="input" placeholder="Escribe..." autocomplete="off">
<button id="send" onclick="sendMsg()">➤</button>
</div>
<script>
const chat = document.getElementById('chat');
const input = document.getElementById('input');

async function sendMsg(){
  const text = input.value.trim();
  if(!text) return;
  chat.innerHTML += `<div class="msg user">${text}</div>`;
  input.value = '';
  chat.scrollTop = chat.scrollHeight;
  
  const loadingId = 'load-'+Date.now();
  chat.innerHTML += `<div class="msg bot loading" id="${loadingId}">Escribiendo...</div>`;
  chat.scrollTop = chat.scrollHeight;

  try{
    const res = await fetch('/chat', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({message: text})
    });
    const data = await res.json();
    document.getElementById(loadingId).remove();
    chat.innerHTML += `<div class="msg bot">${data.reply.replace(/\\n/g,'<br>')}</div>`;
  }catch(e){
    document.getElementById(loadingId).remove();
    chat.innerHTML += `<div class="msg bot">❌ Error de conexión, reintenta</div>`;
  }
  chat.scrollTop = chat.scrollHeight;
}

input.addEventListener('keydown', e=>{
  if(e.key==='Enter') sendMsg();
});
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
        body = request.get_json()
        prompt = body.get('message','') if body else ''
        if not prompt:
            return jsonify({'reply': 'Escribe algo Santi'})

        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            return jsonify({'reply': '❌ No hay GEMINI_API_KEY en Vercel. Ve a Settings > Environment Variables'})

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": f"Eres SAM, el asistente de Santi. Responde corto, útil, amigable y en español. Usuario dice: {prompt}"}]}]
        }
        r = requests.post(url, json=payload, timeout=30)
        data = r.json()

        if 'candidates' in data and len(data['candidates'])>0:
            reply = data['candidates'][0]['content']['parts'][0]['text']
            return jsonify({'reply': reply})
        else:
            # Si falla, muestra el error real para arreglarlo
            err = json.dumps(data)[:800]
            print("Gemini Error:", err)
            if 'API_KEY_INVALID' in err:
                return jsonify({'reply': '❌ API KEY inválida. Crea otra en aistudio.google.com/apikey'})
            if 'QUOTA' in err:
                return jsonify({'reply': '❌ Se acabó la cuota gratis de Gemini, espera 1 min'})
            return jsonify({'reply': f'Error Gemini: {err}'})

    except Exception as e:
        print("Server Error:", str(e))
        return jsonify({'reply': f'Error servidor: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True)
</script></body></html>
"""

@app.route('/')
def index():
    return HTML

@app.route('/chat', methods=['POST'])
def chat_route():
    try:
        body = request.get_json()
        prompt = body.get('message','') if body else ''
        if not prompt:
            return jsonify({'reply': 'Escribe algo Santi'})

        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            return jsonify({'reply': '❌ No hay GEMINI_API_KEY en Vercel. Ve a Settings > Environment Variables'})

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": f"Eres SAM, el asistente de Santi. Responde corto, útil, amigable y en español. Usuario dice: {prompt}"}]}]
        }
        r = requests.post(url, json=payload, timeout=30)
        data = r.json()

        if 'candidates' in data and len(data['candidates'])>0:
            reply = data['candidates'][0]['content']['parts'][0]['text']
            return jsonify({'reply': reply})
        else:
            err = json.dumps(data)[:800]
            print("Gemini Error:", err)
            if 'API_KEY_INVALID' in err:
                return jsonify({'reply': '❌ API KEY inválida. Crea otra en aistudio.google.com/apikey'})
            if 'QUOTA' in err:
                return jsonify({'reply': '❌ Se acabó la cuota gratis de Gemini, espera 1 min'})
            return jsonify({'reply': f'Error Gemini: {err}'})

    except Exception as e:
        print("Server Error:", str(e))
        return jsonify({'reply': f'Error servidor: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True) 
