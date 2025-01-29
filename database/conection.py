import mongoengine
import os
import dotenv
from urllib.parse import quote_plus

# Cargar las variables del archivo .env
# dotenv.load_dotenv()

def conection():
    """
    Establece una conexión con la base de datos MongoDB usando mongoengine.

    Returns:
        mongoengine.connection.MongoClient: El cliente de la base de datos si es exitoso.
        None: Si no se pudo establecer la conexión.
    """
    try:
        # Codificar la contraseña según RFC 3986
        # password = quote_plus(os.getenv('DATABASE_PASSWORD'))
        # username = quote_plus("impresionados")  # Codifica también el nombre de usuario si es necesario

        # Establecer la conexión
        connection = mongoengine.connect(
            db="impresionados",
            host=f"mongodb+srv://impresionados:{os.environ.get('DATABASE_PASSWORD')}@clusterimpresionados.jukxo.mongodb.net/?retryWrites=true&w=majority&appName=ClusterImpresionados"
        )
        print("Conexión establecida con la base de datos.")
        return connection
    except Exception as e:
        print("Error al conectar con la base de datos:", str(e))
        return None
def test_connection():
    """
    Realiza una consulta simple para verificar la conexión y autenticación.
    """
    try:
        # Realiza una consulta simple, como listar las colecciones disponibles
        db = mongoengine.get_db()
        collections = db.list_collection_names()
        print("Colecciones disponibles:", collections)
        return True
    except Exception as e:
        print("Error durante la prueba de conexión:", str(e))
        return False
conection()
test_connection()
if __name__ == "__main__":
    if conection():
        test_connection()
