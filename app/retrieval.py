from qdrant_client import QdrantClient
import google.generativeai as genai
from config import QDRANT_URL, QDRANT_API_KEY, GEMINI_API_KEY

# Initialize Gemini client
genai.configure(api_key=GEMINI_API_KEY)

#Intialize Qdrant client
qdrant_client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)

def retrieve_from_qdrant(query: str, top_k: int = 30):
    
    if not qdrant_client:
        raise RuntimeError("Qdrant client not initialized")
    
    try:
        # Single embedding
        query_embedding = genai.embed_content(
            model="models/text-embedding-004",
            content=query,
            task_type="retrieval_query"
        )['embedding']  # Use singular key
        
        # Perform search
        results = qdrant_client.search(
            collection_name="rag_embeddings",
            query_vector=query_embedding,
            limit=top_k
        )
        
        return [hit.payload for hit in results]
    
    except Exception as e:
        print(f"Retrieval failed: {str(e)}")
        return []