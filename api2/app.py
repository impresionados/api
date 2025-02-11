from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Query
from fastapi.responses import Response
from datetime import datetime
from io import BytesIO
from pydantic import BaseModel
from typing import List, Optional
from database.conection import conection
from mongoengine import FileField
from models.mapeo_colecciones import *
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://10.102.10.35:5173", "http://10.102.9.193:5173", "http://10.102.10.42:5173"],  # Reemplázalo con tu frontend 5173
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos: GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],  # Permitir todos los headers
)
# ========================== MODELOS ==========================

class SuperTipo(Document):
    name = StringField(required=True, unique=True)


class Tipo(Document):
    """    new_super_type.super_tipo = id_super_type
    new_super_type.tipos = IDs_types"""
    name = StringField(required=True, unique=True)
    super_tipo = ReferenceField(SuperTipo, required=True)  # Relación con Tipo
    # tipos = ListField(ReferenceField(SuperTipo))  # Relación con varios Tipos


class Products(Document):
    description = StringField(required=True)
    stock = IntField(required=True, default=0)
    price = IntField(required=True, default=1)
    name = StringField(required=True)
    image = FileField(required=True)
    supertipo = ReferenceField(SuperTipo, default="arreglar")
    tipo = ReferenceField(Tipo, default="arreglar, pero tipo")
    # ratings = StringField(required=True)
# ========================== MODELOS DE RESPUESTA Pydantic ==========================

class RatingModel(BaseModel):
    user_id: str
    rating: int
    comment: Optional[str]
    date: datetime
    address: Optional[str]
    tlf: Optional[str]


class ProductModel(BaseModel):
    id: str
    name: str
    description: Optional[str]
    price: float
    stock: int
    category: List[str]
    image: Optional[str]
    ratings: List[RatingModel]

    class Config:
        orm_mode = True  # Esto permite que Pydantic maneje objetos MongoEngine

class TipoCreateRequest(BaseModel):
    name_type: str
    id_super_type: str
    # IDs_types: List[str]
# ========================== RUTAS PARA USUARIOS ==========================

@app.post("/users/", response_model=dict)
#    address: Optional[str]
#     tlf: Optional[str]
def create_user(user_name: str, email: str, password: str, address: str, tlf: int):
    if User.objects(email=email):
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(user_name=user_name, email=email, password=password, address= address, tlf= tlf, registration_date=datetime.now())
    user.save()
    return {"message": "User created successfully"}


@app.get("/users/exist", response_model=dict)
def user_exist(get_email:str):
    print(get_email)
    # return {"message": get_email}
    return {"exists": bool(User.objects(email=get_email).first())}
    # user = User.objects(email=email)
    # print(user)

