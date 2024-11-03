import openai
from zenml import step
from typing import List, Dict

@step
def generate_embeddings(
    documents: List[Dict],
) -> List[Dict]:
    for document in documents:
        document['embedding'] = get_embedding(document['content'])
    return documents

def get_embedding(text: str) -> List[float]:
    response = openai.Embedding.create(
        input=text,
        engine="text-embedding-ada-002"
    )
    return response['data'][0]['embedding'] 