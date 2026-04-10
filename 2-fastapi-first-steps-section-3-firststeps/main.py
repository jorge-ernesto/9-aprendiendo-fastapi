############################################################
#                    IMPORTAR LIBRERIAS                   #
############################################################

# FastAPI
from fastapi import FastAPI, Query, Body, HTTPException

############################################################
#                    DECLARAR VARIABLES                   #
############################################################

BLOG_POST = [
    {
        "id": 1,
        "title": "Hola desde FastAPI",
        "Content": "Mi primer post con FastAPI",
    },
    {
        "id": 2,
        "title": "Mi segundo Post con FastAPI",
        "Content": "Mi segundo post con FastAPI blablabla",
    },
    {
        "id": 3,
        "title": "Django vs FastAPI",
        "Content": "FastAPI es más rápido por x razones",
    },
]

############################################################
#                       CREAR EL APP                      #
############################################################

# Crear el app
app = FastAPI(title="Mini Blog")

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

    Query parameters
    Query(), define el parametro "query" como query parameter con default=None,
    definirlo con Query(), permite que FastAPI sepa explícitamente que es un parámetro de URL,
    además lo documenta y valida en Swagger, a diferencia de solo asignar = None
"""
@app.get("/posts")
def list_posts(query: str | None = Query(default=None, description="Texto para buscar por título")):
    if query:
        results = [post for post in BLOG_POST if query.lower() in post["title"].lower()]
        return {"data": results, "query": query}

    return {"data": BLOG_POST}



"""
GET POST
    URLs
    http://127.0.0.1:8000/posts/1
    http://127.0.0.1:8000/posts/1?include_content=false

    Path parameters
    ("/posts/{post_id}"), define el parametro "post_id" como path parameter, es decir, parte de la URL

    Query parameters
    Query(), define el parametro "include_content" como query parameter con default=True,
    definirlo con Query(), permite que FastAPI sepa explícitamente que es un parámetro de URL,
    además lo documenta y valida en Swagger, a diferencia de solo asignar = True
"""
@app.get("/posts/{post_id}")
def get_post(post_id: int, include_content: bool = Query(default=True, description="Incluir o no el contenido")):
    for post in BLOG_POST:
        if post["id"] == post_id:
            if not include_content:
                post_ = {"id": post["id"], "title": post["title"]}
                return {"data": post_}
            return {"data": post}

    raise HTTPException(status_code=404, detail="Post no encontrado")



"""
CREATE POST
    URLs
    http://127.0.0.1:8000/posts
"""
@app.post("/posts")
def create_post(post: dict = Body(...)):
    # Validar titulo
    # Validar contenido
    if "title" not in post or "content" not in post:
        return {"error": "Title y Content son requeridos"}

    # Validar que el titulo no este vacio
    if not str(post["title"]).strip():
        return {"error": "Title no puede estar vacío"}

    # Obtener id automaticamente
    new_id = (BLOG_POST[-1]["id"] + 1) if BLOG_POST else 1

    # Crear post
    new_post = {
        "id": new_id,
        "title": post["title"],
        "content": post["content"]
    }
    BLOG_POST.append(new_post)

    return {"message": "Post creado", "data": new_post}



"""
UPDATE POST
    URLs
    http://127.0.0.1:8000/posts/1
"""
@app.put("/posts/{post_id}")
def update_post(post_id: int, data: dict = Body(...)):
    for post in BLOG_POST:
        if post["id"] == post_id:

            # Actualizar post
            if "title" in data:
                post["title"] = data["title"]
            if "content" in data:
                post["content"] = data["content"]
            return {"message": "Post actualizado", "data": post}

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
            return {"message": "Post eliminado"}

    raise HTTPException(status_code=404, detail="Post no encontrado")
