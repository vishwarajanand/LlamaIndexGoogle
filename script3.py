from google.auth import default
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.vertex import VertexTextEmbedding
from llama_index.llms.vertex import Vertex
import os

credentials, project_id = default()

# Using Llamaindex's classes
embed_model = VertexTextEmbedding(
    model_name="textembedding-gecko@001",
    credentials=credentials,
)
llm = Vertex(model="gemini-pro", credentials=credentials)
# Settings.llm = Vertex(model="gemini-pro", credentials=credentials)

documents = SimpleDirectoryReader(".").load_data()
index = VectorStoreIndex.from_documents(
    documents,
    embed_model=embed_model,
)
query_engine = index.as_query_engine(llm)
retriever = index.as_retriever()
# Calls only embedding model to match nodes to query
nodes = retriever.retrieve("Fetches the contents")
print(nodes)
# Calls LLM over retrieved nodes
response = query_engine.query("Summarize the contents")
print(response)
