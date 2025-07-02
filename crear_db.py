import MySQLdb
from config import Config

conn = MySQLdb.connect(
    host=Config.MYSQL_HOST,
    user=Config.MYSQL_USER,
    passwd=Config.MYSQL_PASSWORD
)
cursor = conn.cursor()

cursor.execute("CREATE DATABASE IF NOT EXISTS tienda_ropa")
cursor.execute("USE tienda_ropa")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL UNIQUE,
        email VARCHAR(100),
        password VARCHAR(255)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS productos (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(100),
        descripcion TEXT,
        precio DECIMAL(10, 2),
        imagen VARCHAR(255)
    )
""")

productos = [
    ("Polo Negro", "Polo de algodón 100% negro.", 49.90, "polo_negro.jpg"),
    ("Casaca Denim", "Casaca estilo jean, azul.", 129.90, "casaca_denim.jpg"),
    ("pantalon blanco", "Pantalon de buena calidad.", 129.90, "pants.jpg"),
    ("SPECIAL 4:20 2.0", "Gorro de buena calidad.", 129.90, "west.jpg"),
]

cursor.executemany("INSERT INTO productos (nombre, descripcion, precio, imagen) VALUES (%s, %s, %s, %s)", productos)
conn.commit()

print("Base de datos creada con éxito.")
cursor.close()
conn.close()
