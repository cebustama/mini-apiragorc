from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class SearchRequest(BaseModel):
    query: str


@app.post("/tools/search")
def search_incidents(req: SearchRequest):
    """
    Simula una búsqueda RAG en Elastic / documentación.
    """
    return {
        "results": [
            f"Incidente similar encontrado para: '{req.query}'",
            "Caso previo: caída de servidor en entorno PROD",
            "Solución aplicada: reinicio controlado + revisión de logs"
        ]
    }
