#importiamo le librerie
import os
import openai
from dotenv import load_dotenv

#prendiamo la chiave nel file env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


# creiamo la funzione che riportera' la risposta
def risposta(text):
    
    response = openai.Completion.create(
            model="text-davinci-003", #modello che utilizziamo, in questo caso un modello testuale.
            prompt=text, #indichiamo quel'e' la domanda che richiediamo venga risposta.
            max_tokens=30, #impostiamo il massimo di token utilizzabili per la risposta, notiamo che ogni richiesta somma anche il numero di token della domanda.
            temperature=0.6, # Impostiamo la precisione della risposta il valore va da 0 a 1 (0 preciso, 1 "creativo").
        )
    result=response.choices[0].text #andiamo a prendere nella risposta del modello solo il testo della risposta.
    return result

text = input("Chiedi: ")
print(risposta(text))