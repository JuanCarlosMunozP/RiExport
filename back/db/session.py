import os 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# Aqui ira database URL
DATABASE_URL = os.getenv("DATABASE_URL","postgresql://RiUser:RiPass@localhost:5432/RiDB")

if not DATABASE_URL:
    print("Error al conectar la base de datos")

engine = create_engine(DATABASE_URL)

Base = declarative_base()

SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)

Base.metadata.create_all(bind=engine)

def get_db():

    db = SessionLocal()

    if not db:
        print("Base de datos no encontrada")

    try:
        yield db
        print("Conexion a la base de datos exitosa")
    finally:
        print("Conexion finalizada")
        db.close()

def create_tables_if_not_exist():
    from models.user import User

    Base.metadata.create_all(bind=engine)