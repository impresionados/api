import os
from dotenv import load_dotenv
import mongoengine

# Cargar variables de entorno
load_dotenv()

def conection():
    """
    Establece una conexión con la base de datos MongoDB usando mongoengine.
    """
    try:
        password = os.getenv("DATABASE_PASSWORD")
        if not password:
            raise ValueError("La variable de entorno DATABASE_PASSWORD no está definida.")

        mongo_uri = f"mongodb+srv://impresionados:{password}@clusterimpresionados.jukxo.mongodb.net/impresionados?retryWrites=true&w=majority"

        connection = mongoengine.connect(host=mongo_uri)
        print("✅ Conexión establecida con la base de datos.")
        return connection
    except Exception as e:
        print("❌ Error al conectar con la base de datos:", str(e))
        return None

def test_connection():
    """
    Verifica la conexión con una consulta simple.
    """
    try:
        db = mongoengine.get_db()
        collections = db.list_collection_names()
        print("📂 Colecciones disponibles:", collections)
        return True
    except Exception as e:
        print("❌ Error durante la prueba de conexión:", str(e))
        return False
conection()
# Ejecutar pruebas
if __name__ == "__main__":
    conection()
    test_connection()
