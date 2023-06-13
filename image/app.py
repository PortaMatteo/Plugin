import os
import openai
from dotenv import load_dotenv

#prendiamo la chiave nel file env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


# creiamo la funzione che riportera' la risposta
def risposta(text):
    
    response = openai.Image.create(
        prompt=text,
        n=1,
        size="1024x1024"
    )
    print(response)
    image_url = response['data'][0]['url'] #andiamo a prendere nella risposta del modello solo il testo della risposta.
    return image_url

text = input("Chiedi: ")
print(risposta(text))

