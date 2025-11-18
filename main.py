import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import base64
import requests

from database import create_document
from schemas import CoinAnalysis

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeResponse(BaseModel):
    id: str
    data: CoinAnalysis


@app.get("/")
def read_root():
    return {"message": "Coin Identifier API is running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        from database import db

        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


def call_openai_vision(base64_image: str) -> Dict[str, Any]:
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    # Use a vision-capable chat/completions endpoint. Adjust model as needed.
    endpoint = f"{OPENAI_API_BASE}/chat/completions"
    payload = {
        "model": "gpt-4o-mini",  # lightweight vision model
        "temperature": 0.2,
        "messages": [
            {
                "role": "system",
                "content": "You are a numismatics expert. Analyze the provided coin image and return a concise, structured JSON with fields: name, country, year, denomination, composition, mint_mark, history, features, condition_estimate, estimated_value, confidence (0-1). If uncertain, include best estimates and say 'Unknown' where needed."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Please analyze this coin and extract detailed information."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    },
                ],
            },
        ],
        "response_format": {"type": "json_object"}
    }

    try:
        r = requests.post(endpoint, headers=headers, json=payload, timeout=60)
        r.raise_for_status()
        data = r.json()
        # Extract the JSON content from assistant message
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "{}")
        import json
        parsed = json.loads(content)
        return parsed
    except requests.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"OpenAI API error: {e.response.text[:300]}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling OpenAI: {str(e)[:200]}")


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_coin(file: UploadFile = File(...)):
    try:
        # Read and encode image
        content = await file.read()
        base64_image = base64.b64encode(content).decode("utf-8")

        # Call OpenAI vision
        ai_result = call_openai_vision(base64_image)

        # Normalize into our schema
        analysis = CoinAnalysis(
            filename=file.filename,
            name=ai_result.get("name"),
            country=ai_result.get("country"),
            year=ai_result.get("year"),
            denomination=ai_result.get("denomination"),
            composition=ai_result.get("composition"),
            mint_mark=ai_result.get("mint_mark"),
            history=ai_result.get("history"),
            features=ai_result.get("features"),
            condition_estimate=ai_result.get("condition_estimate"),
            estimated_value=ai_result.get("estimated_value"),
            confidence=ai_result.get("confidence"),
            model="gpt-4o-mini",
            raw_analysis=ai_result,
        )

        # Persist to DB
        doc_id = create_document("coinanalysis", analysis)

        return AnalyzeResponse(id=doc_id, data=analysis)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
