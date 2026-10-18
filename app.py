import os
from flask import Flask, request, jsonify, render_template_string
from google import genai

app = Flask(__name__)

HTML = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<style>body{font-family:sans-serif;max-width:600px;margin:auto;padding:20px}#chat{border:1px solid #ccc;height:300px;overflow:auto;padding:10px}</style>
</head><body><h2>Mi Asistente IA</h2><div id="chat"></div><input id="msg" placeholder="Escribe..." style="width:80%"><button onclick="send()">Enviar</button>
<script>async function send(){let m=document.getElementById('msg').value;let c=document.getElementById('chat');c.innerHTML+='<p><b>Tu:</b> '+m+'</p>';let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:m})});let d=await r.json();c.innerHTML+='<p><b>IA:</b> '+d.reply+'</p>';document.getElementById('msg').value='';}</script></body></html>"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return jsonify({'reply': 'Falta poner GEMINI_API_KEY en Vercel'})
        client = genai.Client(api_key=api_key)
        data = request.get_json()
        msg = data.get('message','Hola')
        resp = client.models.generate_content(model='gemini-3.8-flash', contents=msg)
        return jsonify({'reply': resp.text})
    except Exception as e:
        return jsonify({'reply': f'Error: {str(e)}'})

if __name__ == '__main__':
    app.run() 
