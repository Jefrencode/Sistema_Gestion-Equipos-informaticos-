import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, URL, text
from sqlalchemy.orm import sessionmaker

# Buscar el archivo .env en la raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Obtener las credenciales desde .env
USUARIO = os.getenv("DB_USER")
CONTRASENA = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST")
PUERTO = int(os.getenv("DB_PORT", "3306"))
BASE_DATOS = os.getenv("DB_NAME")

# Crear la URL de conexión
DATABASE_URL = URL.create(
    drivername="mysql+mysqlconnector",
    username=USUARIO,
    password=CONTRASENA,
    host=HOST,
    port=PUERTO,
    database=BASE_DATOS
)

# Motor de SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

# Fábrica de sesiones
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


def probar_conexion():
    try:
        with engine.connect() as conexion:
            nombre_bd = conexion.execute(
                text("SELECT DATABASE()")
            ).scalar_one()

            print(f"Conexión exitosa a: {nombre_bd}")
            return True

    except Exception as error:
        print(f"Error al conectar con MySQL: {error}")
        return False
