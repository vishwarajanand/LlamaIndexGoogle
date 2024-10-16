from google.auth import default
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.vertex import VertexTextEmbedding
from llama_index.llms.vertex import Vertex
import os

PROJECT_ID = os.getenv("PROJECT_ID")
REGION = "us-central1"

credentials, project_id = default()

# Using Llamaindex's classes
Settings.embed_model = VertexTextEmbedding(
    model_name="textembedding-gecko@001",
    credentials=credentials,
)
Settings.llm = Vertex(model="gemini-pro", credentials=credentials)

documents = SimpleDirectoryReader(".").load_data()
index = VectorStoreIndex.from_documents(
    documents,
)
query_engine = index.as_query_engine()
response = query_engine.query("Summarize the contents")
print(response)
