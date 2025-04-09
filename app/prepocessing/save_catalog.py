from qdrant_client import QdrantClient, models
import google.generativeai as genai
from config import QDRANT_URL, QDRANT_API_KEY, GEMINI_API_KEY
import uuid
import pandas as pd

#Intialize Qdrant client
qdrant_client = QdrantClient(
    url=QDRANT_URL,
    # prefer_grpc=True,
    api_key=QDRANT_API_KEY
)

# Initialize embedding model here
genai.configure(api_key=GEMINI_API_KEY)

def initialize_vector_store():
    
    try:
        if not qdrant_client.get_collections():
            raise ConnectionError("Failed to connect to Qdrant cluster")
        
        if not qdrant_client.collection_exists("rag_embeddings"):
            qdrant_client.create_collection(
                collection_name="rag_embeddings",
                vectors_config=models.VectorParams(
                    size=768,  # Dimension for embedding model
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
            Name: {row['Name']}
            {row['Description']}
            Duration: {row['Duration']} minutes
            Test type: {row['Test Type']}
        """
        embedding = genai.embed_content(
            model="models/text-embedding-004",
            content=embedding_text,
            task_type="retrieval_query"
        )['embedding']
        
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
csv_path = "app/data/shl_product_details.csv"  # Path to your CSV file
store_embeddings(csv_path)