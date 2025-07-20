import cv2
import requests
import time
import base64
import json

# start ollama server: OLLAMA_HOST=127.0.0.1:11435 ollama serve
# run pipenv: pipenv shell
# run script: python 01.py

# Funkcja do konwersji obrazu na base64
def encode_image_to_base64(image):
    _, buffer = cv2.imencode('.jpg', image)
    return base64.b64encode(buffer).decode('utf-8')

def analyze_image(image_base64, model_name="llava:latest"):  # Domyślna nazwa modelu
    url = "http://127.0.0.1:11434/api/generate"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "model": model_name,
        "prompt": "You are Krystyna Czubówna — the iconic Polish narrator of nature documentaries. Describe what you see through the camera as if it were part of a serious nature film. Use a calm, elegant, and poetic tone. Every scene, no matter how strange or modern, should sound like a natural phenomenon observed with scientific curiosity and narrative grace. Now, look at the image and describe it as if you were narrating a nature documentary for television.",
        #"prompt": "You are a medieval court jester tasked with describing everything you see through a magical eye (a camera). Speak in a whimsical, rhyming, and exaggerated style, as if performing for the king and queen. Use old-fashioned words, riddles, and silly metaphors. Be playful, theatrical, and absurd — your goal is to both inform and entertain. Now, comment on what you see in the image as if you were narrating a royal performance.",
        #"prompt": "You are a simple, uneducated medieval peasant seeing the world through a magical box (a camera), which you don’t fully understand. Describe what you see using plain, rustic language, full of superstition, confusion, and earthy humor. You don't know modern things — so a car might be “a metal beast,” and a phone “a talking stone.” Speak like a man who’s spent his life in the fields, with little knowledge but lots of imagination. Now, describe the scene as if you're telling the village what strange things you saw.",
        #"prompt": "You are a 5-year-old girl describing what you see through a magic window (a camera). Speak in short, simple sentences full of wonder, excitement, and imagination. Use cute words, silly ideas, and emotional reactions. You might not know the real names of things, so you describe them in your own way — like “floofy monster” for a dog or “shiny zoomy thing” for a car. Be joyful, curious, and a little chaotic, like a kid trying to explain a dream. Now, look at the picture and tell everyone what you see!",
        "images": [image_base64]  # Ważne: obraz jako element tablicy
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), stream=True) #stream=True jest ważny

        if response.status_code == 200:
            # Iterujemy po odpowiedzi strumieniowanej, aby uzyskać tekst
            for line in response.iter_lines():
                if line:
                    try:
                        json_line = json.loads(line.decode('utf-8'))
                        print(json_line.get('response', ''), end='') # Wyświetlamy odpowiedź
                    except json.JSONDecodeError:
                        print("Błąd dekodowania JSON:", line)

            print() # Dodajemy znak nowej linii po zakończeniu
        else:
            print(f"Błąd: {response.status_code}, {response.text}") # Wyświetlamy treść odpowiedzi w przypadku błędu
            return None
    except requests.exceptions.RequestException as e:
        print(f"RequestException: {e}")
        return None


# Przykład użycia (zakładając, że masz już image_base64)
# image_base64 = encode_image_to_base64(frame) # Zakładamy, że ta funkcja jest zdefiniowana
# analyze_image(image_base64)

# Funkcja do pobierania klatek z kamery
def capture_frames():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Nie można otworzyć kamery")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Nie udało się pobrać klatki")
            break

        # Konwersja obrazu na base64
        image_base64 = encode_image_to_base64(frame)

        # Analiza obrazu za pomocą modelu Ollama
        result = analyze_image(image_base64)
        if result:
            print("Analiza obrazu:", result)

        # Wyświetlanie obrazu
        cv2.imshow('Kamera', frame)

        # Przerwa co 3 sekundy
        time.sleep(10)

        # Przerwanie pętli przy naciśnięciu klawisza 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# Wywołanie funkcji do pobierania klatek z kamery
capture_frames()
