import os
from flask import Flask, request, jsonify, render_template_string
from google import genai

app = Flask(__name__)

HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mi Asistente IA</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
<style>
body{margin:0;font-family:-apple-system,sans-serif;background:#0f3d20;min-height:100vh;display:flex;flex-direction:column}
.header{background:#0a2e18;padding:15px;text-align:center} .header h1{margin:0;color:#a7f3d0;font-size:22px}
#chat{max-width:700px;width:100%;margin:20px auto;background:white;border-radius:20px;display:flex;flex-direction:column;overflow:hidden;height:78vh;box-shadow:0 10px 40px rgba(0,0,0,0.3)}
#messages{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:12px;background:white}
.msg{max-width:85%;padding:12px 16px;border-radius:18px;line-height:1.5}
.user{align-self:flex-end;background:#bbf7d0;color:#052e16;border-bottom-right-radius:4px}
.ia{align-self:flex-start;background:#14532d;color:white;border-bottom-left-radius:4px}
.input-area{display:flex;padding:15px;border-top:1px solid #eee;background:#f9fafb}
#msg{flex:1;padding:12px 16px;border:1px solid #bbf7d0;border-radius:25px;outline:none}
button{margin-left:10px;padding:12px 20px;background:#14532d;color:white;border:none;border-radius:25px;font-weight:bold}
</style></head><body>
<div class="header"><h1>🌿🙃😎😎 soy Sam - tu ayuda virtual</h1></div>
<div id="chat"><div id="messages"><div class="msg ia">Hola, ¿qué más? Soy tu asistente personal 😎<br><br>Tareas, cuentos, historia... tú dirás.</div></div>
<div class="input-area"><input id="msg" placeholder="Escribe tu pregunta..." onkeypress="if(event.key==='Enter')send()"><button onclick="send()">Enviar</button></div></div>
<script>
function renderMath(el){
 if(window.renderMathInElement){
   renderMathInElement(el,{delimiters:[{left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false},{left:'\\(',right:'\\)',display:false},{left:'\\[',right:'\\]',display:true}],throwOnError:false});
 }
}
async function send(){
 let input=document.getElementById('msg'); let text=input.value.trim(); if(!text) return;
 let box=document.getElementById('messages');
 box.innerHTML+=`<div class="msg user">${text}</div>`; input.value='';
 let tid='t'+Date.now(); box.innerHTML+=`<div id="${tid}" class="msg ia">Escribiendo... ⏳</div>`;
 box.scrollTop=box.scrollHeight;
 let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:text})});
 let d=
