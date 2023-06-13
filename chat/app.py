#importiamo le librerie
import os
import openai
from dotenv import load_dotenv

#prendiamo la chiave nel file env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


# creiamo la funzione che riportera' la risposta
def risposta(text):
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                #{"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Who won the world series in 2020?"}
            ]
        )
    result=response.choices[0].message.content #andiamo a prendere nella risposta del modello solo il testo della risposta.
    return result

text = input("Chiedi: ")
print(risposta(text))