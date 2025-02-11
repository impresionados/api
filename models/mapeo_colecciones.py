import mongoengine
from mongoengine import Document, StringField, ReferenceField, ListField, FloatField, IntField, FileField

class User(mongoengine.Document):
    meta = {'collection': 'users'}  # To specify the collection being mapped

    # _id = mongoengine.IntField(required=True)
    user_name = mongoengine.StringField(required=True)
    email = mongoengine.StringField(required=True)
    password = mongoengine.StringField(required=True)
    registration_date = mongoengine.DateTimeField(required=True)
    address = mongoengine.StringField(required=True)
    tlf = mongoengine.IntField(required=True)

class Rating(mongoengine.EmbeddedDocument):  # To specify that it is inside another class
    user_id = mongoengine.StringField(required=True)
    rating = mongoengine.IntField(required=True)
    comment = mongoengine.StringField()
    date = mongoengine.DateTimeField(required=True)

class Tipo(Document):
    name = StringField(required=True, unique=True)

class SuperTipo(Document):
    name = StringField(required=True, unique=True)
    tipos_asociados = ListField(ReferenceField(Tipo))  # Relación con varios tipos
# class Product(Document):
#     name = StringField(required=True)
#     description = StringField()
#     price = FloatField(required=True)
#     stock = IntField(required=True)
#     super_tipo = ReferenceField(SuperTipo, required=True)  # Solo SuperTipos existentes
#     tipos = ListField(ReferenceField(Tipo))  # Solo Tipos existentes
class Products(Document):
    description = StringField(required=True)
    stock = IntField(required=True, default=0)
    price = IntField(required=True, default=1)
    name = StringField(required=True)
    image = FileField(required=True)
    supertipo = ReferenceField(SuperTipo, default="arreglar")
    tipo = ListField(ReferenceField(Tipo, default="arreglar, pero tipo"))
    ratings = StringField(required=True)
    category = StringField(required=True)

class Order(mongoengine.Document):
    meta = {'collection': 'orders'}

    # _id = mongoengine.IntField(required=True)
    product_id = mongoengine.StringField(required=True)
    user_id = mongoengine.StringField(required=True)
    date = mongoengine.DateTimeField(required=True)
    total = mongoengine.FloatField(required=True)
    status = mongoengine.StringField(required=True)

