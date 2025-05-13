from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Request model
class EloRequest(BaseModel):
    password: str
    player1_elo: int
    player2_elo: int
    outcome: float  # 1.0 (player1 wins), 0.0 (player2 wins), 0.5 (draw)

# Get API password from environment
API_PASSWORD = os.getenv("API_PASSWORD", "default_password")

# Elo calculation
def calculate_elo(rating1: int, rating2: int, outcome: float, k: int = 32) -> tuple[int, int]:
    expected1 = 1.0 / (1.0 + 10 ** ((rating2 - rating1) / 400.0))
    expected2 = 1.0 / (1.0 + 10 ** ((rating1 - rating2) / 400.0))
    new_rating1 = rating1 + k * (outcome - expected1)
    new_rating2 = rating2 + k * ((1 - outcome) - expected2)
    return round(new_rating1), round(new_rating2)

@app.post("/calculate_elo")
async def calculate_elo_endpoint(request: EloRequest):
    if request.password != API_PASSWORD:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    
    if request.player1_elo < 0 or request.player2_elo < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Elo ratings must be non-negative")
    
    if request.outcome not in [0.0, 0.5, 1.0]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Outcome must be 0.0, 0.5, or 1.0")
    
    new_elo1, new_elo2 = calculate_elo(request.player1_elo, request.player2_elo, request.outcome)
    return {"player1_new_elo": new_elo1, "player2_new_elo": new_elo2}

@app.get("/")
async def root():
    return {"message": "Elo Calculator API"}
