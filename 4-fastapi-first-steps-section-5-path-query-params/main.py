
############################################################
#                    IMPORTAR LIBRERIAS                   #
############################################################

# FastAPI
from fastapi import FastAPI, Query, Body, HTTPException, Path

# Pydantic
from pydantic import BaseModel, Field, field_validator, EmailStr

# Typing
# from typing import Optional, List, Union, Literal  # Se reemplazo con Python nativo
from typing import Literal  # No hay reemplazo en Python nativo

# Helpers
from helpers import utils

# Librerias
from math import ceil

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
        "tags": [
            {"name": "Python"},
            {"name": "fastapi"},
            {"name": "Django"},
        ],
    },
    {
        "id": 4,
        "title": "Hola desde FastAPI",
        "content": "Mi primer post con FastAPI",
    },
    {
        "id": 5,
        "title": "Mi segundo Post con FastAPI",
        "content": "Mi segundo post con FastAPI blablabla",
    },
    {
        "id": 6,
        "title": "Django vs FastAPI",
        "content": "FastAPI es más rápido por x razones",
    },
    {
        "id": 7,
        "title": "Hola desde FastAPI",
        "content": "Mi primer post con FastAPI",
    },
    {
        "id": 8,
        "title": "Mi segundo Post con FastAPI",
        "content": "Mi segundo post con FastAPI blablabla",
    },
    {
        "id": 9,
        "title": "Django vs FastAPI",
        "content": "FastAPI es más rápido por x razones",
    },
    {
        "id": 10,
        "title": "Hola desde FastAPI",
        "content": "Mi primer post con FastAPI",
    },
    {
        "id": 11,
        "title": "Mi segundo Post con FastAPI",
        "content": "Mi segundo post con FastAPI blablabla",
    },
    {
        "id": 12,
        "title": "Django vs FastAPI",
        "content": "FastAPI es más rápido por x razones",
        "tags": [
            {"name": "Python"},
            {"name": "fastapi"},
            {"name": "Django"},
        ],
    },
    {
        "id": 13,
        "title": "Hola desde FastAPI",
        "content": "Mi primer post con FastAPI",
    },
    {
        "id": 14,
        "title": "Mi segundo Post con FastAPI",
        "content": "Mi segundo post con FastAPI blablabla",
    },
    {
        "id": 15,
        "title": "Django vs FastAPI",
        "content": "FastAPI es más rápido por x razones",
        "tags": [
            {"name": "Python"},
            {"name": "fastapi"},
            {"name": "Django"},
        ],
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
    tags: list[Tag] | None = Field(default_factory=list)  # Puede ser null, si es null, se asigna una lista vacía -- = Field(default_factory=list) y = [], son equivalentes, hacen lo mismo
                                                          # Field() permite agregar metadatos como description, min_length, max_length, etc
                                                          # default_factory= -- recibe una función callable y la llama por cada instancia -- para valores mutables ([], {})
                                                          # default=         -- recibe un valor fijo y lo asigna directamente             -- para valores inmutables (None, 0, "texto")
                                                          # default=[]       -- falla porque Pydantic rechaza mutables
                                                          # default=list     -- asignaría la clase, no []
    author: Author | None = None  # Puede ser null


class PostPublic(PostBase):
    id: int


class PostSummary(BaseModel):
    id: int
    title: str


class PaginatedPost(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int
    has_prev: bool
    has_next: bool
    order_by: Literal["id", "title"]  # Literal[], permite definir un conjunto exacto de valores permitidos
    direction: Literal["asc", "desc"]  # Literal[], permite definir un conjunto exacto de valores permitidos
    search: str | None = None
    items: list[PostPublic]


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
    tags: list[Tag] = Field(default_factory=list)  # Puede ser null, si es null, se asigna una lista vacía -- = Field(default_factory=list) y = [], son equivalentes, hacen lo mismo
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
    title: str | None = Field(  # Puede ser null
        default=None,
        min_length=3,
        max_length=100
    )
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
    http://127.0.0.1:8000/posts?query=fastapi
    http://127.0.0.1:8000/posts?page=2&per_page=3
    http://127.0.0.1:8000/posts?order_by=title&direction=desc
"""
@app.get(
    "/posts",
    response_model=PaginatedPost,  # Retorna un PaginatedPost con paginación
)
def list_posts(
    text: str | None = Query(
        default=None,
        deprecated=True,
        description="Parámetro obsoleto, usa 'query o search' en su lugar.",
    ),
    query: str | None = Query(
        default=None,
        description="Texto para buscar por título",
        alias="search",
        min_length=3,
        max_length=50,
        pattern=r"^[\w\sáéíóúÁÉÍÓÚüÜ-]+$",
    ),
    per_page: int = Query(
        10, ge=1, le=50,
        description="Número de resultados (1-50)",
    ),
    page: int = Query(
        1, ge=1,
        description="Número de página (>=1)",
    ),
    order_by: Literal["id", "title"] = Query(
        "id", description="Campo de orden",
    ),
    direction: Literal["asc", "desc"] = Query(
        "asc", description="Dirección de orden",
    ),
):
    results = BLOG_POST

    # Usar query o text (text es obsoleto)
    query = query or text

    # Filtrar por búsqueda
    if query:
        results = [post for post in results if query.lower() in post["title"].lower()]

    # Total de resultados y páginas
    total = len(results)
    total_pages = ceil(total / per_page) if total > 0 else 0

    # Calcular página actual
    if total_pages == 0:
        current_page = 1
    else:
        current_page = min(page, total_pages)

    # Ordenar resultados
    results = sorted(
        results, key=lambda post: post[order_by], reverse=(direction == "desc")
    )

    # Paginar resultados
    if total_pages == 0:
        items = []
    else:
        start = (current_page - 1) * per_page
        items = results[start: start + per_page]  # [10:20]

    # Calcular has_prev y has_next
    has_prev = current_page > 1
    has_next = current_page < total_pages if total_pages > 0 else False

    return PaginatedPost(
        page=current_page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_prev=has_prev,
        has_next=has_next,
        order_by=order_by,
        direction=direction,
        search=query,
        items=items,
    )



"""
FILTER BY TAGS
    URLs
    http://127.0.0.1:8000/posts/by-tags?tags=python&tags=fastapi
"""
@app.get(
    "/posts/by-tags",
    response_model=list[PostPublic],  # Retorna una Lista de PostPublic filtrada por tags
)
def filter_by_tags(
    tags: list[str] = Query(
        ...,
        min_length=2,
        description="Una o más etiquetas. Ejemplo: ?tags=python&tags=fastapi",
    ),
):
    # Convertir tags a minúsculas para comparar sin distinción de mayúsculas
    tags_lower = [tag.lower() for tag in tags]

    return [
        post for post in BLOG_POST
        if any(tag["name"].lower() in tags_lower for tag in post.get("tags", []))
    ]



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
def get_post(
    post_id: int = Path(
        ...,
        ge=1,
        title="ID del post",
        description="Identificador entero del post. Debe ser mayor a 1",
        example=1,
    ),
    include_content: bool = Query(default=True, description="Incluir o no el contenido"),
):
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
            # Convertir modelo de Pydantic a objeto de Python (diccionario, lista, etc)
            # model_dump() de Pydantic, convertir modelo de Pydantic a objeto de Python (diccionario, lista, etc)
            # exclude_unset=True, excluir campos que no se envian en la petición, para no actualizar esos campos a null
            # Si enviamos {"title": "Nuevo título"}, con exclude_unset=True, el resultado de model_dump() será {"title": "Nuevo título"}
            # Si enviamos {"title": "Nuevo título"}, con exclude_unset=False, el resultado de model_dump() será {"title": "Nuevo título", "content": None}, lo cual no queremos porque no queremos actualizar el contenido a null
            playload = data.model_dump(
                exclude_unset=True,
            )

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
@app.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: int):
    for index, post in enumerate(BLOG_POST):
        if post["id"] == post_id:
            BLOG_POST.pop(index)  # Eliminar elemento de array
            return

    raise HTTPException(status_code=404, detail="Post no encontrado")

