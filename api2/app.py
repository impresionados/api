from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from fastapi.responses import StreamingResponse
from models.mapeo_colecciones import User, Product, Order, Rating
from datetime import datetime
from io import BytesIO
import uvicorn
from pydantic import BaseModel
from typing import List, Optional
from database.conection import conection
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Reemplázalo con tu frontend
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos: GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],  # Permitir todos los headers
)

# ----- Modelos de Respuesta Pydantic -----
# Modelo de Rating
class RatingModel(BaseModel):
    user_id: str
    rating: int
    comment: Optional[str]
    date: datetime

# Modelo de Producto
class ProductModel(BaseModel):
    id: str  # Usamos 'str' para representar el ObjectId como un string
    name: str
    description: Optional[str]
    price: float
    stock: int
    category: List[str]
    image: Optional[str]  # Si la imagen existe, se convierte a string
    ratings: List[RatingModel]

    class Config:
        orm_mode = True  # Esto permite que Pydantic maneje objetos MongoEngine


# ----- Rutas para Usuarios -----
@app.post("/users/", response_model=dict)
def create_user(user_name: str, email: str, password: str, address: str, tlf: int):
    if User.objects(email=email):
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(user_name=user_name, email=email, password=password, address=address,
	tlf=tlf ,registration_date=datetime.now())
    user.save()
    return {"message": "User created successfully"}

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


# ----- Rutas para Productos -----
@app.post("/products/", response_model=dict)
async def create_product(name: str = Form(...), description: str = Form(...), price: float = Form(...), stock: int = Form(...), category: List[str] = Form(...), image: UploadFile = File(...)):
    image_data = BytesIO(await image.read())
    product = Product(name=name, description=description, price=price, stock=stock, category=category)
    product.image.put(image_data, filename=image.filename, content_type=image.content_type)
    product.save()
    return {"message": "Product created successfully", "product_id": str(product.id)}

@app.get("/products/", response_model=List[ProductModel])
def get_all_products():
    products = Product.objects()
    product_list = []

    for product in products:
        image_url = None
        if product.image:
            try:
                # Verificamos si image tiene una ID válida
                image_url = str(product.image.id)
            except AttributeError:
                # Si no hay id, entonces manejamos el error de forma adecuada
                image_url = None  # O podrías asignar un valor por defecto

        product_dict = {
            'id': str(product.id),  # Convertimos el ObjectId a string
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'stock': product.stock,
            'category': product.category,
            'image': image_url,
            'ratings': [
                {
                    'user_id': rating.user_id,
                    'rating': rating.rating,
                    'comment': rating.comment,
                    'date': rating.date
                } for rating in product.ratings
            ]
        }
        product_list.append(product_dict)

    return product_list



@app.get("/products/{product_id}", response_model=ProductModel)
def get_product_by_id(product_id: str):
    product = Product.objects(id=product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return {
        'id': str(product.id),
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'stock': product.stock,
        'category': product.category,
        'image':  None, #str(product.image.id) if product.image else None,
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
    product = Product.objects(id=product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.update(stock=new_stock)
    return {"message": "Stock updated successfully"}

@app.post("/products/{product_id}/ratings", response_model=dict)
def add_rating_to_product(product_id: str, user_id: str, rating: int, comment: str = None):
    product = Product.objects(id=product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    new_rating = Rating(user_id=user_id, rating=rating, comment=comment, date=datetime.now())
    product.update(push__ratings=new_rating)
    return {"message": "Rating added successfully"}

@app.get("/products/{product_id}/image")
def get_product_image(product_id: str):
    product = Product.objects(id=product_id).first()
    if not product or not product.image:
        raise HTTPException(status_code=404, detail="Image not found")
    return StreamingResponse(BytesIO(product.image.read()), media_type=product.image.content_type)

@app.delete("/products/{product_id}", response_model=dict)
def delete_product(product_id: str):
    product = Product.objects(id=product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.delete()
    return {"message": "Product deleted successfully"}


# ----- Rutas para Órdenes -----
@app.post("/orders/", response_model=dict)
def create_order(product_id: str, user_id: str, total: float, status: str):
    if not Product.objects(id=product_id):
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
