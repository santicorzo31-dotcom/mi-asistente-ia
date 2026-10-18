import os
from flask import Flask, request, jsonify, render_template_string
import google.generativeai as genai

app = Flask(__name__)

api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

HTML = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Mi Asistente IA</title><style>body{font-family:system-ui;background:#0f0f0f;color:white;display:flex;justify-content:center;padding:20px} .box{width:100%;max-width:600px} h1{color:#c3a6ff} textarea{width:100%;padding:12px;border-radius:12px;border:1px solid #444;background:#1a1a1a;color:white;box-sizing:border-box} button{background:#a78bfa;border:0;padding:12px 20px;border-radius:10px;font-weight:bold;margin-top:10px;cursor:pointer} #respuesta{margin-top:20px;white-space:pre-wrap;background:#1e1e1e;padding:15px;border-radius:12px;min-height:20px}</style></head><body><div class="box"><h1>Mi Asistente IA</h1><p>Hola! Soy tu asistente personal. En que te ayudo?</p><textarea id="m" rows="4" placeholder="Escribe tu mensaje..."></textarea><br><button onclick="send()">Enviar</button><div id="respuesta"></div></div><script>async function send(){let m=document.getElementById('m').value;let r=document.getElementById('respuesta');if(!m.trim())return;r.textContent='Pensando...';let res=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:m})});let d=await res.json();r.textContent=d.reply;}</script></div></body></html>"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/chat', methods=['POST'])
def chat():
    if not model:
        return jsonify({'reply': 'Falta configurar GEMINI_API_KEY en Vercel. Ve a Settings > Environment Variables.'})
    data = request.get_json()
    msg = data.get('message','')
    resp = model.generate_content(msg)
    return jsonify({'reply': resp.text})

if __name__ == '__main__':
    app.run()
