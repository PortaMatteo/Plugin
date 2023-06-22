import numpy as np
import openai
from pypdf import PdfReader
from redis.commands.search.field import TextField, VectorField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query
import requests 
from bs4 import BeautifulSoup
import re
import redis

INDEX_NAME = "embeddings-index"           # name of the search index
PREFIX = "doc"                            # prefix for the document keys
# distance metric for the vectors (ex. COSINE, IP, L2)
DISTANCE_METRIC = "COSINE"

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_PASSWORD = "" 

class DataService():

    def __init__(self):
        # Connect to Redis
        self.redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD
        )

    def drop_redis_data(self, index_name: str = INDEX_NAME):
        try:
            self.redis_client.flushdb()
            print('Index dropped')
        except:
            # Index doees not exist
            print('Index does not exist')

    def load_data_to_redis(self, embeddings):
        # Constants
        vector_dim = len(embeddings[0]['vector'])  # length of the vectors
        
		# Initial number of vectors
        vector_number = len(embeddings)

        # Define RediSearch fields
        text = TextField(name="text")
        text_embedding = VectorField("vector",
                                     "FLAT", {
                                         "TYPE": "FLOAT32",
                                         "DIM": vector_dim,
                                         "DISTANCE_METRIC": "COSINE",
                                         "INITIAL_CAP": vector_number,
                                     }
                                     )
        fields = [text, text_embedding]

        # Check if index exists
        try:
            self.redis_client.ft(INDEX_NAME).info()
            print("Index already exists")
            n_keys = self.redis_client.info()['db0']['keys']
        except:
            # Create RediSearch Index
            self.redis_client.ft(INDEX_NAME).create_index(
                fields=fields,
                definition=IndexDefinition(
                    prefix=[PREFIX], index_type=IndexType.HASH)
            )
            n_keys = 0
        
        for embedding in embeddings:
            key = f"{PREFIX}:{str(embedding['id'] + n_keys)}"
            embedding["vector"] = np.array(
                embedding["vector"], dtype=np.float32).tobytes()
            self.redis_client.hset(key, mapping=embedding)
        print(
            f"Loaded {self.redis_client.info()['db0']['keys']} documents in Redis search index with name: {INDEX_NAME}")


    def remove_newlines(self,text):
        text = open(text, "r", encoding="UTF-8").read()
        text = text.replace('\n', ' ')
        text = text.replace('\\n', ' ')
        text = text.replace('  ', ' ')
        text = text.replace('  ', ' ')
        return text



    def pdf_to_embeddings(self, pdf_path: str, chunk_length: int = 550):
        # Read data from pdf file and split it into chunks
        reader = PdfReader(pdf_path)
        chunks = []
        for page in reader.pages:
            text_page = page.extract_text()
            chunks.extend([text_page[i:i+chunk_length].replace('\n', '')
                          for i in range(0, len(text_page), chunk_length)])

        # Create embeddings
        response = openai.Embedding.create(
            model='text-embedding-ada-002', input=chunks)
        print([value['index'] for value in response['data']])
        return [{'id': value['index'], 'vector':value['embedding'], 'text':chunks[value['index']]} for value in response['data']]

    def txt_to_embeddings(self, text, chunk_length: int = 250):
        # Read data from pdf file and split it into chunks
        text = open(text, "r")
        text = text.read()

        chunks = []
        
        chunks.extend([text[i:i+chunk_length].replace('\n', '')
                       for i in range(0, len(text), chunk_length)])

        # Create embeddings
        response = openai.Embedding.create(
            model='text-embedding-ada-002', input=chunks)
        return [{'id': value['index'], 'vector':value['embedding'], 'text':chunks[value['index']]} for value in response['data']]
    
    def url_to_embeddings(self, url, chunk_length: int = 250):
        # Read data from pdf file and split it into chunks

        def format_url(testo):
            pattern = r"<.*?>"  # Pattern per cercare "<" seguito da qualsiasi carattere, incluso il newline, fino a ">"
            testo_senza_angolari = re.sub(pattern, "", testo)  # Rimuovi i match del pattern dal testo
            return testo_senza_angolari




        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        body = soup.find('body')
        content = str(soup.find_all("p"))
    
        text = format_url(content)


        chunks = []
        
        chunks.extend([text[i:i+chunk_length].replace('\n', '')
                       for i in range(0, len(text), chunk_length)])

        # Create embeddings
        response = openai.Embedding.create(
            model='text-embedding-ada-002', input=chunks)
        return [{'id': value['index'], 'vector':value['embedding'], 'text':chunks[value['index']]} for value in response['data']]

    def search_redis(self,
                     user_query: str,
                     index_name: str = "embeddings-index",
                     vector_field: str = "vector",
                     return_fields: list = ["text", "vector_score"],
                     hybrid_fields="*",
                     k: int = 20,
                     print_results: bool = False,
                     ):
        # Creates embedding vector from user query
        embedded_query = openai.Embedding.create(input=user_query,
                                                 model="text-embedding-ada-002",
                                                 )["data"][0]['embedding']
        # Prepare the Query
        base_query = f'{hybrid_fields}=>[KNN {k} @{vector_field} $vector AS vector_score]'
        query = (
            Query(base_query)
            .return_fields(*return_fields)
            .sort_by("vector_score")
            .paging(0, k)
            .dialect(2)
        )
        params_dict = {"vector": np.array(
            embedded_query).astype(dtype=np.float32).tobytes()}
        # perform vector search
        results = self.redis_client.ft(index_name).search(query, params_dict)
        if print_results:
            for i, doc in enumerate(results.docs):
                score = 1 - float(doc.vector_score)
                print(f"{i}. {doc.text} (Score: {round(score ,3) })")
        return [doc['text'] for doc in results.docs]