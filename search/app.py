#importiamo le librerie
import os
import openai
from dotenv import load_dotenv
import pandas as pd
import numpy as np
from openai.embeddings_utils import distances_from_embeddings

#prendiamo la chiave nel file env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
'''
df = pd.read_json('training.json')

df['embeddings'] = df.text.apply(lambda x: openai.Embedding.create(input=x, engine='text-embedding-ada-002')['data'][0]['embedding'])

df.to_csv('output/embeddings.csv')
df.head()
'''
df = pd.read_csv('output/embeddings.csv')
df['embeddings'] = df['embeddings'].apply(eval).apply(np.array)

def create_context(
    question, df, max_len=1800, size="ada"
):
    """
    Create a context for a question by finding the most similar context from the dataframe
    """

    # Get the embeddings for the question
    q_embeddings = openai.Embedding.create(input=question, engine='text-embedding-ada-002')['data'][0]['embedding']

    # Get the distances from the embeddings
    df['distances'] = distances_from_embeddings(q_embeddings, df['embeddings'].values, distance_metric='cosine')


    returns = []

    # Sort by distance and add the text to the context until the context is too long
    for i, row in df.sort_values('distances', ascending=True).iterrows():
        
        # Else add it to the text that is being returned
        returns.append(row["text"])

    # Return the context
    return "\n\n###\n\n".join(returns)

def answer_question(
    df,
    model="text-davinci-003",
    question="",
    max_len=1800,
    size="ada",
    debug=False,
    max_tokens=50,
    stop_sequence=None
):
    """
    Answer a question based on the most similar context from the dataframe texts
    """
    context = create_context(
        question,
        df,
        max_len=max_len,
        size=size,
    )
    # If debug, print the raw model response
    if debug:
        print("Context:\n" + context)
        print("\n\n")

    try:
        # Create a completions using the question and context
        response = openai.Completion.create(
            prompt=f"Answer the question based on the context below, and if the question can't be answered based on the context, say \"I don't know\"\n\nContext: {context}\n\n---\n\nQuestion: {question}\nAnswer:",
            temperature=0,
            max_tokens=max_tokens,
            model=model
        )
        print(response)
        return response["choices"][0]["text"].strip()

    except Exception as e:
        print(e)
        return ""


#print(answer_question(df, question="cos'è il calcio"))
print(answer_question(df, question=input('cerca: ')))