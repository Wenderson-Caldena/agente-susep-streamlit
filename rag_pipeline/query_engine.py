import os
import pickle
import faiss
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
import httpx

# OpenAI client com SSL desabilitado (ambiente local)
load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    http_client=httpx.Client(verify=False)
)

# Caminhos
INDEX_DIR = "embeddings/faiss_index"
INDEX_FILE = os.path.join(INDEX_DIR, "faiss.index")
METADATA_FILE = os.path.join(INDEX_DIR, "metadata.pkl")

# Load dos dados
def load_faiss_and_metadata():
    index = faiss.read_index(INDEX_FILE)
    with open(METADATA_FILE, "rb") as f:
        metadata = pickle.load(f)
    return index, metadata

# Embedding da pergunta
def embed_question(question: str):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=question
    )
    return np.array(response.data[0].embedding).reshape(1, -1).astype("float32")

def query_rag(question: str, top_k: int = 5) -> str:
    index, metadata = load_faiss_and_metadata()
    question_vec = embed_question(question)

    distances, indices = index.search(question_vec, top_k)
    retrieved_chunks = [metadata[i] for i in indices[0]]

    context = ""
    for i, chunk in enumerate(retrieved_chunks, 1):
        context += f"[Trecho {i}]\n"
        context += f"Seção: {chunk['section']}\n"
        context += f"Subseção: {chunk['subsection']}\n"
        context += f"Artigo: {chunk['article']}\n"
        context += f"Texto:\n{chunk['text']}\n\n"

    context = context[:24000]  # Limite de contexto

    prompt = f"""Você é um assistente especializado em regulação da SUSEP.

Sua tarefa é responder com base **somente** nos trechos fornecidos abaixo, extraídos da Circular SUSEP 648.

Para cada pergunta, procure identificar:
- Artigos relevantes
- Seção/Subseção correspondentes
- Fórmulas ou conceitos aplicáveis

Caso não encontre a resposta, diga que não há informação suficiente nos trechos apresentados.

Trechos:
\"\"\"
{context}
\"\"\"

Pergunta: {question}
Resposta:
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    print("❓ Digite sua pergunta sobre a Circular SUSEP 648:")
    question = input("> ")
    resposta = query_rag(question)
    print("\n💬 Resposta da IA:\n")
    print(resposta)
