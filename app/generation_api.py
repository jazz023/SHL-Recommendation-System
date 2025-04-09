import re
from fastapi import FastAPI, status
from pydantic import BaseModel
from groq import Groq
from config import GROQ_API_KEY
from retrieval import retrieve_from_qdrant
from fastapi.responses import JSONResponse
import json

app = FastAPI()
groq_client = Groq(api_key=GROQ_API_KEY)

class RecommendationRequest(BaseModel):
    query: str
    max_duration: int = None
    test_type: str = None
    
class IndentedJSONResponse(JSONResponse):
    def render(self, content: any) -> bytes:
        return json.dumps(
            content,
            indent=4,
            ensure_ascii=False,
            default=str  # Handle non-serializable types
        ).encode("utf-8")

def llm_rerank(query: str, candidates: list) -> list:
    
    messages = [{
    "role": "system",
    "content": (
        "You are a reranking assistant for assessments. Follow these rules strictly:\n"
        "1. Return ONLY assessment NAMES wrapped in || (e.g., ||Java Coding Test||)\n"
        "2. List exactly 10 names in relevance order\n"
        "3. Never add explanations or formatting\n"
        "4. Use ONLY these delimiters: ||\n"
        "5. Never use markdown\n"
        "6. Maintain exact spelling from context\n"
        "Example response:\n"
        "||Assessment 1||\n||Assessment 2||\n..."
    )
    }, {
        "role": "user", 
        "content": (
            f"Reorder these assessments for '{query}':\n" +
            '\n'.join([
                f"Assessment {i+1}:\n"
                f"Name: {c['name']}\n"
                f"Context: {c['description']}\n"
                f"Duration: {c['duration']} mins\n"
                f"Test Type: {c['test_type']}\n"
                f"Remote Testing: {c['remote_testing']}\n"
                f"Adaptive Support: {c['adaptive_support']}\n"
                for i, c in enumerate(candidates)
            ]) +
            "\nReturn only the top 10 sorted names."
        )
    }]
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.3
        )
        
        content = response.choices[0].message.content
        
        matches = re.findall(r'\|\|(.*?)\|\|', content)
        
        # Robust parsing
        if not matches:
            matches = re.findall(r'\d+\.\s+(.*?)(?:\s*-|\(|$)', content)
        if not matches:
            matches = re.findall(r'-\s+(.*?)(?:\s*-|\(|$)', content)    

        ranked_names = [name.strip() for name in matches if name.strip()]
        
        if len(ranked_names) < 10:
            missing = 10 - len(ranked_names)
            ranked_names += [c['name'] for c in candidates if c['name'] not in ranked_names][:missing]
        
        # Create name-to-candidate mapping
        candidate_map = {c['name'].lower().strip(): c for c in candidates}
        
        # Convert ranked_names to candidate dictionaries
        ranked = []
        for name in ranked_names:
            # Exact match
            clean_name = name.lower().strip()
            if clean_name in candidate_map:
                ranked.append(candidate_map[clean_name])
                continue
                
            # Partial match fallback
            for cname, candidate in candidate_map.items():
                if clean_name in cname or cname in clean_name:
                    ranked.append(candidate)
                    break
        
            
        # Ensure exactly 10 items
        return (ranked + [c for c in candidates if c not in ranked])[:10]

    except Exception as e:
        print(f"LLM Error: {str(e)}")
        return candidates[:10]  # Fallback mechanism
    
def parse_duration(duration) -> int | None:
    try:
        # Direct integer conversion
        return int(duration)
    except (TypeError, ValueError):
        # Extract first numeric sequence from strings
        if match := re.search(r'\d+', str(duration)):
            return int(match.group())
    return None

@app.get("/", response_class=IndentedJSONResponse)
async def root():
    return {
        "message": "SHL Assessment Recommender API is running",
        "endpoints": [
            {"path": "/health", "method": "GET", 
             "description": "Health check endpoint"},
            {"path": "/recommend", "method": "POST", 
             "description": "Get assessment recommendations based on a Natural Language query"}
        ],
        "version": "1.0.0"
    }


@app.get("/health", response_class=IndentedJSONResponse)
async def health_check():
    return JSONResponse(
        content={"status": "healthy"},
        status_code=200,
        media_type="application/json"
    )

@app.post("/recommend", response_class=IndentedJSONResponse)
async def recommend(request: RecommendationRequest):
    try:
        candidates = retrieve_from_qdrant(request.query, top_k=20)
        
        # Apply filters
        if request.max_duration:    
            candidates = [c for c in candidates 
                         if int(c.get('duration', 0)) <= request.max_duration]

        # LLM reranking
        ranked = llm_rerank(request.query, candidates)
        
        return JSONResponse(
            content={
                "recommended_assessments": [{
                    "url": c["url"],
                    "adaptive_support": c["adaptive_support"],
                    "description": c["description"],
                    "duration": parse_duration(c.get('duration')),
                    "remote_support": c["remote_testing"],
                    "test_type": [ct.strip() for ct in c["test_type"].split(",")]
                } for c in ranked[:10]]
            },
            status_code=status.HTTP_200_OK,
            media_type="application/json"
        )
        
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )