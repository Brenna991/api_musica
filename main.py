from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, field_validator
from typing import Optional, List
from typing import optional
from fastapi.staticfiles import StaticFiles 

app = FastAPI()
app.mount("/static}", StaticFiles(directory="frontend"), name="static")

# --- Model (entrada) ---
class MusicaCreate(BaseModel):
    titulo: str 
    artista: str
    genero: optional [str]

class Musica(MusicaCreate):
    id: int

class MusicaCreate(BaseModel):
    titulo:Optional [str]= None
    artista: Optional[str]=None
    genero: Optional[str] = None

    @field_validator("titulo", "artista", mode="before")
    def strip_spaces(cls, v):
        return v.strip() if isinstance(v, str) else v

# --- "Banco" em memória ---
musicas: List[dict] = [
    {"id": 1, "titulo": "On This Love", "artista": "Suki Waterhouse", "genero": None},
    {"id": 2, "titulo": "Church Bells", "artista": "Henry Morris", "genero": None},
    {"id": 3, "titulo": "Bye", "artista": "Altare", "genero": None},
    {"id": 4, "titulo": "Sinking Love", "artista": "Last Known Species", "genero": None},
    {"id": 5, "titulo": "Robbed", "artista": "Rachel Chinouriri", "genero": None},
    {"id": 6, "titulo": "Belong To One", "artista": "Oskar Med K", "genero": None},
]

def _next_id() -> int:
    return max((m["id"] for m in musicas), default=0) + 1

# --- Endpoints básicos ---
@app.get("/musicas")
def listar_musicas():
    return {"musicas": musicas}

@app.get("/musicas/{id}")
def buscar_musicas(id: int):
    for musica in musicas:
        if musica["id"] == id:
            return musica
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Música não encontrada.")

# --- POST com checagem anti-duplicata simples ---
@app.post("/musicas", status_code=201)
def adicionar_musica(musica: MusicaCreate):
    # normalização simples: strip() já feita no validator; comparar em lower()
    titulo_novo = musica.titulo.lower()
    artista_novo = musica.artista.lower()

    # checar duplicata: percorre toda a lista
    for m in musicas:
        if m.get("titulo", "").lower() == titulo_novo and m.get("artista", "").lower() == artista_novo:
            raise HTTPException(status_code=400, detail="Essa música já existe.")

    # se passou na checagem, cria a entrada (id primeiro pra estética)
    novo = musica.model_dump() if hasattr(musica, "model_dump") else musica.dict()
    novo = {"id": _next_id(), **novo}
    musicas.append(novo)
    return {"mensagem": "Música adicionada com sucesso!!", "musica": novo}

@app.put("/musicas/{id}")
def atualizar_musica(id: int, payload: MusicaCreate):
    for idx, m in enumerate(musicas):
        if m["id"] == id:
            novo_titulo = payload.titulo.strip() if payload.titulo is not None else m["titulo"]
            novo_artista = payload.artista.strip() if payload.artista is not None else m["artista"]

            for other in musicas:
                if other ["id"] !=id and other["titulo"].lower() == novo_titulo.lower() and other["artista"].lower() == novo_artista.lower():
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ja existe outra musica com esse titulo e artista.")
                
                if payload.titulo is not None:
                    m["titulo"] = payload.titulo
                if payload.artista is not None:
                    m["artista"] = payload.artista
                if payload.genero is not None:
                    m["genero"] = payload.genero

            musicas[idx] = m
            return {"mensagem": "Música atualizada com sucesso!", "musica": m}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Música não encontrada.")

@app.delete("/musicas/{id}", status_code=200)
def excluir_musica(id: int):
    for m in musicas:
        if m["id"] == id:
            musicas.remove(m)
            return {"mensagem": "Música removida com sucesso!"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Música não encontrada.")