@app.get("/users/{email}", response_model=dict)
def get_user_by_email(email: str):
    user = User.objects(email=email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = user.to_mongo().to_dict()
    user_data["_id"] = str(user_data["_id"])  # Convertir el ObjectId a str
    return user_data


@app.put("/users/{user_id}/email", response_model=dict)
def update_user_email(user_id: str, new_email: str):
    user = User.objects(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.update(email=new_email)
    return {"message": "Email updated successfully"}


@app.delete("/users/{user_id}", response_model=dict)
def delete_user(user_id: str):
    user = User.objects(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.delete()
    return {"message": "User deleted successfully"}

# # ========================== RUTAS PARA TIPOS Y SUPER TIPOS ==========================
#
# @app.get("/tipos/")
# def obtener_tipos():
#     return [{"id": str(tipo.id), "nombre": tipo.name} for tipo in SuperTipo.objects()]
#
# @app.post("/tipo/")
# def crear_tipo(nombre):
#     if nombre is None or nombre.strip() == '':
#         raise ValueError("El nombre no puede ser nulo o vacío.")
#     tipo = SuperTipo(name=nombre)
#     tipo.save()
#     return {"id" : str(tipo.id), "nombre" : tipo.name}


# ========================== RUTAS PARA PRODUCTOS ==========================

@app.post("/products/", response_model=dict)
async def create_product(name: str = Form(...),
                         description: str = Form(...),
                         price: float = Form(...),
                         stock: int = Form(...),
                         # category: List[str] = Form(...),
                         image: UploadFile = File(...),
                         supertipo: str = Form(...),
                         tipo: str = Form(...),
                         # ratings: List[RatingModel] = Form(...)
                         ):
    image_data = BytesIO(await image.read())
    product = Products(name=name, description=description, price=price, stock=stock,
                       supertipo=supertipo,
                       tipo=tipo,
                       # ratings=ratings
                       )
    product.image.put(image_data, filename=image.filename, content_type=image.content_type)
    product.save()
    return {"message": "Product created successfully", "product_id": str(product.id)}

@app.get("/products/", response_model=List[ProductModel])
def get_all_products():
    products = Products.objects()  # Obtiene todos los productos de la base de datos
    return [
        {
            "id": str(product.id),
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "stock": product.stock,
            "category": product.category,
            "image": f"http://localhost:8001/products/{product.id}/image" if product.image else None,
            "ratings": [
                {
                    "user_id": rating.user_id,
                    "rating": rating.rating,
                    "comment": rating.comment,
                    "date": rating.date
                }
                for rating in product.ratings
            ]
        }
        for product in products
    ]


@app.get("/products/{product_id}", response_model=ProductModel)
def get_product_by_id(product_id: str):
    product = Products.objects(id=product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return {
        'id': str(product.id),
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'stock': product.stock,
        'category': product.category,
        'image': None,
        'ratings': [
            {
                'user_id': rating.user_id,
                'rating': rating.rating,
                'comment': rating.comment,
                'date': rating.date
            } for rating in product.ratings
        ]
    }

@app.put("/products/{product_id}/stock", response_model=dict)
def update_product_stock(product_id: str, new_stock: int):
    product = Products.objects(id=product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.update(stock=new_stock)
    return {"message": "Stock updated successfully"}

@app.post("/products/{product_id}/ratings", response_model=dict)
def add_rating_to_product(product_id: str, user_id: str, rating: int, comment: str = None):
    product = Products.objects(id=product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    new_rating = Rating(user_id=user_id, rating=rating, comment=comment, date=datetime.now())
    product.update(push__ratings=new_rating)
    return {"message": "Rating added successfully"}


@app.get("/products/{product_id}/image")
def get_product_image(product_id: str):
    product = Products.objects(id=product_id).first()

    if not product or not product.image:
        raise HTTPException(status_code=404, detail="Image not found")

    return Response(content=product.image.read(), media_type=product.image.content_type)


@app.delete("/products/{product_id}", response_model=dict)
def delete_product(product_id: str):
    product = Products.objects(id=product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.delete()
    return {"message": "Product deleted successfully"}

# ========================== RUTAS PARA ÓRdenes ==========================

@app.post("/orders/", response_model=dict)
def create_order(product_id: str, user_id: str, total: float, status: str):
    if not Products.objects(id=product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    if not User.objects(id=user_id):
        raise HTTPException(status_code=404, detail="User not found")
    order = Order(product_id=product_id, user_id=user_id, date=datetime.now(), total=total, status=status)
    order.save()
    return {"message": "Order created successfully", "order_id": str(order.id)}

@app.get("/orders/{order_id}", response_model=dict)
def get_order_by_id(order_id: str):
    order = Order.objects(id=order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order.to_mongo().to_dict()

@app.get("/orders/user/{user_id}", response_model=list)
def get_orders_by_user(user_id: str):
    orders = Order.objects(user_id=user_id)
    return [order.to_mongo().to_dict() for order in orders]

@app.put("/orders/{order_id}/status", response_model=dict)
def update_order_status(order_id: str, new_status: str):
    order = Order.objects(id=order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.update(status=new_status)
    return {"message": "Order status updated successfully"}

@app.delete("/orders/{order_id}", response_model=dict)
def delete_order(order_id: str):
    order = Order.objects(id=order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.delete()
    return {"message": "Order deleted successfully"}





#Crear type
# @app.get('/super_type/')
# def create_type(name_type:str):
#     new_type = create_type(name_type)
#     return new_type

#Todos los super type
@app.get('/super_type_all/')
def get_all_type():
    aux = []
    for tipo in SuperTipo.objects():
        auxx = {
            'id': str(tipo.id),
            'name': tipo.name
        }
        aux.append(auxx)
    return aux

#Eliminar Type
@app.delete('/super_type/delete/')
def delete_type(id_type:str):
    SuperTipo.objects(id=id_type).delete()
    return {"message": "Type deleted"}

#Devolver id segun nombre super tipo
@app.get('/super_type/by_name/')
def get_id_by_name_super_type(name_super_type:str):
    super_type_ref = SuperTipo.objects(name=name_super_type).first()
    if not super_type_ref:
        return {"error": "SuperTipo no encontrado"}
    return {"id": str(super_type_ref.id)}
#Devolver tipos segun id super tipo
@app.get('/type/by_super_type/')
def get_types_by_super_type(id_super_type:str):
    types_by_super_type = []
    for tipo in Tipo.objects(super_tipo=id_super_type):
        types_by_super_type.append(tipo.name)
    return types_by_super_type
#----------------------------------------------------------------
#Crear type
@app.post('/type/')
def create_super_type(data: TipoCreateRequest):
    # Verificar que el SuperTipo existe
    super_tipo_ref = SuperTipo.objects(id=data.id_super_type).first()
    if not super_tipo_ref:
        return {"error": "SuperTipo no encontrado"}

    # Crear el nuevo Tipo
    new_tipo = Tipo(
        name=data.name_type,
        super_tipo=super_tipo_ref,
    )
    new_tipo.save()

    return {"message": f"Tipo '{new_tipo.name}' creado correctamente"}

#Todos los super type
@app.get("/supertypes_with_types/")
def obtener_supertypes_con_tipos():
    supertipos_dict = {}

    for supertipo in SuperTipo.objects():
        supertipos_dict[supertipo.name] = []
        for tipo in Tipo.objects(super_tipo=supertipo):
            supertipos_dict[supertipo.name].append(tipo.name)

    return supertipos_dict

 #filtro
# @app.get("/filter/")
# def filtrar_tipos(listas:list):
#     for lista in listas:
#         if lista != []:
#             pass
