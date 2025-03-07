import os
import speech_recognition as sr
from googletrans import Translator
import pyttsx3
from flask import Flask, render_template, request

# Inicializar Flask
app = Flask(__name__)

# Configuración del traductor
translator = Translator()

# Configuración del motor de síntesis de voz
engine = pyttsx3.init()

# Configuración del reconocedor de voz
recognizer = sr.Recognizer()

# Idiomas soportados
languages = {
    'en': 'English',
    'es': 'Español',
    'fr': 'Français',
    'de': 'Deutsch',
    'it': 'Italiano',
    'pt': 'Português',
    'ru': 'Русский',
    'ja': '日本語',
    'zh': '中文'
}

# Función para detectar el idioma del texto
def detect_language(text):
    detected = translator.detect(text)
    return detected.lang

# Función para sintetizar la voz
def speak(text, lang='es'):
    engine.setProperty('rate', 150)  # Velocidad de la voz
    engine.setProperty('volume', 1)  # Volumen
    engine.setProperty('voice', lang)  # Cambiar idioma de la voz
    engine.say(text)
    engine.runAndWait()

# Página principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para manejar la traducción
@app.route('/listen', methods=['POST'])
def listen_and_translate():
    target_language = request.form.get('language')  # El idioma de destino

    print("Escuchando... Di algo.")
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)  # Ajusta la sensibilidad
        audio = recognizer.listen(source)

        try:
            print("Reconociendo...")
            text = recognizer.recognize_google(audio, language='auto')  # auto detecta el idioma
            print(f"Texto detectado: {text}")
            
            # Detectar el idioma y traducirlo al idioma de destino
            detected_lang = detect_language(text)
            print(f"Idioma detectado: {languages.get(detected_lang, 'Desconocido')}")
            
            # Traducir el texto al idioma de destino (target_language)
            translation = translator.translate(text, src=detected_lang, dest=target_language)
            translated_text = translation.text
            print(f"Traducción al {languages.get(target_language, 'Desconocido')}: {translated_text}")
            
            # Sintetizar la traducción en voz
            speak(translated_text, target_language)
            
            return f"Traducción: {translated_text}"
        
        except sr.UnknownValueError:
            return "No se entendió lo que dijiste, por favor repite."
        except sr.RequestError:
            return "Error de servicio; por favor intente más tarde."
        except Exception as e:
            return f"Error: {e}"

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True)
