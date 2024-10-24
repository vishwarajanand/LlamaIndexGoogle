from google.auth import default
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
)

from llama_index.embeddings.vertex import VertexTextEmbedding
from llama_index.llms.vertex import Vertex
from llama_index.vector_stores.postgres import PGVectorStore
import asyncpg  # type: ignore
from google.cloud.alloydb.connector import AsyncConnector, IPTypes
import pg8000
from google.cloud.alloydb.connector import Connector

credentials, project_id = default()


# Using Llamaindex's classes
embed_model = VertexTextEmbedding(
    model_name="textembedding-gecko@001",
    credentials=credentials,
)
llm = Vertex(model="gemini-pro", credentials=credentials)


class settings:
    project_id = "#######"  # @param {type:"string"}
    region = "#######"  # @param {type:"string"}
    cluster_name = "#######"  # @param {type:"string"}
    instance_name = "#######"  # @param {type:"string"}
    database_name = "postgres"  # @param {type:"string"}
    table_name = "products"  # @param {type:"string"}
    user = "postgres"  # @param {type:"string"}
    password = "#######"  # input("Please provide a password to be used for 'postgres' database user: ")


async def getAsyncConn() -> asyncpg.Connection:
    conn = await AsyncConnector().connect(  # type: ignore
        f"projects/{settings.project_id}/locations/{settings.region}/clusters/{settings.cluster_name}/instances/{settings.instance_name}",
        "asyncpg",
        user=settings.user,
        password=settings.password,
        db=settings.database_name,
        enable_iam_auth=False,  # maybe needs to be disabled???
    )
    return conn


def getSyncConn() -> pg8000.dbapi.Connection:
    connector = Connector()
    conn: pg8000.dbapi.Connection = connector.connect(
        f"projects/{settings.project_id}/locations/{settings.region}/clusters/{settings.cluster_name}/instances/{settings.instance_name}",
        "pg8000",
        user=settings.user,
        password=settings.password,
        db=settings.database_name,
        ip_type=IPTypes.PUBLIC,
        enable_iam_auth=True,
    )
    return conn


vector_store = PGVectorStore.from_params(
    connection_string="postgresql+pg8000://",
    async_connection_string="postgresql+asyncpg://",
    # Note: Needed changes in LlamaIndex's PGVectorStore implementation:
    # Provide different create_engine_kwargs for create_engine and create_asyncengine:
    # **self.create_engine_kwargs --> ["not_sync"] OR ["sync"] respectively
    create_engine_kwargs={
        "sync": {"creator": getSyncConn},
        "not_sync": {"async_creator": getAsyncConn},
        # "async_creator": getAsyncConn,
    },
    # table_name=settings.table_name,
    embed_dim=768,
    # hnsw_kwargs={
    #     "hnsw_m": 16,
    #     "hnsw_ef_construction": 64,
    #     "hnsw_ef_search": 40,
    #     "hnsw_dist_method": "vector_cosine_ops",
    # },
)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
documents = SimpleDirectoryReader(".").load_data()

# index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

index = VectorStoreIndex.from_documents(
    documents,
    embed_model=embed_model,
    storage_context=storage_context,
    show_progress=True,
)
query_engine = index.as_query_engine(llm)

retriever = index.as_retriever()
# Calls only embedding model to match nodes to query
nodes = retriever.retrieve("Fetches the contents")
print(nodes)
# Calls LLM over retrieved nodes
response = query_engine.query("Summarize the contents")
print(response)
