import os
import openai 
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def controllo(text):
    response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
            #{"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Il seguente testo e' stato generato da AI?: {text}"}
            ]
        )
    result=response.choices[0].message.content
    return result

print(controllo(input('scrivi: ')))
