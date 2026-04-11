############################################################
#                    IMPORTAR LIBRERIAS                   #
############################################################

# Inserta la carpeta padre "9-aprendiendo-fastapi" al inicio de sys.path en la posición 0,
# para poder importar la carpeta "helpers" desde este archivo,
# lo que estaba en la posición 0 se desplaza, no se pierde
import sys
sys.path.insert(0, "..")

# FastAPI
from fastapi import FastAPI, Query, Body, HTTPException

# Pydantic
from pydantic import BaseModel, Field, field_validator, EmailStr

# Typing
# from typing import Optional, List, Union  # Se reemplazo con Python nativo

# Helpers
from helpers import utils

############################################################
#                    DECLARAR VARIABLES                   #
############################################################

BLOG_POST = [
    {
        "id": 1,
        "title": "Hola desde FastAPI",
        "content": "Mi primer post con FastAPI",
    },
    {
        "id": 2,
        "title": "Mi segundo Post con FastAPI",
        "content": "Mi segundo post con FastAPI blablabla",
    },
    {
        "id": 3,
        "title": "Django vs FastAPI",
        "content": "FastAPI es más rápido por x razones",
    },
]

############################################################
#                       CREAR EL APP                      #
############################################################

# Crear el app
app = FastAPI(title="Mini Blog")

############################################################
#                         MODELOS                         #
############################################################


# ****************** Modelos de respuesta ******************


class Tag(BaseModel):
    name: str = Field(
        ...,  # ..., significa que el campo es obligatorio
        min_length=2,
        max_length=30,
        description="Nombre de la etiqueta",
    )


class Author(BaseModel):
    name: str
    email: EmailStr


class PostBase(BaseModel):
    title: str
    content: str
    tags: list[Tag] | None = []  # Puede ser null, si es null, se asigna una lista vacía
    author: Author | None = None  # Puede ser null


class PostPublic(PostBase):
    id: int


class PostSummary(BaseModel):
    id: int
    title: str


# ****************** Modelos de petición ******************


class PostCreate(BaseModel):
    title: str = Field(
        ...,  # ..., significa que el campo es obligatorio
        min_length=3,
        max_length=100,
        description="Titulo del post (mínimo 3 caracteres, máximo 100)",
        examples=["Mi primer post con FastAPI"],
    )
    content: str | None = Field(  # Puede ser null
        default="Contenido no disponible",
        min_length=10,
        description="Contenido del post (mínimo 10 caracteres)",
        examples=["Este es un contenido válido porque tiene 10 caracteres o más"],
    )
    tags: list[Tag] | None = []  # Puede ser null, si es null, se asigna una lista vacía
    author: Author | None = None  # Puede ser null

    # Validar campo titulo
    # @field_validator("title"), significa que se validara el campo titulo
    # @classmethod, significa que es un metodo de clase, para validar campo titulo
    #  -> str, significa que el metodo retorna un string
    @field_validator("title")
    @classmethod
    def not_allowed_title(cls, value: str) -> str:
        if "spam" in value.lower():
            raise ValueError("El título no puede contener la palabra: 'spam'")
        return value


class PostUpdate(BaseModel):
    title: str
    content: str | None = None  # Puede ser null


############################################################
#                         ENDPOINTS                        #
############################################################



"""
HOME
    URLs
    http://127.0.0.1:8000
"""
@app.get("/")
def home():
    return {"message": "Bienvenidos a Mini Blog por Devtalles"}



"""
LIST POSTS
    URLs
    http://127.0.0.1:8000/posts
    http://127.0.0.1:8000/posts?query=hola
"""
@app.get(
    "/posts",
    response_model=list[PostPublic],  # Retorna una Lista de PostPublic
    response_description="Lista de posts",
)
def list_posts(query: str | None = Query(default=None, description="Texto para buscar por título")):
    if query:
        return [post for post in BLOG_POST if query.lower() in post["title"].lower()]

    return BLOG_POST



"""
GET POST
    URLs
    http://127.0.0.1:8000/posts/1
    http://127.0.0.1:8000/posts/1?include_content=false
"""
@app.get(
    "/posts/{post_id}",
    response_model=PostPublic | PostSummary,  # Retorna un PostPublic (con contenido) o un PostSummary (solo id y title)
    response_description="Post encontrado",
)
def get_post(post_id: int, include_content: bool = Query(default=True, description="Incluir o no el contenido")):
    for post in BLOG_POST:
        if post["id"] == post_id:
            if not include_content:
                return {"id": post["id"], "title": post["title"]}
            return post

    raise HTTPException(status_code=404, detail="Post no encontrado")



"""
CREATE POST
    URLs
    http://127.0.0.1:8000/posts
"""
@app.post(
    "/posts",
    response_model=PostPublic,  # Retorna un PostPublic
    response_description="Post creado (OK)",
)
def create_post(post: PostCreate):
    # Debug
    utils.error_log("****************** create_post ******************")
    utils.error_log("type", type(post))
    utils.error_log("post", post)

    # Obtener id automaticamente
    new_id = (BLOG_POST[-1]["id"] + 1) if BLOG_POST else 1

    # Crear post
    new_post = {
        "id": new_id,
        "title": post.title,
        "content": post.content,
        "tags": [tag.model_dump() for tag in post.tags],  # model_dump() de Pydantic, convertir modelo de Pydantic a objeto de Python (diccionario, lista, etc)
        "author": post.author.model_dump() if post.author else None,  # model_dump() de Pydantic, convertir modelo de Pydantic a objeto de Python (diccionario, lista, etc)
    }
    BLOG_POST.append(new_post)

    return new_post



"""
UPDATE POST
    URLs
    http://127.0.0.1:8000/posts/1
"""
@app.put(
    "/posts/{post_id}",
    response_model=PostPublic,  # Retorna un PostPublic
    response_description="Post actualizado",
    response_model_exclude_none=True,
)
def update_post(post_id: int, data: PostUpdate):
    for post in BLOG_POST:
        if post["id"] == post_id:

            # Debug
            utils.error_log("****************** update_post ******************")
            utils.error_log("type", type(data))
            utils.error_log("post", data)

            # Convertir modelo de Pydantic a objeto de Python (diccionario, lista, etc)
            # model_dump() de Pydantic, convertir modelo de Pydantic a objeto de Python (diccionario, lista, etc)
            # exclude_unset=True, excluir campos que no se envian en la petición, para no actualizar esos campos a null
            # Si enviamos {"title": "Nuevo título"}, con exclude_unset=True, el resultado de model_dump() será {"title": "Nuevo título"}
            # Si enviamos {"title": "Nuevo título"}, con exclude_unset=False, el resultado de model_dump() será {"title": "Nuevo título", "content": None}, lo cual no queremos porque no queremos actualizar el contenido a null
            playload = data.model_dump(
                exclude_unset=True
            )

            # Debug
            utils.error_log("type", type(playload))
            utils.error_log("playload", playload)

            # Actualizar post
            if "title" in playload:
                post["title"] = playload["title"]
            if "content" in playload:
                post["content"] = playload["content"]
            return post

    raise HTTPException(status_code=404, detail="Post no encontrado")



"""
DELETE POST
    URLs
    http://127.0.0.1:8000/posts/1
"""
@app.delete("/posts/{post_id}")  # ("/posts/{post_id}", status_code=204)
def delete_post(post_id: int):
    for index, post in enumerate(BLOG_POST):
        if post["id"] == post_id:
            BLOG_POST.pop(index)  # Eliminar elemento de array
            return

    raise HTTPException(status_code=404, detail="Post no encontrado")
