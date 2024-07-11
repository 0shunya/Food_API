from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from models import Food, SessionLocal, engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

class FoodCreate(BaseModel):
    name: str
    price: float
    description: str

class FoodResponse(FoodCreate):
    id: int

    class Config:
        orm_mode = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/foods/", response_model=FoodResponse)
def create_food(food: FoodCreate, db: Session = Depends(get_db)):
    db_food = Food(name=food.name, price=food.price, description=food.description)
    db.add(db_food)
    db.commit()
    db.refresh(db_food)
    return db_food

@app.get("/foods/{food_id}", response_model=FoodResponse)
def read_food(food_id: int, db: Session = Depends(get_db)):
    db_food = db.query(Food).filter(Food.id == food_id).first()
    if db_food is None:
        raise HTTPException(status_code=404, detail="Food item not found")
    return db_food

@app.get("/foods/", response_model=List<FoodResponse>)
def read_foods(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    foods = db.query(Food).offset(skip).limit(limit).all()
    return foods
