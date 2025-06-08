# 📱 scripts de la abse de datos 

# Esquema de Base de Datos MySQL para Chatbot Tienda Tecnológica

---

## Tabla `productos`

```sql
CREATE TABLE productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    categoria VARCHAR(50) NOT NULL COMMENT 'celulares, laptops, impresoras, etc.',
    descripcion TEXT,
    precio_actual DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL,
    especificaciones JSON,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

- **id**: Identificador único y auto incremental para cada producto.
- **nombre**: Nombre del producto (máximo 100 caracteres).
- **categoria**: Categoría a la que pertenece el producto, con ejemplo de valores como celulares, laptops, impresoras, etc.
- **descripcion**: Descripción detallada del producto.
- **precio_actual**: Precio vigente del producto con dos decimales.
- **stock**: Cantidad disponible en inventario.
- **especificaciones**: Campo JSON que permite almacenar características técnicas flexibles y variables para cada producto.
- **fecha_creacion**: Fecha y hora en que se registró el producto; por defecto toma la fecha y hora actual automáticamente.

---
## Tabla `precios_historicos`

```sql
CREATE TABLE precios_historicos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    producto_id INT NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

```

- **id**: Identificador único y auto incremental para cada registro de precio histórico.
- **producto_id**: Identificador del producto al que pertenece el precio; es una clave foránea que referencia a la tabla `productos`.
- **precio**: Precio registrado en esa fecha histórica.
- **fecha_registro**: Fecha y hora en que se registró ese precio; por defecto toma la fecha y hora actual automáticamente.

---
## Tabla `predicciones_precios`

```sql
CREATE TABLE predicciones_precios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    producto_id INT NOT NULL,
    precio_predicho DECIMAL(10,2) NOT NULL,
    fecha_prediccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_predicha DATE NOT NULL COMMENT 'fecha para la que se predice el precio',
    confianza DECIMAL(5,2) COMMENT 'porcentaje de confianza en la predicción',
    FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

