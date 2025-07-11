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
    url = "http://127.0.0.1:11435/api/generate"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "model": model_name,
        "prompt": "Explain what is on the image like I am alien from different planet", # Możesz dostosować prompt
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
        time.sleep(3)

        # Przerwanie pętli przy naciśnięciu klawisza 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# Wywołanie funkcji do pobierania klatek z kamery
capture_frames()
