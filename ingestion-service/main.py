from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI(title ="Ingestion service")

# internal buffer
buffer_size = 128
buffer = []