```

- **id**: Identificador único y auto incremental para cada predicción.
- **producto_id**: Identificador del producto al que pertenece la predicción; clave foránea que referencia a `productos`.
- **precio_predicho**: Precio estimado o predicho para una fecha futura.
- **fecha_prediccion**: Fecha y hora en que se hizo la predicción; por defecto toma la fecha y hora actual automáticamente.
- **fecha_predicha**: Fecha futura para la cual se realiza la predicción del precio.
- **confianza**: Porcentaje que indica el nivel de confianza en la predicción realizada.

---
## Tabla `interacciones_chatbot`

```sql
CREATE TABLE interacciones_chatbot (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id VARCHAR(50) NOT NULL COMMENT 'ID de Telegram',
    mensaje TEXT NOT NULL,
    respuesta TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    presupuesto DECIMAL(10,2) COMMENT 'si fue proporcionado'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

```

- **id**: Identificador único y auto incremental para cada interacción.
- **usuario_id**: Identificador del usuario en Telegram (u otro canal), para identificar la conversación.
- **mensaje**: Texto o contenido enviado por el usuario.
- **respuesta**: Texto o contenido que el chatbot respondió al usuario.
- **timestamp**: Fecha y hora en que ocurrió la interacción; por defecto toma la fecha y hora actual automáticamente.
- **presupuesto**: Monto opcional que el usuario haya proporcionado durante la conversación, si aplica.

---
## Tabla `estos son algunos de los datos que se peuden utilzoiar como prueba (no son todos los incluidos por tema de espacio)`

```sql
INSERT INTO productos (nombre, categoria, descripcion, precio_actual, stock, especificaciones) VALUES
-- Celulares
('iPhone 13 Pro', 'celulares', 'Apple iPhone 13 Pro 128GB Azul Sierra', 999.99, 25, 
 '{"pantalla": "6.1 pulgadas", "ram": "6GB", "almacenamiento": "128GB", "camara": "Triple 12MP", "sistema": "iOS 15"}'),
('Samsung Galaxy S21', 'celulares', 'Samsung Galaxy S21 5G 128GB Phantom Gray', 799.99, 30, 
 '{"pantalla": "6.2 pulgadas", "ram": "8GB", "almacenamiento": "128GB", "camara": "Triple 64MP", "sistema": "Android 11"}'),
('Xiaomi Redmi Note 10', 'celulares', 'Xiaomi Redmi Note 10 128GB 6GB RAM Onyx Gray', 249.99, 50, 
 '{"pantalla": "6.43 pulgadas", "ram": "6GB", "almacenamiento": "128GB", "camara": "Cuádruple 48MP", "sistema": "Android 11"}'),

-- Laptops
('MacBook Pro 14" M1 Pro', 'laptops', 'Apple MacBook Pro 14" Chip M1 Pro 16GB 512GB SSD', 1999.99, 15, 
 '{"pantalla": "14.2 pulgadas", "procesador": "Apple M1 Pro", "ram": "16GB", "almacenamiento": "512GB SSD", "graficos": "16-core GPU"}'),
('Dell XPS 13', 'laptops', 'Dell XPS 13 9310 13.4" FHD+ i7 16GB 512GB SSD', 1299.99, 20, 
 '{"pantalla": "13.4 pulgadas", "procesador": "Intel Core i7-1185G7", "ram": "16GB", "almacenamiento": "512GB SSD", "graficos": "Intel Iris Xe"}'),

-- Impresoras
('HP LaserJet Pro M404dn', 'impresoras', 'Impresora láser monocromática HP LaserJet Pro M404dn', 299.99, 25, 
 '{"tipo": "láser", "color": "monocromática", "velocidad": "40 ppm", "resolucion": "1200 x 1200 dpi", "conectividad": "Ethernet, USB"}'),
('Epson EcoTank ET-4760', 'impresoras', 'Impresora multifunción de tanque de tinta Epson EcoTank ET-4760', 399.99, 18, 
 '{"tipo": "inyección de tinta", "color": "color", "velocidad": "15 ppm", "resolucion": "4800 x 1200 dpi", "conectividad": "Wi-Fi, Ethernet, USB"}');

-- Insertar precios históricos
INSERT INTO precios_historicos (producto_id, precio, fecha_registro) VALUES
-- Para iPhone 13 Pro
(1, 1099.99, '2023-01-15 10:00:00'),
(1, 1049.99, '2023-02-20 10:00:00'),
(1, 999.99, '2023-03-10 10:00:00'),

-- Para Samsung Galaxy S21
(2, 849.99, '2023-01-10 10:00:00'),
(2, 799.99, '2023-03-05 10:00:00'),

-- Para MacBook Pro
(4, 2199.99, '2023-01-10 10:00:00'),
(4, 1999.99, '2023-03-01 10:00:00');

-- Insertar predicciones de precios
INSERT INTO predicciones_precios (producto_id, precio_predicho, fecha_predicha, confianza) VALUES
(1, 979.99, '2023-05-15', 85.5),
(2, 779.99, '2023-05-20', 82.3),
(4, 1949.99, '2023-06-01', 87.2);

-- Insertar interacciones con el chatbot
INSERT INTO interacciones_chatbot (usuario_id, mensaje, respuesta, presupuesto) VALUES
('user123', 'Tengo un presupuesto de 1000 dólares', 'Te recomiendo estos productos...', 1000.00),
('user456', 'Qué laptops tienen?', 'Estas son nuestras laptops destacadas...', NULL),
('user789', 'iPhone 13 Pro tiene descuento?', 'Actualmente cuesta $999.99...', NULL);

INSERT INTO productos (nombre, categoria, descripcion, precio_actual, stock, especificaciones) VALUES
-- 1. Tablets (20 productos)
('iPad Pro 12.9"', 'tablets', 'Apple iPad Pro 12.9" 128GB Wi-Fi Space Gray', 1099.99, 18,
 '{"pantalla": "12.9 pulgadas", "almacenamiento": "128GB", "sistema": "iPadOS 15", "chip": "M1"}'),
('Samsung Galaxy Tab S8', 'tablets', 'Samsung Galaxy Tab S8 11" 128GB Wi-Fi Plata', 699.99, 22,
 '{"pantalla": "11 pulgadas", "almacenamiento": "128GB", "sistema": "Android 12", "procesador": "Snapdragon 8 Gen 1"}'),
('Lenovo Tab P11 Pro', 'tablets', 'Lenovo Tab P11 Pro 11.5" 128GB Gris', 499.99, 15,
 '{"pantalla": "11.5 pulgadas OLED", "almacenamiento": "128GB", "sistema": "Android 10"}'),
('Huawei MatePad Pro', 'tablets', 'Huawei MatePad Pro 12.6" 256GB Gris', 799.99, 12,
 '{"pantalla": "12.6 pulgadas", "almacenamiento": "256GB", "sistema": "HarmonyOS 2"}'),
('Amazon Fire HD 10', 'tablets', 'Amazon Fire HD 10 10.1" 32GB Negro', 149.99, 30,
 '{"pantalla": "10.1 pulgadas", "almacenamiento": "32GB", "sistema": "Fire OS"}'),
('Microsoft Surface Pro 8', 'tablets', 'Surface Pro 8 13" i5 8GB 128GB Platino', 1099.99, 10,
 '{"pantalla": "13 pulgadas", "procesador": "Intel Core i5", "ram": "8GB", "almacenamiento": "128GB SSD"}'),
('Xiaomi Pad 5', 'tablets', 'Xiaomi Pad 5 11" 128GB Wi-Fi Negro', 399.99, 20,
 '{"pantalla": "11 pulgadas", "almacenamiento": "128GB", "sistema": "Android 11"}'),
('Realme Pad', 'tablets', 'Realme Pad 10.4" 64GB Wi-Fi Gris', 229.99, 25,
 '{"pantalla": "10.4 pulgadas", "almacenamiento": "64GB", "sistema": "Android 11"}'),
('Oppo Pad Air', 'tablets', 'Oppo Pad Air 10.36" 64GB Wi-Fi Azul', 279.99, 18,
 '{"pantalla": "10.36 pulgadas", "almacenamiento": "64GB", "sistema": "Android 11"}'),
('Alldocube iPlay 40', 'tablets', 'Alldocube iPlay 40 10.4" 128GB Azul', 199.99, 15,
 '{"pantalla": "10.4 pulgadas", "almacenamiento": "128GB", "sistema": "Android 10"}'),

-- 2. Smartwatches (20 productos)
('Apple Watch Series 8', 'smartwatches', 'Apple Watch Series 8 GPS 45mm Medianoche', 429.99, 25,
 '{"pantalla": "1.9 pulgadas", "conectividad": "GPS", "resistencia": "50m", "bateria": "18h"}'),
('Samsung Galaxy Watch 5', 'smartwatches', 'Samsung Galaxy Watch 5 44mm Bluetooth Grafito', 279.99, 20,
 '{"pantalla": "1.4 pulgadas", "conectividad": "Bluetooth", "resistencia": "50m", "bateria": "50h"}'),
('Huawei Watch GT 3', 'smartwatches', 'Huawei Watch GT 3 46mm Negro', 199.99, 18,
 '{"pantalla": "1.43 pulgadas", "bateria": "14 días", "resistencia": "50m"}'),
('Amazfit GTR 4', 'smartwatches', 'Amazfit GTR 4 1.43" Negro', 199.99, 15,
 '{"pantalla": "1.43 pulgadas", "bateria": "14 días", "resistencia": "50m"}'),
('Garmin Venu 2', 'smartwatches', 'Garmin Venu 2 1.3" Slate', 399.99, 12,
 '{"pantalla": "1.3 pulgadas", "bateria": "11 días", "resistencia": "50m"}'),

-- 3. Auriculares (20 productos)
('Apple AirPods Pro 2', 'auriculares', 'Apple AirPods Pro (2da generación)', 249.99, 30,
 '{"tipo": "inalámbricos", "cancelacion_ruido": "sí", "conexion": "Bluetooth 5.3"}'),
('Sony WH-1000XM5', 'auriculares', 'Sony WH-1000XM5 Negro', 399.99, 15,
 '{"tipo": "over-ear", "cancelacion_ruido": "sí", "bateria": "30h"}'),
('Bose QuietComfort 45', 'auriculares', 'Bose QuietComfort 45 Negro', 329.99, 18,
 '{"tipo": "over-ear", "cancelacion_ruido": "sí", "bateria": "24h"}'),

-- 4. Televisores (20 productos)
('Samsung QN90B Neo QLED', 'televisores', 'Samsung QN90B 55" Neo QLED 4K Smart TV', 1499.99, 10,
 '{"pantalla": "55 pulgadas", "resolucion": "4K", "tecnologia": "Neo QLED"}'),
('LG C2 OLED', 'televisores', 'LG C2 65" OLED evo 4K Smart TV', 1999.99, 8,
 '{"pantalla": "65 pulgadas", "resolucion": "4K", "tecnologia": "OLED"}'),

-- 5. Consolas (20 productos)
('PlayStation 5', 'consolas', 'Sony PlayStation 5 Standard Edition', 499.99, 5,
 '{"almacenamiento": "825GB SSD", "resolucion": "8K", "formato": "Digital"}'),
('Xbox Series X', 'consolas', 'Microsoft Xbox Series X 1TB', 499.99, 7,
 '{"almacenamiento": "1TB SSD", "resolucion": "8K"}');

-- Más interacciones con el chatbot (20 adicionales)
INSERT INTO interacciones_chatbot (usuario_id, mensaje, respuesta, presupuesto) VALUES
('user124', 'Qué tablets Android recomiendan?', 'Tenemos estas opciones de tablets Android...', NULL),
('user125', 'Busco smartwatch con buena batería', 'Te recomiendo estos smartwatches con larga duración...', NULL),
('user126', 'Auriculares con cancelación de ruido', 'Estos son nuestros auriculares con ANC...', NULL),
('user127', 'TV OLED 55 pulgadas', 'Estas son nuestras TVs OLED de 55"...', NULL),
('user128', 'Consola para regalo', 'Tenemos estas opciones de consolas...', NULL),
('user129', 'Tengo $300 para auriculares', 'Con ese presupuesto te recomendamos...', 300.00),
('user130', 'Tablet económica para niños', 'Estas tablets son ideales para niños...', NULL),
('user131', 'Smartwatch para nadar', 'Estos relojes son resistentes al agua...', NULL),
('user132', 'TV con mejor relación calidad-precio', 'Estos televisores ofrecen lo mejor por su precio...', NULL),
('user133', 'Comparativa PS5 vs Xbox', 'Estas son las diferencias principales...', NULL),
('user134', 'Tablet con lápiz incluido', 'Estas tablets incluyen stylus...', NULL),
('user135', 'Auriculares deportivos', 'Estos auriculares son ideales para deporte...', NULL),
('user136', 'TV para gaming', 'Estos televisores tienen baja latencia...', NULL),
('user137', 'Consola portátil', 'Tenemos estas opciones portátiles...', NULL),
('user138', 'Tablet Windows', 'Estas tablets ejecutan Windows...', NULL),
('user139', 'Presupuesto 200 para smartwatch', 'Con $200 puedes conseguir...', 200.00),
('user140', 'Auriculares baratos', 'Estas son nuestras opciones económicas...', NULL),
('user141', 'TV pequeño para cocina', 'Te recomendamos estos modelos compactos...', NULL),
('user142', 'Accesorios para PS5', 'Tenemos estos accesorios...', NULL),
('user143', 'Tablet con 5G', 'Estas tablets incluyen conectividad 5G...', NULL);

-- Insertar precios históricos para los nuevos productos
INSERT INTO precios_historicos (producto_id, precio, fecha_registro) VALUES
-- Para iPad Pro
(8, 1199.99, '2023-01-10'),
(8, 1149.99, '2023-02-15'),
(8, 1099.99, '2023-03-20'),

-- Para Galaxy Tab S8
(9, 749.99, '2023-01-05'),
(9, 699.99, '2023-03-10'),

-- Para Apple Watch
(28, 449.99, '2023-02-01'),
(28, 429.99, '2023-04-01');

-- Insertar predicciones para nuevos productos
INSERT INTO predicciones_precios (producto_id, precio_predicho, fecha_predicha, confianza) VALUES
(8, 1049.99, '2023-06-15', 82.5),
(9, 679.99, '2023-06-20', 85.0),
(28, 419.99, '2023-07-01', 88.3);

```
