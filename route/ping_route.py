from fastapi import APIRouter

ping = APIRouter()


@ping.get("/ping")
def get():
    return "hello python"
