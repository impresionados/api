import mongoengine
from datetime import datetime
from models.mapeo_colecciones import *
# ----- CRUD for User -----
class UserCRUD:
    @staticmethod
    def create_user(user_name, email, password):
        user = User(
            user_name=user_name,
            email=email,
            password=password,
            registration_date=datetime.now()
        )
        user.save()
        return user

    @staticmethod
    def get_user_by_email(email):
        return User.objects(email=email).first()

    @staticmethod
    def update_user_email(user_id, new_email):
        user = User.objects(id=user_id).first()
        if user:
            user.update(email=new_email)
        return user

    @staticmethod
    def delete_user(user_id):
        user = User.objects(id=user_id).first()
        if user:
            user.delete()
        return user


# ----- CRUD for Product -----
class ProductCRUD:
    @staticmethod
    def create_product(name, description, price, stock, category, image=None):
        product = Product(
            name=name,
            description=description,
            price=price,
            stock=stock,
            category=category,
            image=image,
            ratings=[]
        )
        product.save()
        return product

    @staticmethod
    def get_all_products():
        return Product.objects()

    @staticmethod
    def get_product_by_id(product_id):
        return Product.objects(id=product_id).first()

    @staticmethod
    def update_product_stock(product_id, new_stock):
        product = Product.objects(id=product_id).first()
        if product:
            product.update(stock=new_stock)
        return product

    @staticmethod
    def delete_product(product_id):
        product = Product.objects(id=product_id).first()
        if product:
            product.delete()
        return product

    @staticmethod
    def add_rating_to_product(product_id, user_id, rating, comment=None):
        product = Product.objects(id=product_id).first()
        if product:
            new_rating = Rating(
                user_id=user_id,
                rating=rating,
                comment=comment,
                date=datetime.now()
            )
            product.update(push__ratings=new_rating)
        return product


# ----- CRUD for Order -----
class OrderCRUD:
    @staticmethod
    def create_order(product_id, user_id, total, status):
        order = Order(
            product_id=product_id,
            user_id=user_id,
            date=datetime.now(),
            total=total,
            status=status
        )
        order.save()
        return order

    @staticmethod
    def get_order_by_id(order_id):
        return Order.objects(id=order_id).first()

    @staticmethod
    def get_orders_by_user(user_id):
        return Order.objects(user_id=user_id)

    @staticmethod
    def update_order_status(order_id, new_status):
        order = Order.objects(id=order_id).first()
        if order:
            order.update(status=new_status)
        return order

    @staticmethod
    def delete_order(order_id):
        order = Order.objects(id=order_id).first()
        if order:
            order.delete()
        return order
