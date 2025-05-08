from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os


class AvailableSlot(BaseModel):
    date: str
    day: str
    slots: List[str]


class Doctor(BaseModel):
    name: str
    specialty: str
    available_slots: List[AvailableSlot]


load_dotenv()

DATABASE = os.getenv("DATABASE")
COLLECTION = os.getenv("COLLECTION")
MONGO_URI = os.getenv("MONGO_URI")

my_client = AsyncIOMotorClient(MONGO_URI)
my_db = my_client[DATABASE]
doctors_collection = my_db[COLLECTION]

app = FastAPI()


@app.get("/")
def hello_world():
    return "Hello World"


@app.get("/doctors")
async def get_all_doctors():
    doctor_list = []
    async for doctor in doctors_collection.find():
        doctor["_id"] = str(doctor["_id"])
        doctor_list.append(doctor)
    return doctor_list


@app.post("/doctors", status_code=201)
async def add_new_doctor(doctor: Doctor):
    new_doctor = doctor.model_dump()
    result = await doctors_collection.insert_one(new_doctor)
    created_doctor = await doctors_collection.find_one({"_id": result.inserted_id})
    created_doctor["_id"] = str(created_doctor["_id"])
    return {
        "success": True,
        "message": "Doctor profile created successfully.",
        "doctor_id": created_doctor["_id"]
    }


@app.get("/doctors/{doctor_name}")
async def get_doctor_by_name(doctor_name: str):
    doctor = await doctors_collection.find_one({"name": doctor_name})
    if doctor:
        doctor["_id"] = str(doctor["_id"])
        return doctor
    return {"message": f"Doctor with name '{doctor_name}' not found"}
