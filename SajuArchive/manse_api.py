from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
from manse import SajuCoreEngine, lunar_to_solar, get_ai_interpretation

app = FastAPI(title="Mansin Saju API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SajuRequest(BaseModel):
    name: str = "내담자"
    gender: str = "남"
    cal_type: str = "양력"
    year: int
    month: int
    day: int
    hour: int = 12
    unknown_time: bool = False
    is_leap_month: bool = False
    api_key: Optional[str] = None
    focus: Optional[str] = "종합 운세"
    marriage: Optional[str] = "미혼"
    occupation: Optional[str] = "선택 안 함"

@app.post("/api/saju")
async def calculate_saju(req: SajuRequest):
    b_year, b_month, b_day = req.year, req.month, req.day
    if req.cal_type == "음력":
        try:
            solar_date = lunar_to_solar(req.year, req.month, req.day, req.is_leap_month)
            b_year, b_month, b_day = solar_date.year, solar_date.month, solar_date.day
        except Exception as e:
            raise HTTPException(status_code=400, detail="음력 날짜 변환 실패")
            
    b_hour = 12 if req.unknown_time else req.hour
    
    try:
        pils = SajuCoreEngine.get_pillars(b_year, b_month, b_day, b_hour, req.gender)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    saju_data = {
        "name": req.name,
        "gender": req.gender,
        "birth_type": req.cal_type,
        "raw_birth": {"year": req.year, "month": req.month, "day": req.day, "hour": req.hour},
        "solar_birth": {"year": b_year, "month": b_month, "day": b_day, "hour": b_hour},
        "marriage": req.marriage,
        "occupation": req.occupation
    }
    
    # Try fetching AI interpretation if API Key provided
    ai_text = None
    if req.api_key:
        try:
            import requests # checking if we just need to proxy groq here or use manse.py's native 
            # Actually, `get_ai_interpretation` has specific args. Let's just return pils and saju_data first
            pass
        except Exception as e:
            print("AI Error:", e)

    return {"status": "success", "pils": pils, "saju_data": saju_data}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
