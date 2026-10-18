import os
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mi Asistente IA</title>
<style>
body { font-family: Arial; background:#101114; color:white; padding:20px; }
h1 { color:#b9a0ff; }
#chat { max-width:600px; margin:auto; }
textarea { width:100%; box-sizing:border-box; padding:12px; border-radius:10px; }
button { padding:12px; background:#9a7bff; border:0; border-radius:10px; margin-top:8px; }
#respuesta { white-space:pre-wrap; margin-top:20px; }
</style>
</head>
<body>
<div id="chat">
<h1>Mi Asistente IA</h1>
<p>¡Hola! Soy tu asistente personal. ¿En qué te ayudo?</p>
<textarea id="mensaje" rows="4" placeholder="Escribe tu mensaje..."></textarea>
<button onclick="enviar()">Enviar</button>
<div id="respuesta"></div>
</div>
<script>
async function enviar() {
 const m = document.getElementById('mensaje');
 const r = document.getElementById('respuesta');
 if (!m.value.trim()) return;
 r.textContent = 'Pensando...';
 try {
  const res = await fetch('/chat', {
   method:'POST',
   headers:{'Content-Type':'application/json'},
   body:JSON.stringify({mensaje:m.value})
  });
  const data = await res.json();
  r.textContent = data.respuesta || data.error || 'Error desconocido';
 } catch(e) { r.textContent = 'No se pudo conectar.'; }
}
</script>
</body>
</html>
"""

@app.route("/")
def inicio():
    return render_template_string(HTML)

@app.route("/chat", methods=["POST"])
def chat():
    mensaje = request.json.get("mensaje", "").strip()
    if not mensaje:
        return jsonify({"error": "Escribe un mensaje"}), 400

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return jsonify({"error": "Falta configurar la clave de Claude en el servidor."}), 500

    import anthropic
    cliente = anthropic.Anthropic(api_key=api_key)
    respuesta = cliente.messages.create(
        model="claude-3-5-haiku-latest",
        max_tokens=800,
        messages=[{"role": "user", "content": mensaje}]
    )
    return jsonify({"respuesta": respuesta.content[0].text})

if __name__ == "__main__":
    app.run()
