CREATE DATABASE IF NOT EXISTS tienda_ropa;
USE tienda_ropa;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100),
    password VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),
    descripcion TEXT,
    precio DECIMAL(10, 2),
    imagen VARCHAR(255)
);

INSERT INTO productos (nombre, descripcion, precio, imagen) VALUES
('Polo Negro', 'Polo de algodón 100% negro.', 49.90, 'polo_negro.jpg'),
('Casaca Denim', 'Casaca estilo jean, azul.', 129.90, 'casaca_denim.jpg');
