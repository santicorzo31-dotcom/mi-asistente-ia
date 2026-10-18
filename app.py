from flask import Flask, request, jsonify
import os
import requests
import json

# Inicializar la app de Flask
app = Flask(__name__)

# =======================
# HTML DE SAM - DISEÑO VERDE
# =======================
HTML_PAGE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SAM - Asistente de Santi</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: system-ui, -apple-system, sans-serif; }
        body { background: #f5f5f5; display: flex; flex-direction: column; height: 100vh; }
        header { background: #0f3d1f; color: #a7f3d0; padding: 18px; text-align: center; font-weight: 700; font-size: 22px; letter-spacing: 1px; }
        #chat { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 12px; }
        .msg { padding: 14px 18px; border-radius: 20px; max-width: 85%; line-height: 1.5; word-wrap: break-word; font-size: 15px; }
        .bot { background: #14532d; color: white; align-self: flex-start; border-bottom-left-radius: 6px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .user { background: #dcfce7; color: #14532d; align-self: flex-end; border-bottom-right-radius: 6px; font-weight: 500; }
        #bar { background: white; padding: 12px; display: flex; gap: 10px; align-items: center; border-top: 1px solid #e5e5e5; }
        .icon-btn { background: #f0f0f0; border: 0; width: 44px; height: 44px; border-radius: 50%; font-size: 20px; cursor: pointer; }
        #input { flex: 1; background: #f5f5f5; border: 1px solid #e5e5e5; padding: 14px 18px; border-radius: 30px; outline: none; font-size: 16px; }
        #input:focus { border-color: #14532d; background: white; }
        #send { background: #14532d; color: white; border: 0; width: 50px; height: 50px; border-radius: 50%; font-size: 20px; cursor: pointer; }
        #send:active { transform: scale(0.95); }
        .loading { opacity: 0.7; font-style: italic; }
    </style>
</head>
<body>
    <header>🌿 SAM 👽 - Tu Asistente IA</header>
    
    <div id="chat">
        <div class="msg bot">Hola Santi, ya quedé 🙏 Elegante y rápido. ¿En qué te ayudo hoy?</div>
    </div>
    
    <div id="bar">
        <button class="icon-btn" title="Cámara">📷</button>
        <button class="icon-btn" title="Imagen">🖼️</button>
        <button class="icon-btn" title="Voz">🎤</button>
        <input id="input" placeholder="Escribe tu mensaje..." autocomplete="off">
        <button id="send" onclick="sendMessage()">➤</button>
    </div>

    <script>
        const chatContainer = document.getElementById('chat');
        const messageInput = document.getElementById('input');

        async function sendMessage() {
            const text = messageInput.value.trim();
            if (!text) return;

            // Mostrar mensaje del usuario
            chatContainer.innerHTML += `<div class="msg user">${text}</div>`;
            messageInput.value = '';
            chatContainer.scrollTop = chatContainer.scrollHeight;

            // Mostrar cargando
            const loadingId = 'loading-' + Date.now();
            chatContainer.innerHTML += `<div class="msg bot loading" id="${loadingId}">SAM está escribiendo...</div>`;
            chatContainer.scrollTop = chatContainer.scrollHeight;

            try {
                // Llamar a nuestro backend /chat
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });

                const data = await response.json();
                
                // Quitar cargando y mostrar respuesta
                document.getElementById(loadingId).remove();
                const formattedReply = data.reply.replace(/\\n/g, '<br>');
                chatContainer.innerHTML += `<div class="msg bot">${formattedReply}</div>';

            } catch (error) {
                document.getElementById(loadingId).remove();
                chatContainer.innerHTML += `<div class="msg bot">❌ Error de conexión, reintenta Santi</div>`;
                console.error(error);
            }
            
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        // Enviar con Enter
        messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>
"""

# Ruta principal que muestra el chat
@app.route('/')
def home():
    return HTML_PAGE

# Ruta del API que habla con Gemini
@app.route('/chat', methods=['POST'])
def chat_api():
    try:
        # Obtener mensaje del usuario
        body = request.get_json()
        user_prompt = body.get('message', '') if body else ''

        if not user_prompt:
            return jsonify({'reply': 'Escribe algo Santi'})

        # Leer la API KEY de Vercel
        api_key = os.environ.get('GEMINI_API_KEY')

        if not api_key:
            return jsonify({'reply': '❌ No hay GEMINI_API_KEY configurada en Vercel > Settings > Environment Variables'})

        # URL del modelo nuevo que sí funciona en 2026
        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

        # Payload para Gemini
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"Eres SAM, el asistente personal de Santi. Eres amigable, corto, útil y hablas en español. Responde a: {user_prompt}"
                        }
                    ]
                }
            ]
        }

        # Hacer la petición a Google
        response = requests.post(gemini_url, json=payload, timeout=30)
        result = response.json()

        # Si hay respuesta, devolverla
        if 'candidates' in result and len(result['candidates']) > 0:
            text_reply = result['candidates'][0]['content']['parts'][0]['text']
            return jsonify({'reply': text_reply})
        else:
            # Si hay error, mostrar cual es
            error_text = json.dumps(result)[:800]
            print(f"Error Gemini: {error_text}")

            if 'API_KEY_INVALID' in error_text:
                return jsonify({'reply': '❌ Tu API KEY es inválida. Ve a aistudio.google.com/apikey y crea otra nueva'})
            
            if 'QUOTA' in error_text or '429' in error_text:
                return jsonify({'reply': '❌ Se acabó la cuota gratis de Gemini, espera 1 minuto y reintenta'})

            return jsonify({'reply': f"Error de la API de Gemini: {error_text}"})

    except Exception as e:
        print(f"Error en servidor: {str(e)}")
        return jsonify({'reply': f"Error en el servidor: {str(e)}"})

# Para correr local
if __name__ == '__main__':
    app.run(debug=True) 
