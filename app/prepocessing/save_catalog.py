from qdrant_client import QdrantClient, models
from llama_index.embeddings.ollama import OllamaEmbedding
from app.config import QDRANT_URL, QDRANT_API_KEY, OLLAMA_BASE_URL
import uuid
import pandas as pd

#Intialize Qdrant client
qdrant_client = QdrantClient(
    url=QDRANT_URL,
    prefer_grpc=True,
    api_key=QDRANT_API_KEY
)

# Initialize embedding model here
embed_model = OllamaEmbedding(  
    model_name="nomic-embed-text",
    base_url=OLLAMA_BASE_URL
)

def initialize_vector_store():
    
    try:
        if not qdrant_client.get_collections():
            raise ConnectionError("Failed to connect to Qdrant cluster")
        
        if not qdrant_client.collection_exists("rag_embeddings"):
            qdrant_client.create_collection(
                collection_name="rag_embeddings",
                vectors_config=models.VectorParams(
                    size=768,  # Dimension for nomic-embed-text
                    distance=models.Distance.COSINE
                )
            )
            print("Vector store initialized successfully")
        
    except Exception as e:
        print(f"Vector store initialization failed: {str(e)}")
        raise
    
def store_embeddings(csv_path: str, collection_name: str = "rag_embeddings"):
    
    # Read CSV data
    df = pd.read_csv(csv_path).fillna("")
    
    # Prepare points list
    points = []
    
    for _, row in df.iterrows():
        # Generate embedding
        embedding_text = \
        f"""
            Duration: {row['Duration']} minutes
            Test type: {row['Test Type']}
            Supported features- Remote-Testing:{row['Remote Testing']}, Adaptive/IRT-Support:{row['Adaptive/IRT Support']}
            {row['Description']}
        """
        embedding = embed_model.get_text_embedding(embedding_text)
        
        # Create payload with data
        payload = {
            "name": row["Name"],
            "url": row["URL"],
            "description": row["Description"],
            "remote_testing": row["Remote Testing"],
            "adaptive_support": row["Adaptive/IRT Support"],
            "duration": row["Duration"].split("=")[-1].strip() if row["Duration"] else "",
            "test_type": row["Test Type"]
        }
        
        # Create Qdrant point
        points.append(
            models.PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload=payload
        ))
    
    # Upsert to Qdrant
    qdrant_client.upsert(
        collection_name=collection_name,
        points=points
    )
    print(f"Successfully upserted {len(points)} embeddings")

# Initialize vector store
initialize_vector_store()

# Store embeddings from CSV
csv_path = "data/shl_product_details.csv"  # Path to your CSV file
store_embeddings(csv_path)