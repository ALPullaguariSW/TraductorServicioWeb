from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
from googletrans import Translator
import pyttsx3  # Para síntesis de voz

app = Flask(__name__)

# Configurar el traductor
translator = Translator()

# Configurar el reconocedor de voz
recognizer = sr.Recognizer()

# Configurar el motor de síntesis de voz
engine = pyttsx3.init()

# Configurar las propiedades de la voz
engine.setProperty('rate', 150)  # Velocidad de la voz
engine.setProperty('volume', 1)  # Volumen de la voz

# Cambiar a una voz más amigable si está disponible
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # Cambiar la voz, si hay varias opciones

# Idiomas soportados (puedes agregar más idiomas si lo deseas)
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
    engine.say(text)
    engine.runAndWait()

# Función principal para escuchar y traducir
def listen_and_translate(target_language='es'):  # Escuchar siempre activado
    try:
        print("Escuchando... Di algo.")
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)  # Ajusta la sensibilidad
            audio = recognizer.listen(source)

        print("Reconociendo...")
        # Reconocimiento de voz (en varios idiomas)
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
        
        return translated_text  # Retornamos la traducción para usar en la respuesta web

    except sr.UnknownValueError:
        print("No se entendió lo que dijiste, por favor repite.")
        return "No se entendió lo que dijiste, por favor repite."
    except sr.RequestError:
        print("Error de servicio; por favor intente más tarde.")
        return "Error de servicio; por favor intente más tarde."
    except Exception as e:
        print(f"Error: {e}")
        return f"Error: {e}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/listen', methods=['POST'])
def listen_and_translate_api():
    target_language = request.json['target_language']
    translated_text = listen_and_translate(target_language)
    return jsonify({"translated_text": translated_text})

if __name__ == "__main__":
    app.run(debug=True)
