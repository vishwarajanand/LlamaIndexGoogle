from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings

from langchain_google_vertexai import VertexAIEmbeddings
from langchain_google_vertexai import ChatVertexAI, VertexAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os

PROJECT_ID = os.getenv("PROJECT_ID")


# Either of the below works
Settings.embed_model = GoogleGenerativeAIEmbeddings(
    # Needs GOOGLE_API_KEY env var set
    model="models/embedding-001"
)
Settings.embed_model = VertexAIEmbeddings(
    model_name="textembedding-gecko@001", project=PROJECT_ID
)


# Either of the below works
Settings.llm = VertexAI(model_name="gemini-pro")
Settings.llm = ChatVertexAI(model_name="gemini-pro")

documents = SimpleDirectoryReader(".").load_data()

index = VectorStoreIndex.from_documents(
    documents,
)

query_engine = index.as_query_engine()
response = query_engine.query("Summarize the contents")
print(response)
