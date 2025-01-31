import os
import subprocess

# Definir el puerto con un valor por defecto si no está en las variables de entorno
port = os.getenv("PORT", "8000")

# Comando para ejecutar uvicorn
cmd = ["uvicorn", "api2.app:app", "--host", "0.0.0.0", "--port", 8001, "--reload"]

# Ejecutar el comando
subprocess.run(cmd)
