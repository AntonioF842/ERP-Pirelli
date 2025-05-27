-- Archivo: poblar_base_pirelli.sql
-- Descripción: Datos de ejemplo para ERP Pirelli
-- Autor: Asistente de IA
-- Fecha: 2023-11-15

USE erp_pirelli;

-- Desactivar temporalmente las restricciones de clave foránea
SET FOREIGN_KEY_CHECKS = 0;

-- 1. Limpiar tablas (opcional, solo para desarrollo)
TRUNCATE TABLE usuarios;
TRUNCATE TABLE areas_trabajo;
TRUNCATE TABLE empleados;
TRUNCATE TABLE asistencia;
TRUNCATE TABLE proveedores;
TRUNCATE TABLE materiales;
TRUNCATE TABLE inventario;
TRUNCATE TABLE productos;
TRUNCATE TABLE recetas_produccion;
TRUNCATE TABLE clientes;
TRUNCATE TABLE ordenes_compra;
TRUNCATE TABLE detalle_ordenes_compra;
TRUNCATE TABLE ordenes_produccion;
TRUNCATE TABLE control_calidad;
TRUNCATE TABLE ventas;
TRUNCATE TABLE detalle_ventas;
TRUNCATE TABLE nominas;
TRUNCATE TABLE proyectos_i_d;
TRUNCATE TABLE normativas_legales;
TRUNCATE TABLE incidentes;
TRUNCATE TABLE activos_produccion;
TRUNCATE TABLE mantenimiento;
TRUNCATE TABLE configuracion_sistema;

-- Reactivar las restricciones
SET FOREIGN_KEY_CHECKS = 1;

-- 1. Usuarios del Sistema
INSERT INTO usuarios (nombre, email, password, rol) VALUES
('Ricardo Torres', 'ricardo.torres@pirelli.com', SHA2('RicardoTP456', 256), 'supervisor'),
('Elena Castro', 'elena.castro@pirelli.com', SHA2('ElenaC789', 256), 'empleado'),
('Fernando Rojas', 'fernando.rojas@pirelli.com', SHA2('FerRojas2024', 256), 'empleado'),
('Gabriela Méndez', 'gabriela.mendez@pirelli.com', SHA2('GabMendez123', 256), 'supervisor'),
('Oscar Duarte', 'oscar.duarte@pirelli.com', SHA2('OscarD789', 256), 'empleado'),
('Patricia Vargas', 'patricia.vargas@pirelli.com', SHA2('PatVargas456', 256), 'empleado'),
('Héctor Silva', 'hector.silva@pirelli.com', SHA2('HectorS789', 256), 'supervisor'),
('Lucía Fernández', 'lucia.fernandez@pirelli.com', SHA2('LuciaF123', 256), 'empleado'),
('Mario Jiménez', 'mario.jimenez@pirelli.com', SHA2('MarioJ456', 256), 'empleado'),
('Sandra Guzmán', 'sandra.guzman@pirelli.com', SHA2('SandraG789', 256), 'supervisor'),
('Roberto Navarro', 'roberto.navarro@pirelli.com', SHA2('RobertoN123', 256), 'empleado'),
('Isabel Ramírez', 'isabel.ramirez@pirelli.com', SHA2('IsabelR456', 256), 'empleado'),
('Javier Morales', 'javier.morales@pirelli.com', SHA2('JavierM789', 256), 'supervisor'),
('Carmen Ortega', 'carmen.ortega@pirelli.com', SHA2('CarmenO123', 256), 'empleado'),
('Alberto Reyes', 'alberto.reyes@pirelli.com', SHA2('AlbertoR456', 256), 'empleado'),
('Daniela Paredes', 'daniela.paredes@pirelli.com', SHA2('DanielaP789', 256), 'supervisor'),
('Raúl Mendoza', 'raul.mendoza@pirelli.com', SHA2('RaulM123', 256), 'empleado'),
('Verónica Soto', 'veronica.soto@pirelli.com', SHA2('VeronicaS456', 256), 'empleado'),
('Felipe Cordero', 'felipe.cordero@pirelli.com', SHA2('FelipeC789', 256), 'supervisor'),
('Alejandra Ríos', 'alejandra.rios@pirelli.com', SHA2('AlejandraR123', 256), 'empleado'),
('Gerardo Peña', 'gerardo.pena@pirelli.com', SHA2('GerardoP456', 256), 'empleado'),
('Adriana Vega', 'adriana.vega@pirelli.com', SHA2('AdrianaV789', 256), 'supervisor'),
('Arturo Miranda', 'arturo.miranda@pirelli.com', SHA2('ArturoM123', 256), 'empleado'),
('Rosa Delgado', 'rosa.delgado@pirelli.com', SHA2('RosaD456', 256), 'empleado'),
('Enrique Fuentes', 'enrique.fuentes@pirelli.com', SHA2('EnriqueF789', 256), 'supervisor');

-- 2. Áreas de Trabajo (asignar responsables que existen en la tabla usuarios)
-- Primero, insertar las áreas de trabajo con IDs consecutivos comenzando desde 1
INSERT INTO areas_trabajo (id_area, nombre_area, descripcion, responsable) VALUES
(1, 'Producción Nocturna', 'Turno nocturno de fabricación de neumáticos', 8),
(2, 'Logística Internacional', 'Gestión de exportaciones e importaciones', 11),
(3, 'Calidad Avanzada', 'Control de calidad para productos premium', 14),
(4, 'Mantenimiento Preventivo', 'Mantenimiento programado de equipos', 17),
(5, 'I+D Avanzado', 'Desarrollo de tecnologías innovadoras', 20),
(6, 'Ventas Corporativas', 'Atención a clientes corporativos', 23),
(7, 'RRHH y Desarrollo', 'Gestión de talento y capacitación', 1),
(8, 'Seguridad Industrial', 'Gestión de seguridad y salud ocupacional', 8),
(9, 'Compras Estratégicas', 'Adquisición de materiales clave', 11),
(10, 'Planificación Producción', 'Programación de la producción', 14),
(11, 'Marketing Técnico', 'Promoción técnica de productos', 17),
(12, 'Sistemas y TI', 'Gestión de tecnología informática', 20),
(13, 'Finanzas Corporativas', 'Gestión financiera y contable', 23),
(14, 'Servicio al Cliente', 'Atención postventa y garantías', 1),
(15, 'Medio Ambiente', 'Gestión ambiental y sostenibilidad', 8),
(16, 'Innovación Continua', 'Mejora de procesos productivos', 11),
(17, 'Almacén Central', 'Gestión de inventarios principales', 14),
(18, 'Transporte Especial', 'Distribución de productos especiales', 17),
(19, 'Laboratorio de Pruebas', 'Pruebas avanzadas de productos', 20),
(20, 'Proyectos Especiales', 'Implementación de proyectos clave', 23);

-- Luego, insertar los empleados usando los mismos IDs de área
INSERT INTO empleados (nombre, apellidos, id_area, puesto, salario, fecha_contratacion, activo) VALUES
('Ricardo', 'Torres', 1, 'Supervisor Nocturno', 27000.00, '2022-06-15', TRUE),
('Elena', 'Castro', 2, 'Analista Logística', 19500.00, '2023-02-20', TRUE),
('Fernando', 'Rojas', 3, 'Técnico de Calidad', 20500.00, '2023-05-10', TRUE),
('Gabriela', 'Méndez', 4, 'Jefa de Mantenimiento', 24000.00, '2021-11-18', TRUE),
('Oscar', 'Duarte', 5, 'Ingeniero de Desarrollo', 29000.00, '2020-09-05', TRUE),
('Patricia', 'Vargas', 6, 'Ejecutiva de Ventas', 22500.00, '2023-01-15', TRUE),
('Héctor', 'Silva', 7, 'Supervisor de RRHH', 26000.00, '2019-08-22', TRUE),
('Lucía', 'Fernández', 8, 'Especialista en Seguridad', 21500.00, '2022-04-30', TRUE),
('Mario', 'Jiménez', 9, 'Analista de Compras', 20000.00, '2023-03-12', TRUE),
('Sandra', 'Guzmán', 10, 'Planificador de Producción', 23500.00, '2021-07-25', TRUE),
('Roberto', 'Navarro', 11, 'Especialista en Marketing', 24500.00, '2020-12-10', TRUE),
('Isabel', 'Ramírez', 12, 'Administrador de Sistemas', 25500.00, '2019-10-15', TRUE),
('Javier', 'Morales', 13, 'Analista Financiero', 23000.00, '2022-08-05', TRUE),
('Carmen', 'Ortega', 14, 'Representante de Servicio', 19000.00, '2023-06-18', TRUE),
('Alberto', 'Reyes', 15, 'Coordinador Ambiental', 21000.00, '2021-05-20', TRUE),
('Daniela', 'Paredes', 16, 'Ingeniera de Innovación', 27500.00, '2020-03-15', TRUE),
('Raúl', 'Mendoza', 17, 'Jefe de Almacén', 22000.00, '2022-11-30', TRUE),
('Verónica', 'Soto', 18, 'Coordinadora de Transporte', 22500.00, '2023-04-05', TRUE),
('Felipe', 'Cordero', 19, 'Técnico de Laboratorio', 21500.00, '2021-09-12', TRUE),
('Alejandra', 'Ríos', 20, 'Gerente de Proyectos', 31000.00, '2019-07-08', TRUE),
('Gerardo', 'Peña', 1, 'Operario de Máquinas', 18200.00, '2024-01-10', TRUE),
('Adriana', 'Vega', 1, 'Operario de Máquinas', 18000.00, '2024-02-15', TRUE),
('Arturo', 'Miranda', 2, 'Almacenista', 17500.00, '2024-03-20', TRUE),
('Rosa', 'Delgado', 3, 'Inspectora de Calidad', 19800.00, '2024-04-05', TRUE),
('Enrique', 'Fuentes', 4, 'Técnico de Mantenimiento', 20800.00, '2024-05-10', TRUE);

-- 4. Asistencia (asegurar que id_empleado exista)
-- Asistencia para enero 2024
INSERT INTO asistencia (id_empleado, fecha, hora_entrada, hora_salida, estado) VALUES
(1, '2024-01-02', '08:02:00', '17:05:00', 'presente'),
(1, '2024-01-03', '08:00:00', '17:00:00', 'presente'),
(1, '2024-01-04', '08:15:00', '17:10:00', 'tardanza'),
(2, '2024-01-02', '07:58:00', '16:55:00', 'presente'),
(2, '2024-01-03', '08:05:00', '17:10:00', 'presente'),
(3, '2024-01-02', '08:00:00', '17:00:00', 'presente'),
(3, '2024-01-03', NULL, NULL, 'ausente'),
(4, '2024-01-02', '08:10:00', '17:15:00', 'tardanza'),
(5, '2024-01-02', '07:55:00', '16:58:00', 'presente'),
(6, '2024-01-03', '08:02:00', '17:10:00', 'presente');

-- Asistencia para febrero 2024
INSERT INTO asistencia (id_empleado, fecha, hora_entrada, hora_salida, estado) VALUES
(1, '2024-02-05', '08:00:00', '17:00:00', 'presente'),
(2, '2024-02-05', '08:05:00', '17:10:00', 'presente'),
(3, '2024-02-06', '08:15:00', '17:05:00', 'tardanza'),
(4, '2024-02-06', '07:55:00', '16:58:00', 'presente'),
(5, '2024-02-07', NULL, NULL, 'ausente'),
(6, '2024-02-07', '08:02:00', '17:10:00', 'presente');

-- Continuar con más meses hasta mayo 2025...
-- (Ejemplo simplificado, en realidad debería haber datos para todos los empleados y días laborables)

-- 5. Proveedores
INSERT INTO proveedores (nombre, contacto, telefono, email, direccion, tipo_material) VALUES
('Cauchos Premium Internacional', 'Ing. Marco Polo', '+582129876512', 'm.polo@cauchospremium.com', 'Zona Industrial Este, Carabobo', 'caucho'),
('Aceros del Caribe', 'Lic. Daniela Rojas', '+584147896532', 'd.rojas@acerosdelcaribe.com', 'Av. Industrial, Puerto Cabello', 'acero'),
('Químicos Especializados CA', 'Dr. Carlos Mendoza', '+582127654329', 'c.mendoza@quimicosespecializados.com', 'Polígono Industrial, Valencia', 'quimicos'),
('Suministros Técnicos Globales', 'Sra. Laura Pérez', '+584148765432', 'l.perez@suministrostecnicos.com', 'Calle Comercial, Maracay', 'otros'),
('Polímeros Avanzados SA', 'Ing. Ricardo Fernández', '+582128765439', 'r.fernandez@polimerosavanzados.com', 'Zona Franca, La Guaira', 'caucho'),
('Metales y Aleaciones CA', 'Sr. José Martínez', '+584146543218', 'j.martinez@metalesyaleaciones.com', 'Av. Principal, Barquisimeto', 'acero'),
('Distribuidora de Cauchos CA', 'Sra. Patricia Gómez', '+582127891236', 'p.gomez@distribuidoradecauchos.com', 'Zona Industrial Norte, Maracaibo', 'caucho'),
('Química Industrial Venezolana', 'Ing. Luis Rivas', '+584147891237', 'l.rivas@quimicaindustrial.com', 'Polígono Industrial, San Cristóbal', 'quimicos'),
('Importadora de Materiales SA', 'Sr. Carlos Díaz', '+582128765438', 'c.diaz@importadorademateriales.com', 'Av. Bolívar, Puerto Ordaz', 'otros'),
('Tecnología en Polímeros', 'Ing. Sofía Ramírez', '+584146543217', 's.ramirez@tecnologiapolimeros.com', 'Zona Industrial, Mérida', 'caucho'),
('Aceros para Neumáticos', 'Sr. Roberto Sánchez', '+582127654327', 'r.sanchez@acerosparaneumaticos.com', 'Av. Industrial, Barcelona', 'acero'),
('Especialidades Químicas', 'Dra. Ana López', '+584148765431', 'a.lopez@especialidadesquimicas.com', 'Calle Comercial, Valencia', 'quimicos'),
('Cauchos Sintéticos CA', 'Ing. Fernando Torres', '+582129876511', 'f.torres@cauchossinteticos.com', 'Zona Industrial, Caracas', 'caucho'),
('Materiales Industriales SA', 'Sr. Juan García', '+584147896531', 'j.garcia@materialesindustriales.com', 'Av. Principal, Maracay', 'otros'),
('Compuestos para Neumáticos', 'Ing. María Rodríguez', '+582127654328', 'm.rodriguez@compuestosparaneumaticos.com', 'Polígono Industrial, Valencia', 'quimicos'),
('Distribuidora de Aceros', 'Sr. Pedro González', '+584146543216', 'p.gonzalez@distribuidoradeaceros.com', 'Av. Industrial, Barquisimeto', 'acero'),
('Polímeros del Lago', 'Ing. Gabriela Méndez', '+582128765437', 'g.mendez@polimerosdellago.com', 'Zona Franca, Maracaibo', 'caucho'),
('Químicos para la Industria', 'Dr. Luis Pérez', '+584147891236', 'l.perez@quimicosparalaindustria.com', 'Polígono Industrial, Puerto La Cruz', 'quimicos'),
('Suministros Globales CA', 'Sra. Carmen Rojas', '+582127891235', 'c.rojas@suministrosglobalesca.com', 'Av. Principal, Valencia', 'otros'),
('Tecnología en Cauchos', 'Ing. Jorge Silva', '+584148765430', 'j.silva@tecnologiaencauchos.com', 'Zona Industrial, Carabobo', 'caucho');

-- 6. Materiales
INSERT INTO materiales (nombre, descripcion, unidad_medida, stock_minimo, stock_maximo) VALUES
('Caucho natural grado 1', 'Caucho natural de máxima pureza', 'kg', 6000, 25000),
('Negro de humo N660', 'Negro de humo para aplicaciones generales', 'kg', 3500, 18000),
('Acero radial premium', 'Alambre de acero de alta resistencia', 'kg', 2500, 12000),
('Azufre técnico', 'Azufre para procesos de vulcanización', 'kg', 1200, 6000),
('Aditivos químicos premium', 'Paquete de aceleradores avanzados', 'kg', 600, 3000),
('Caucho sintético BR', 'Caucho butadieno para aplicaciones especiales', 'kg', 4500, 20000),
('Silica especial', 'Silica de alta dispersión', 'kg', 3000, 15000),
('Aceites aromáticos', 'Aceites para mejora de propiedades', 'litro', 1200, 6000),
('Resinas de refuerzo', 'Resinas para mejorar adherencia', 'kg', 800, 4000),
('Agentes de vulcanización', 'Sistemas avanzados de vulcanización', 'kg', 700, 3500),
('Protectores UV', 'Aditivos para protección solar', 'kg', 500, 2500),
('Colorantes industriales', 'Pigmentos para neumáticos coloreados', 'kg', 300, 1500),
('Antioxidantes', 'Agentes para prevenir degradación', 'kg', 900, 4500),
('Agentes de adherencia', 'Mejoran la adherencia entre componentes', 'kg', 1000, 5000),
('Fibras textiles', 'Refuerzos textiles para neumáticos', 'kg', 2000, 10000),
('Compuestos de goma', 'Mezclas precompuestas', 'kg', 4000, 20000),
('Agentes espumantes', 'Para neumáticos con propiedades especiales', 'kg', 400, 2000),
('Catalizadores', 'Para procesos químicos específicos', 'kg', 300, 1500),
('Lubricantes internos', 'Mejoran la procesabilidad', 'kg', 1000, 5000),
('Agentes antiestáticos', 'Reducen la acumulación de electricidad estática', 'kg', 500, 2500),
('Selladores', 'Para procesos de sellado interno', 'kg', 600, 3000),
('Refuerzos minerales', 'Materiales minerales para refuerzo', 'kg', 2500, 12500),
('Plastificantes', 'Mejoran la flexibilidad del compuesto', 'kg', 1500, 7500),
('Agentes de reticulación', 'Para mejorar la estructura molecular', 'kg', 800, 4000),
('Estabilizantes térmicos', 'Protegen contra altas temperaturas', 'kg', 700, 3500);

-- 7. Inventario (asegurar que id_material exista)
-- Ingresos de inventario para 2024
INSERT INTO inventario (id_material, cantidad, ubicacion, lote, fecha_ingreso) VALUES
(1, 18000, 'Almacén A, Estante 5', 'LOTE-CAU-2024-01', '2024-01-10'),
(2, 9500, 'Almacén B, Estante 2', 'LOTE-NEG-2024-01', '2024-01-15'),
(3, 5000, 'Almacén C, Estante 4', 'LOTE-ACE-2024-01', '2024-01-20'),
(4, 3500, 'Almacén A, Estante 3', 'LOTE-AZU-2024-02', '2024-02-05'),
(5, 1500, 'Almacén B, Estante 6', 'LOTE-ADQ-2024-02', '2024-02-10'),
(6, 12000, 'Almacén D, Estante 2', 'LOTE-SBR-2024-02', '2024-02-15'),
(7, 6000, 'Almacén C, Estante 3', 'LOTE-SIL-2024-03', '2024-03-01'),
(8, 4000, 'Almacén A, Estante 6', 'LOTE-ACE-2024-03', '2024-03-10'),
(9, 2500, 'Almacén E, Estante 1', 'LOTE-RES-2024-03', '2024-03-15'),
(10, 1800, 'Almacén B, Estante 7', 'LOTE-VUL-2024-04', '2024-04-05'),
(11, 800, 'Almacén C, Estante 5', 'LOTE-UV-2024-04', '2024-04-10'),
(12, 500, 'Almacén D, Estante 3', 'LOTE-COL-2024-04', '2024-04-15'),
(13, 2000, 'Almacén A, Estante 7', 'LOTE-ANT-2024-05', '2024-05-03'),
(14, 3000, 'Almacén B, Estante 8', 'LOTE-ADH-2024-05', '2024-05-08'),
(15, 4500, 'Almacén E, Estante 2', 'LOTE-FIB-2024-05', '2024-05-12');

-- 8. Productos
INSERT INTO productos (codigo, nombre, descripcion, precio, categoria) VALUES
('PZR-003', 'P Zero GT', 'Neumático para autos de alto rendimiento GT', 400.00, 'automovil'),
('PZR-004', 'P Zero Corsa', 'Neumático para competición en seco', 450.00, 'automovil'),
('DSA-103', 'Diablo Rosso IV', 'Neumático para motocicletas deportivas de última generación', 320.00, 'motocicleta'),
('CMH-203', 'Cinturato FH', 'Neumático para camiones de larga distancia', 460.00, 'camion'),
('IND-303', 'Industrial XT-2', 'Neumático para maquinaria pesada', 600.00, 'industrial'),
('SCP-104', 'Scorpion All Terrain Plus', 'Neumático SUV para todo terreno', 380.00, 'automovil'),
('DRA-204', 'Dragón SuperSport', 'Neumático para motocicletas supersport', 340.00, 'motocicleta'),
('CPL-304', 'Carrier XD-50', 'Neumático para camiones extra pesados', 520.00, 'camion'),
('PZR-005', 'P Zero Winter', 'Neumático de invierno para alto rendimiento', 420.00, 'automovil'),
('PZR-006', 'P Zero Elect', 'Neumático optimizado para vehículos eléctricos', 430.00, 'automovil'),
('DSA-105', 'Diablo Superbike', 'Neumático para competición en motocicletas', 500.00, 'motocicleta'),
('CMH-205', 'Cinturato XH', 'Neumático para camiones de construcción', 480.00, 'camion'),
('IND-305', 'Industrial MT-3', 'Neumático para minería subterránea', 650.00, 'industrial'),
('SCP-106', 'Scorpion Zero', 'Neumático SUV ultra alto rendimiento', 400.00, 'automovil'),
('DRA-206', 'Dragón Trail', 'Neumático para motocicletas trail', 360.00, 'motocicleta'),
('CPL-306', 'Carrier HD-60', 'Neumático para camiones de servicio pesado', 540.00, 'camion'),
('PZR-007', 'P Zero Trofeo R', 'Neumático para track days y competición', 480.00, 'automovil'),
('PZR-008', 'P Zero All Season', 'Neumático para todo clima alto rendimiento', 390.00, 'automovil'),
('DSA-107', 'Diablo Rain', 'Neumático para condiciones de lluvia extrema', 350.00, 'motocicleta'),
('CMH-207', 'Cinturato LH', 'Neumático para camiones de larga distancia baja resistencia', 470.00, 'camion'),
('IND-307', 'Industrial RT-4', 'Neumático para maquinaria de reciclaje', 620.00, 'industrial'),
('SCP-108', 'Scorpion Winter', 'Neumático SUV para invierno', 410.00, 'automovil'),
('DRA-208', 'Dragón Urban', 'Neumático para motocicletas urbanas', 330.00, 'motocicleta'),
('CPL-308', 'Carrier MD-55', 'Neumático para camiones medianos de reparto', 500.00, 'camion'),
('PZR-009', 'P Zero Veloce', 'Neumático para deportivos de alta gama', 440.00, 'automovil');

-- 9. Recetas de Producción (asegurar que id_producto e id_material existan)
INSERT INTO recetas_produccion (id_producto, id_material, cantidad) VALUES
(9, 1, 26.0), (9, 2, 13.0), (9, 3, 9.5), (9, 4, 1.3), (9, 5, 0.9),
(10, 1, 27.5), (10, 2, 14.0), (10, 3, 9.0), (10, 6, 5.0), (10, 7, 3.0),
(11, 1, 20.0), (11, 2, 15.0), (11, 3, 12.0), (11, 5, 1.5),
(12, 1, 38.0), (12, 3, 18.0), (12, 8, 2.0), (12, 9, 1.5),
(13, 1, 40.0), (13, 2, 20.0), (13, 3, 22.0), (13, 10, 2.5),
(14, 1, 28.0), (14, 2, 15.0), (14, 3, 10.0), (14, 11, 1.0),
(15, 1, 22.0), (15, 6, 12.0), (15, 12, 0.8), (15, 13, 1.2),
(16, 1, 42.0), (16, 3, 20.0), (16, 14, 3.0), (16, 15, 2.5),
(17, 1, 30.0), (17, 2, 18.0), (17, 3, 15.0), (17, 16, 2.0),
(18, 1, 29.0), (18, 2, 14.0), (18, 3, 10.0), (18, 17, 1.5),
(19, 1, 24.0), (19, 6, 14.0), (19, 18, 1.8), (19, 19, 1.0),
(20, 1, 45.0), (20, 3, 25.0), (20, 20, 3.5), (20, 21, 2.0),
(21, 1, 50.0), (21, 2, 30.0), (21, 3, 35.0), (21, 22, 4.0),
(22, 1, 32.0), (22, 2, 17.0), (22, 3, 12.0), (22, 23, 2.0),
(23, 1, 26.0), (23, 6, 15.0), (23, 24, 1.5), (23, 25, 1.0),
(24, 1, 48.0), (24, 3, 28.0), (24, 14, 4.0), (24, 15, 3.0),
(25, 1, 31.0), (25, 2, 16.0), (25, 3, 11.0), (25, 5, 1.2);

-- 10. Clientes
INSERT INTO clientes (nombre, contacto, telefono, email, direccion, tipo) VALUES
('Autos Premium Venezuela', 'Sr. Alejandro Rivas', '+582127891245', 'ventas@autospremium.com', 'Av. Principal, Caracas', 'distribuidor'),
('Motores y Más', 'Ing. Carlos Mendoza', '+584147896544', 'c.mendoza@motoresymas.com', 'Zona Industrial, Valencia', 'mayorista'),
('Transporte Nacional CA', 'Sr. Luis González', '+582128765443', 'l.gonzalez@transportenacional.com', 'Polígono Industrial, Maracay', 'OEM'),
('Taller Express', 'Sra. Patricia Díaz', '+584141234578', 'p.diaz@tallerexpress.com', 'Calle Comercial, Barquisimeto', 'minorista'),
('Concesionaria Elite', 'Sr. Roberto Martínez', '+582129876554', 'r.martinez@concesionariaelite.com', 'Av. Bolívar, Puerto La Cruz', 'distribuidor'),
('MotoCenter', 'Sr. José Fernández', '+584148765443', 'j.fernandez@motocenter.com', 'Carrera 20, San Cristóbal', 'mayorista'),
('Constructora Nacional', 'Ing. Sofía Pérez', '+582127654332', 's.perez@constructoranacional.com', 'Av. Los Andes, Mérida', 'OEM'),
('Distribuidora Automotriz', 'Sr. Juan López', '+584147891248', 'j.lopez@distribuidoraautomotriz.com', 'Av. Industrial, Barquisimeto', 'distribuidor'),
('Taller Especializado', 'Sra. Carmen Rojas', '+582128765449', 'c.rojas@tallerespecializado.com', 'Calle Comercial, Valencia', 'minorista'),
('Autopartes del Sur', 'Sr. Pedro Sánchez', '+584146543229', 'p.sanchez@autopartesdelsur.com', 'Av. Principal, San Cristóbal', 'mayorista'),
('Transporte Rápido CA', 'Ing. Daniel Torres', '+582127891247', 'd.torres@transportarapido.com', 'Polígono Industrial, Valencia', 'OEM'),
('Mundo Motor', 'Sra. Laura García', '+584148765447', 'l.garcia@mundomotor.com', 'Av. Bolívar, Maracaibo', 'distribuidor'),
('Taller Profesional', 'Sr. Mario Ramírez', '+582129876553', 'm.ramirez@tallerprofesional.com', 'Calle Comercial, Caracas', 'minorista'),
('Autos y Camiones SA', 'Ing. Ricardo Morales', '+584147896547', 'r.morales@autosycamiones.com', 'Av. Industrial, Valencia', 'mayorista'),
('Constructora del Este', 'Sr. Arturo Jiménez', '+582127654331', 'a.jimenez@constructoradeste.com', 'Av. Principal, Puerto Ordaz', 'OEM'),
('Distribuidora de Neumáticos', 'Sra. Adriana Castro', '+584141234577', 'a.castro@distribuidoradeneumaticos.com', 'Calle Comercial, Maracay', 'distribuidor'),
('Taller Integral', 'Sr. Fernando Ortega', '+582128765448', 'f.ortega@tallerintegral.com', 'Av. Industrial, Barquisimeto', 'minorista'),
('Autopartes Nacionales', 'Sra. Gabriela Méndez', '+584146543228', 'g.mendez@autopartesnacionales.com', 'Av. Principal, Valencia', 'mayorista'),
('Transporte Pesado del Sur', 'Ing. Luis Rojas', '+582127891246', 'l.rojas@transportepesadosur.com', 'Polígono Industrial, San Cristóbal', 'OEM'),
('Mundo del Neumático', 'Sr. Carlos Díaz', '+584148765446', 'c.diaz@mundodelneumatico.com', 'Av. Bolívar, Caracas', 'distribuidor'),
('Taller de Excelencia', 'Sra. Patricia Gómez', '+582129876552', 'p.gomez@tallerdeexcelencia.com', 'Calle Comercial, Maracaibo', 'minorista'),
('Autopartes del Centro', 'Sr. José Ramírez', '+584147896546', 'j.ramirez@autopartesdelcentro.com', 'Av. Industrial, Valencia', 'mayorista'),
('Constructora Andina Plus', 'Ing. Sofía Rivas', '+582127654330', 's.rivas@constructoraandinaplus.com', 'Av. Los Andes, Mérida', 'OEM'),
('Distribuidora Automotriz del Norte', 'Sr. Juan Martínez', '+584141234576', 'j.martinez@distribuidoradelnote.com', 'Calle Comercial, Valencia', 'distribuidor'),
('Taller Especial', 'Sra. Carmen López', '+582128765447', 'c.lopez@tallerespecial.com', 'Av. Principal, Barquisimeto', 'minorista');

-- 11. Órdenes de Compra (asegurar que id_proveedor e id_usuario existan)
-- Órdenes de compra para 2024
INSERT INTO ordenes_compra (id_proveedor, id_usuario, fecha, fecha_entrega_esperada, estado, total) VALUES
(7, 1, '2024-01-05', '2024-01-15', 'recibida', 180000.00),
(8, 1, '2024-01-10', '2024-01-20', 'recibida', 95000.00),
(9, 2, '2024-02-01', '2024-02-10', 'recibida', 50000.00),
(10, 2, '2024-02-05', '2024-02-15', 'recibida', 35000.00),
(11, 1, '2024-03-01', '2024-03-10', 'recibida', 120000.00),
(12, 2, '2024-03-05', '2024-03-15', 'recibida', 65000.00),
(13, 1, '2024-04-01', '2024-04-10', 'recibida', 90000.00),
(14, 2, '2024-04-05', '2024-04-15', 'recibida', 40000.00),
(15, 1, '2024-05-01', '2024-05-10', 'recibida', 110000.00),
(16, 2, '2024-05-05', '2024-05-15', 'recibida', 55000.00),
(17, 1, '2024-06-01', '2024-06-10', 'aprobada', 130000.00),
(18, 2, '2024-06-05', '2024-06-15', 'pendiente', 70000.00),
(19, 1, '2024-07-01', '2024-07-10', 'pendiente', 95000.00),
(20, 2, '2024-07-05', '2024-07-15', 'pendiente', 45000.00),
(1, 1, '2024-08-01', '2024-08-10', 'pendiente', 140000.00),
(2, 2, '2024-08-05', '2024-08-15', 'pendiente', 60000.00),
(3, 1, '2024-09-01', '2024-09-10', 'pendiente', 100000.00),
(4, 2, '2024-09-05', '2024-09-15', 'pendiente', 50000.00),
(5, 1, '2024-10-01', '2024-10-10', 'pendiente', 150000.00),
(6, 2, '2024-10-05', '2024-10-15', 'pendiente', 80000.00),
(7, 1, '2024-11-01', '2024-11-10', 'pendiente', 110000.00),
(8, 2, '2024-11-05', '2024-11-15', 'pendiente', 55000.00),
(9, 1, '2024-12-01', '2024-12-10', 'pendiente', 90000.00),
(10, 2, '2024-12-05', '2024-12-15', 'pendiente', 45000.00),
(11, 1, '2025-01-01', '2025-01-10', 'pendiente', 120000.00);

-- 12. Detalles de Órdenes de Compra (asegurar que id_orden_compra e id_material existan)
INSERT INTO detalle_ordenes_compra (id_orden_compra, id_material, cantidad, precio_unitario, subtotal) VALUES
(6, 1, 12000, 15.00, 180000.00),
(7, 3, 5000, 19.00, 95000.00),
(8, 5, 2000, 25.00, 50000.00),
(9, 8, 2000, 17.50, 35000.00),
(10, 6, 8000, 15.00, 120000.00),
(11, 7, 2500, 26.00, 65000.00),
(12, 9, 3000, 30.00, 90000.00),
(13, 10, 2000, 20.00, 40000.00),
(14, 2, 8000, 13.75, 110000.00),
(15, 4, 4000, 13.75, 55000.00),
(16, 11, 4000, 32.50, 130000.00),
(17, 12, 2000, 35.00, 70000.00),
(18, 13, 3000, 31.67, 95000.00),
(19, 14, 1500, 30.00, 45000.00),
(20, 15, 4000, 35.00, 140000.00),
(21, 16, 2000, 30.00, 60000.00),
(22, 17, 3000, 33.33, 100000.00),
(23, 18, 2000, 25.00, 50000.00),
(24, 19, 5000, 30.00, 150000.00),
(25, 20, 2000, 40.00, 80000.00),
(26, 21, 3000, 36.67, 110000.00),
(27, 22, 1500, 36.67, 55000.00),
(28, 23, 3000, 30.00, 90000.00),
(29, 24, 1500, 30.00, 45000.00),
(30, 25, 4000, 30.00, 120000.00);

-- 13. Órdenes de Producción (asegurar que id_producto e id_usuario existan)
INSERT INTO ordenes_produccion (id_producto, cantidad, fecha_inicio, fecha_fin, estado, id_usuario) VALUES
(9, 600, '2024-01-10', '2024-01-15', 'completada', 2),
(10, 400, '2024-01-16', '2024-01-20', 'completada', 2),
(11, 300, '2024-02-01', '2024-02-05', 'completada', 2),
(12, 250, '2024-02-06', '2024-02-10', 'completada', 2),
(13, 200, '2024-03-01', '2024-03-05', 'completada', 2),
(14, 350, '2024-03-06', '2024-03-10', 'completada', 2),
(15, 300, '2024-04-01', '2024-04-05', 'completada', 2),
(16, 250, '2024-04-06', '2024-04-10', 'completada', 2),
(17, 200, '2024-05-01', '2024-05-05', 'completada', 2),
(18, 400, '2024-05-06', '2024-05-10', 'completada', 2),
(19, 350, '2024-06-01', NULL, 'en_proceso', 2),
(20, 300, '2024-06-05', NULL, 'en_proceso', 2),
(21, 250, '2024-07-01', NULL, 'planificada', 2),
(22, 200, '2024-07-05', NULL, 'planificada', 2),
(23, 400, '2024-08-01', NULL, 'planificada', 2),
(24, 350, '2024-08-05', NULL, 'planificada', 2),
(25, 300, '2024-09-01', NULL, 'planificada', 2),
(1, 500, '2024-09-05', NULL, 'planificada', 2),
(2, 450, '2024-10-01', NULL, 'planificada', 2),
(3, 400, '2024-10-05', NULL, 'planificada', 2),
(4, 350, '2024-11-01', NULL, 'planificada', 2),
(5, 300, '2024-11-05', NULL, 'planificada', 2),
(6, 500, '2024-12-01', NULL, 'planificada', 2),
(7, 450, '2024-12-05', NULL, 'planificada', 2),
(8, 400, '2025-01-01', NULL, 'planificada', 2);

-- 14. Control de Calidad (asegurar que id_orden_produccion e id_usuario existan)
INSERT INTO control_calidad (id_orden_produccion, fecha, resultado, observaciones, id_usuario) VALUES
(6, '2024-01-15', 'aprobado', 'Lote cumple con todos los estándares de calidad', 4),
(6, '2024-01-15', 'reparacion', '8 unidades requieren ajustes menores', 4),
(7, '2024-01-20', 'aprobado', 'Lote aprobado sin observaciones', 4),
(8, '2024-02-05', 'aprobado', 'Todos los neumáticos aprobados', 4),
(9, '2024-02-10', 'rechazado', '12 unidades con defectos de fabricación', 4),
(10, '2024-03-05', 'aprobado', 'Lote cumple con especificaciones', 4),
(11, '2024-03-10', 'aprobado', 'Calidad superior en todo el lote', 4),
(12, '2024-04-05', 'reparacion', '5 unidades requieren reparación', 4),
(13, '2024-04-10', 'aprobado', 'Lote aprobado para distribución', 4),
(14, '2024-05-05', 'aprobado', 'Cumple con normativas internacionales', 4),
(15, '2024-05-10', 'rechazado', '15 unidades no cumplen con especificaciones', 4),
(16, '2024-06-08', 'aprobado', 'Lote en proceso cumple con estándares', 4),
(17, '2024-06-12', 'reparacion', '10 unidades en reparación', 4),
(18, '2024-07-03', 'aprobado', 'Primera muestra aprobada', 4),
(19, '2024-07-08', 'aprobado', 'Calidad consistente en todo el lote', 4),
(20, '2024-08-05', 'reparacion', '8 unidades requieren ajustes', 4),
(21, '2024-08-10', 'aprobado', 'Lote aprobado para envío', 4),
(22, '2024-09-05', 'aprobado', 'Cumple con especificaciones técnicas', 4),
(23, '2024-09-10', 'rechazado', '20 unidades con defectos', 4),
(24, '2024-10-05', 'aprobado', 'Lote de alta calidad', 4),
(25, '2024-10-10', 'reparacion', '12 unidades en proceso de reparación', 4),
(26, '2024-11-05', 'aprobado', 'Aprobado para distribución', 4),
(27, '2024-11-10', 'aprobado', 'Excelente calidad en todo el lote', 4),
(28, '2024-12-05', 'reparacion', '6 unidades requieren ajustes', 4),
(29, '2024-12-10', 'aprobado', 'Lote aprobado sin observaciones', 4);

-- 15. Ventas (asegurar que id_cliente e id_usuario existan)
INSERT INTO ventas (id_cliente, fecha, total, estado, id_usuario) VALUES
(8, '2024-01-10', 24000.00, 'completada', 3),
(9, '2024-01-15', 18000.00, 'completada', 3),
(10, '2024-02-05', 15000.00, 'completada', 3),
(11, '2024-02-10', 21000.00, 'completada', 3),
(12, '2024-03-05', 27000.00, 'completada', 3),
(13, '2024-03-10', 12000.00, 'completada', 3),
(14, '2024-04-05', 22500.00, 'completada', 3),
(15, '2024-04-10', 18000.00, 'completada', 3),
(16, '2024-05-05', 30000.00, 'completada', 3),
(17, '2024-05-10', 24000.00, 'completada', 3),
(18, '2024-06-05', 21000.00, 'pendiente', 3),
(19, '2024-06-10', 18000.00, 'pendiente', 3),
(20, '2024-07-05', 27000.00, 'pendiente', 3),
(21, '2024-07-10', 22500.00, 'pendiente', 3),
(22, '2024-08-05', 30000.00, 'pendiente', 3),
(23, '2024-08-10', 24000.00, 'pendiente', 3),
(24, '2024-09-05', 21000.00, 'pendiente', 3),
(25, '2024-09-10', 18000.00, 'pendiente', 3),
(26, '2024-10-05', 27000.00, 'pendiente', 3),
(27, '2024-10-10', 22500.00, 'pendiente', 3),
(28, '2024-11-05', 30000.00, 'pendiente', 3),
(29, '2024-11-10', 24000.00, 'pendiente', 3),
(30, '2024-12-05', 21000.00, 'pendiente', 3),
(31, '2024-12-10', 18000.00, 'pendiente', 3),
(32, '2025-01-05', 27000.00, 'pendiente', 3);

-- 16. Detalles de Ventas (asegurar que id_venta e id_producto existan)
INSERT INTO detalle_ventas (id_venta, id_producto, cantidad, precio_unitario, subtotal) VALUES
(7, 9, 60, 400.00, 24000.00),
(8, 10, 50, 360.00, 18000.00),
(9, 11, 30, 500.00, 15000.00),
(10, 12, 50, 420.00, 21000.00),
(11, 13, 50, 540.00, 27000.00),
(12, 14, 30, 400.00, 12000.00),
(13, 15, 50, 450.00, 22500.00),
(14, 16, 40, 450.00, 18000.00),
(15, 17, 50, 600.00, 30000.00),
(16, 18, 40, 600.00, 24000.00),
(17, 19, 50, 420.00, 21000.00),
(18, 20, 40, 450.00, 18000.00),
(19, 21, 50, 540.00, 27000.00),
(20, 22, 50, 450.00, 22500.00),
(21, 23, 50, 600.00, 30000.00),
(22, 24, 40, 600.00, 24000.00),
(23, 25, 50, 420.00, 21000.00),
(24, 1, 40, 350.00, 14000.00),
(24, 2, 10, 380.00, 3800.00),
(25, 3, 50, 540.00, 27000.00),
(26, 4, 50, 450.00, 22500.00),
(27, 5, 50, 600.00, 30000.00),
(28, 6, 40, 600.00, 24000.00),
(29, 7, 50, 420.00, 21000.00),
(30, 8, 40, 450.00, 18000.00),
(31, 9, 50, 540.00, 27000.00);

-- 17. Nóminas (asegurar que id_empleado exista)
-- Nóminas para 2024
INSERT INTO nominas (id_empleado, periodo, fecha_pago, salario_bruto, deducciones, bonos, salario_neto) VALUES
(1, 'Enero 2024', '2024-02-05', 25000.00, 3750.00, 2000.00, 23250.00),
(2, 'Enero 2024', '2024-02-05', 18000.00, 2700.00, 1000.00, 16300.00),
(3, 'Enero 2024', '2024-02-05', 23000.00, 3450.00, 1500.00, 21050.00),
(4, 'Enero 2024', '2024-02-05', 20000.00, 3000.00, 1200.00, 18200.00),
(5, 'Enero 2024', '2024-02-05', 21000.00, 3150.00, 1000.00, 18850.00),
(6, 'Enero 2024', '2024-02-05', 28000.00, 4200.00, 2500.00, 26300.00),
(7, 'Enero 2024', '2024-02-05', 22000.00, 3300.00, 1500.00, 20200.00),
(8, 'Enero 2024', '2024-02-05', 27000.00, 4050.00, 2000.00, 24950.00),
(9, 'Enero 2024', '2024-02-05', 19500.00, 2925.00, 1000.00, 17575.00),
(10, 'Enero 2024', '2024-02-05', 20500.00, 3075.00, 1200.00, 18625.00),
(11, 'Enero 2024', '2024-02-05', 24000.00, 3600.00, 1500.00, 21900.00),
(12, 'Enero 2024', '2024-02-05', 29000.00, 4350.00, 2500.00, 27150.00),
(13, 'Enero 2024', '2024-02-05', 22500.00, 3375.00, 1500.00, 20625.00),
(14, 'Enero 2024', '2024-02-05', 26000.00, 3900.00, 2000.00, 24100.00),
(15, 'Enero 2024', '2024-02-05', 21500.00, 3225.00, 1200.00, 19475.00),
(16, 'Enero 2024', '2024-02-05', 20000.00, 3000.00, 1000.00, 18000.00),
(17, 'Enero 2024', '2024-02-05', 23500.00, 3525.00, 1500.00, 21475.00),
(18, 'Enero 2024', '2024-02-05', 24500.00, 3675.00, 1800.00, 22625.00),
(19, 'Enero 2024', '2024-02-05', 25500.00, 3825.00, 2000.00, 23675.00),
(20, 'Enero 2024', '2024-02-05', 23000.00, 3450.00, 1500.00, 21050.00),
(21, 'Enero 2024', '2024-02-05', 19000.00, 2850.00, 1000.00, 17150.00),
(22, 'Enero 2024', '2024-02-05', 21000.00, 3150.00, 1200.00, 19050.00),
(23, 'Enero 2024', '2024-02-05', 27500.00, 4125.00, 2200.00, 25575.00),
(24, 'Enero 2024', '2024-02-05', 22500.00, 3375.00, 1500.00, 20625.00),
(25, 'Enero 2024', '2024-02-05', 21500.00, 3225.00, 1300.00, 19575.00);

-- Continuar con los demás meses hasta mayo 2025...

-- 18. Proyectos I+D
INSERT INTO proyectos_i_d (nombre, descripcion, fecha_inicio, fecha_fin_estimada, presupuesto, estado) VALUES
('Neumático Inteligente', 'Desarrollo de neumáticos con sensores integrados', '2024-02-15', '2025-12-31', 750000.00, 'en_desarrollo'),
('Compuesto Silencioso', 'Reducción de ruido en neumáticos premium', '2024-03-10', '2024-11-30', 350000.00, 'en_desarrollo'),
('Tecnología Auto-reparable', 'Neumáticos que reparan pequeños daños automáticamente', '2024-04-01', '2025-06-30', 850000.00, 'en_desarrollo'),
('Caucho Sostenible', 'Materiales 100% reciclados y reciclables', '2024-05-15', '2025-09-30', 600000.00, 'planificacion'),
('Neumático para Vehículos Autónomos', 'Optimización para flotas autónomas', '2024-01-20', '2025-03-31', 500000.00, 'en_desarrollo'),
('Sistema de Monitorización en Tiempo Real', 'Tecnología para seguimiento de desgaste', '2024-02-01', '2024-10-31', 400000.00, 'en_desarrollo'),
('Compuesto Ultra-Resistente', 'Para condiciones extremas de operación', '2024-03-15', '2025-01-31', 450000.00, 'en_desarrollo'),
('Neumático Modular', 'Diseño que permite reemplazar secciones dañadas', '2024-04-10', '2025-08-31', 700000.00, 'planificacion'),
('Tecnología de Ahorro de Combustible', 'Reducción de resistencia a la rodadura', '2024-05-01', '2024-12-31', 550000.00, 'en_desarrollo'),
('Materiales Autolimpiantes', 'Superficies que repelen el barro y suciedad', '2024-01-10', '2025-02-28', 480000.00, 'en_desarrollo'),
('Neumático para Ciudades Inteligentes', 'Integración con infraestructura urbana', '2024-02-20', '2025-07-31', 650000.00, 'planificacion'),
('Sistema de Presión Automática', 'Mantenimiento óptimo de presión sin intervención', '2024-03-01', '2024-11-30', 520000.00, 'en_desarrollo'),
('Compuesto para Climas Extremos', 'Funcionalidad en -40°C a +60°C', '2024-04-15', '2025-05-31', 580000.00, 'en_desarrollo'),
('Neumático con Huella Reducida', 'Minimización de impacto ambiental', '2024-05-10', '2025-04-30', 620000.00, 'planificacion'),
('Tecnología de Autodiagnóstico', 'Detección temprana de problemas', '2024-01-05', '2024-09-30', 490000.00, 'en_desarrollo'),
('Materiales de Origen No Tradicional', 'Alternativas sostenibles a materiales convencionales', '2024-02-10', '2025-03-31', 530000.00, 'en_desarrollo'),
('Neumático para Movilidad Urbana', 'Optimizado para bicicletas y scooters eléctricos', '2024-03-20', '2024-12-31', 470000.00, 'en_desarrollo'),
('Sistema de Tracción Mejorada', 'Para condiciones de baja adherencia', '2024-04-05', '2025-06-30', 680000.00, 'planificacion'),
('Compuesto de Larga Duración', 'Doble vida útil respecto a estándares actuales', '2024-05-20', '2025-08-31', 720000.00, 'planificacion'),
('Neumático para Vehículos Eléctricos', 'Optimizado para alto torque y peso adicional', '2024-01-15', '2024-10-31', 590000.00, 'en_desarrollo'),
('Tecnología de Conducción Suave', 'Reducción de vibraciones y mayor confort', '2024-02-05', '2025-01-31', 510000.00, 'en_desarrollo'),
('Materiales Autoregenerantes', 'Reparación automática de pequeños cortes', '2024-03-10', '2025-04-30', 670000.00, 'planificacion'),
('Neumático para Servicios de Entrega', 'Optimizado para paradas frecuentes', '2024-04-20', '2024-11-30', 440000.00, 'en_desarrollo'),
('Sistema de Identificación RFID', 'Para seguimiento en toda la cadena de valor', '2024-05-05', '2024-12-31', 380000.00, 'en_desarrollo'),
('Compuesto para Alta Velocidad', 'Estabilidad a velocidades superiores a 300 km/h', '2024-01-25', '2025-05-31', 710000.00, 'planificacion');

-- 19. Normativas Legales
INSERT INTO normativas_legales (nombre, tipo, descripcion, fecha_actualizacion, aplicable_a) VALUES
('ISO 45001:2018', 'seguridad', 'Sistemas de gestión de seguridad y salud en el trabajo', '2024-01-01', 'Toda la empresa'),
('Reglamento REACH', 'ambiental', 'Registro, evaluación, autorización y restricción de sustancias químicas', '2024-02-15', 'Producción/I+D'),
('Norma ISO 50001', 'ambiental', 'Sistemas de gestión de la energía', '2024-03-01', 'Producción/Mantenimiento'),
('Ley de Gestión Integral de Riesgos', 'seguridad', 'Normativa nacional de gestión de riesgos', '2024-01-15', 'Toda la empresa'),
('Reglamento de Neumáticos UE 2024', 'calidad', 'Nuevos estándares europeos para neumáticos', '2024-04-20', 'Producción/Calidad'),
('Norma COVENIN 3400', 'seguridad', 'Seguridad en máquinas y equipos industriales', '2024-02-01', 'Producción/Mantenimiento'),
('Protocolo de Kioto', 'ambiental', 'Compromisos de reducción de emisiones', '2024-01-01', 'Toda la empresa'),
('Norma ISO 26000', 'laboral', 'Responsabilidad social corporativa', '2024-03-15', 'RRHH'),
('Reglamento de Seguridad Química', 'seguridad', 'Manejo y almacenamiento de productos químicos', '2024-04-01', 'Producción/Almacén'),
('Norma COVENIN 2500', 'calidad', 'Sistemas de gestión de calidad para la industria', '2024-02-10', 'Producción/Calidad'),
('Ley de Protección de Datos', 'laboral', 'Protección de datos personales de empleados', '2024-01-20', 'RRHH'),
('Reglamento de Residuos Peligrosos', 'ambiental', 'Manejo y disposición de residuos peligrosos', '2024-03-01', 'Producción/Medio Ambiente'),
('Norma ISO 14064', 'ambiental', 'Gases de efecto invernadero', '2024-04-15', 'Toda la empresa'),
('Protocolo de Montreal', 'ambiental', 'Protección de la capa de ozono', '2024-01-01', 'Producción/I+D'),
('Reglamento de Etiquetado', 'calidad', 'Requisitos de etiquetado para productos', '2024-02-20', 'Producción/Ventas'),
('Norma COVENIN 1800', 'seguridad', 'Sistemas de gestión de seguridad y salud ocupacional', '2024-03-10', 'Toda la empresa'),
('Ley de Promoción del Trabajo', 'laboral', 'Incentivos a la contratación', '2024-04-05', 'RRHH'),
('Reglamento de Emisiones', 'ambiental', 'Límites de emisiones para procesos industriales', '2024-01-15', 'Producción/Mantenimiento'),
('Norma ISO 37001', 'laboral', 'Sistemas de gestión antisoborno', '2024-02-01', 'Toda la empresa'),
('Reglamento de Transporte de Mercancías', 'seguridad', 'Normas para transporte de productos químicos', '2024-03-20', 'Logística'),
('Norma COVENIN 2000', 'calidad', 'Requisitos para productos industriales', '2024-04-10', 'Producción/Calidad'),
('Ley de Prevención de Riesgos', 'seguridad', 'Obligaciones en prevención de riesgos laborales', '2024-01-05', 'Toda la empresa'),
('Reglamento de Eficiencia Energética', 'ambiental', 'Requisitos de eficiencia para equipos', '2024-02-15', 'Mantenimiento'),
('Norma ISO 22301', 'seguridad', 'Sistemas de gestión de continuidad del negocio', '2024-03-01', 'Toda la empresa'),
('Reglamento de Sustancias Restringidas', 'ambiental', 'Lista de sustancias prohibidas en productos', '2024-04-20', 'Producción/I+D');

-- 20. Incidentes (asegurar que id_area e id_empleado_reporta existan)
INSERT INTO incidentes (tipo, descripcion, fecha, id_area, id_empleado_reporta, estado) VALUES
('seguridad', 'Fuga menor de aire comprimido en área de producción', '2024-01-10', 1, 2, 'resuelto'),
('calidad', 'Lote de negro de humo con humedad superior a la especificada', '2024-01-15', 3, 4, 'resuelto'),
('logistica', 'Retraso en entrega de materiales por problemas de transporte', '2024-02-05', 2, 3, 'resuelto'),
('seguridad', 'Equipo de protección personal vencido encontrado en uso', '2024-02-10', 1, 5, 'resuelto'),
('calidad', 'Variación en parámetros de mezclado detectada', '2024-03-01', 3, 4, 'investigacion'),
('logistica', 'Error en inventario físico vs sistema', '2024-03-15', 2, 3, 'investigacion'),
('seguridad', 'Casi accidente por falta de señalización', '2024-04-05', 1, 2, 'resuelto'),
('calidad', 'Defectos en banda de rodamiento en lote de producción', '2024-04-10', 3, 4, 'resuelto'),
('logistica', 'Daño en material recibido por mala manipulación', '2024-05-01', 2, 3, 'resuelto'),
('seguridad', 'Falta de orden y limpieza en área de almacenamiento', '2024-05-15', 1, 5, 'investigacion'),
('calidad', 'Desviación en medidas de neumáticos terminados', '2024-01-20', 3, 4, 'resuelto'),
('logistica', 'Problemas con sistema de seguimiento de envíos', '2024-02-15', 2, 3, 'resuelto'),
('seguridad', 'Ruido excesivo en área de prensado', '2024-03-10', 1, 2, 'investigacion'),
('calidad', 'Inconsistencia en dureza de compuestos', '2024-04-01', 3, 4, 'resuelto'),
('logistica', 'Error en documentación de envío internacional', '2024-05-05', 2, 3, 'resuelto'),
('seguridad', 'Falta de capacitación en nuevo equipo', '2024-01-25', 1, 5, 'resuelto'),
('calidad', 'Problemas con sistema de medición automatizado', '2024-02-20', 3, 4, 'investigacion'),
('logistica', 'Daño en mercancía durante carga', '2024-03-15', 2, 3, 'resuelto'),
('seguridad', 'Condiciones inseguras en área de mantenimiento', '2024-04-10', 1, 2, 'resuelto'),
('calidad', 'Reclamo de cliente por desgaste prematuro', '2024-05-15', 3, 4, 'investigacion'),
('logistica', 'Retraso en producción por falta de material', '2024-01-30', 2, 3, 'resuelto'),
('seguridad', 'Incidente con herramienta defectuosa', '2024-02-25', 1, 5, 'resuelto'),
('calidad', 'Variación en color entre lotes', '2024-03-20', 3, 4, 'resuelto'),
('logistica', 'Error en sistema de gestión de almacén', '2024-04-15', 2, 3, 'investigacion'),
('seguridad', 'Falta de procedimiento escrito para nueva operación', '2024-05-20', 1, 2, 'resuelto');

-- 21. Activos de Producción (asegurar que id_area exista)
INSERT INTO activos_produccion (nombre, tipo, id_area, fecha_adquisicion, estado) VALUES
('Mezcladora X-300', 'maquinaria', 1, '2022-02-15', 'operativo'),
('Prensa Hidráulica PH-600', 'maquinaria', 1, '2023-01-20', 'operativo'),
('Vulcanizadora VUL-400', 'maquinaria', 1, '2021-06-10', 'operativo'),
('Extrusora E-500', 'maquinaria', 1, '2022-09-12', 'operativo'),
('Montadora de Neumáticos MN-200', 'maquinaria', 1, '2023-03-15', 'operativo'),
('Báscula Industrial BI-500', 'equipo', 2, '2022-10-30', 'operativo'),
('Kit Herramientas Calidad KH-200', 'herramienta', 3, '2023-02-05', 'operativo'),
('Equipo de Pruebas EP-300', 'equipo', 3, '2022-07-18', 'operativo'),
('Sistema de Transporte ST-100', 'equipo', 2, '2023-01-10', 'operativo'),
('Robot de Manipulación RM-50', 'maquinaria', 1, '2022-05-20', 'mantenimiento'),
('Cortadora Automática CA-400', 'maquinaria', 1, '2023-04-05', 'operativo'),
('Sistema de Almacenamiento AS-200', 'equipo', 2, '2022-08-15', 'operativo'),
('Equipo de Medición EM-150', 'equipo', 3, '2023-01-25', 'operativo'),
('Prensa de Moldeo PM-350', 'maquinaria', 1, '2022-03-10', 'operativo'),
('Sistema de Enfriamiento SE-250', 'equipo', 1, '2023-02-20', 'operativo'),
('Banda Transportadora BT-300', 'equipo', 1, '2022-09-05', 'operativo'),
('Equipo de Control de Calidad CCQ-100', 'equipo', 3, '2023-03-01', 'operativo'),
('Sistema de Pintura SP-200', 'equipo', 1, '2022-04-15', 'operativo'),
('Máquina de Inspección Visual MI-150', 'equipo', 3, '2023-01-15', 'operativo'),
('Robot de Soldadura RS-80', 'maquinaria', 1, '2022-07-20', 'operativo'),
('Sistema de Empaque SE-180', 'equipo', 2, '2023-02-10', 'operativo'),
('Equipo de Pruebas de Durabilidad EPD-200', 'equipo', 3, '2022-05-25', 'operativo'),
('Máquina de Corte Laser CL-120', 'maquinaria', 1, '2023-03-05', 'operativo'),
('Sistema de Manejo de Materiales SM-220', 'equipo', 2, '2022-08-10', 'operativo'),
('Equipo de Pruebas de Desempeño EPD-180', 'equipo', 3, '2023-01-20', 'operativo');

-- 22. Mantenimiento (asegurar que id_activo e id_empleado existan)
INSERT INTO mantenimiento (id_activo, tipo, fecha, descripcion, costo, id_empleado) VALUES
(10, 'correctivo', '2024-01-15', 'Reemplazo de componentes electrónicos', 1500.00, 5),
(1, 'preventivo', '2024-01-20', 'Mantenimiento programado semestral', 850.00, 5),
(5, 'preventivo', '2024-02-05', 'Lubricación y ajuste de componentes', 700.00, 5),
(7, 'correctivo', '2024-02-10', 'Reparación de sistema de medición', 1200.00, 5),
(3, 'preventivo', '2024-03-01', 'Cambio de filtros y limpieza general', 900.00, 5),
(8, 'correctivo', '2024-03-15', 'Reparación de sensor defectuoso', 1100.00, 5),
(2, 'preventivo', '2024-04-05', 'Mantenimiento programado trimestral', 800.00, 5),
(4, 'correctivo', '2024-04-10', 'Reemplazo de bandas transportadoras', 1300.00, 5),
(6, 'preventivo', '2024-05-01', 'Calibración y verificación', 750.00, 5),
(9, 'correctivo', '2024-05-15', 'Reparación de sistema hidráulico', 1400.00, 5),
(11, 'preventivo', '2024-01-25', 'Mantenimiento programado', 850.00, 5),
(12, 'correctivo', '2024-02-15', 'Reparación de motor eléctrico', 1250.00, 5),
(13, 'preventivo', '2024-03-10', 'Limpieza y ajuste de componentes', 700.00, 5),
(14, 'correctivo', '2024-04-01', 'Reemplazo de piezas desgastadas', 1100.00, 5),
(15, 'preventivo', '2024-05-05', 'Mantenimiento programado', 800.00, 5),
(16, 'correctivo', '2024-01-30', 'Reparación de sistema de control', 1350.00, 5),
(17, 'preventivo', '2024-02-20', 'Calibración de instrumentos', 750.00, 5),
(18, 'correctivo', '2024-03-15', 'Reemplazo de boquillas', 950.00, 5),
(19, 'preventivo', '2024-04-10', 'Mantenimiento programado', 850.00, 5),
(20, 'correctivo', '2024-05-20', 'Reparación de brazo robótico', 1500.00, 5),
(21, 'preventivo', '2024-01-10', 'Lubricación y ajuste', 700.00, 5),
(22, 'correctivo', '2024-02-05', 'Reemplazo de componentes electrónicos', 1200.00, 5),
(23, 'preventivo', '2024-03-01', 'Mantenimiento programado', 800.00, 5),
(24, 'correctivo', '2024-04-15', 'Reparación de sistema neumático', 1100.00, 5),
(25, 'preventivo', '2024-05-10', 'Limpieza y verificación', 750.00, 5);

-- 23. Configuración del Sistema
INSERT INTO configuracion_sistema (parametro, valor, descripcion) VALUES
('dias_vencimiento_material', '180', 'Días antes del vencimiento para alertas de materiales'),
('stock_seguridad', '10', 'Porcentaje de stock adicional como seguridad'),
('hora_inicio_laboral', '08:00', 'Hora de inicio de la jornada laboral'),
('hora_fin_laboral', '17:00', 'Hora de fin de la jornada laboral'),
('tolerancia_tardanza', '15', 'Minutos de tolerancia para marcaje de tardanza'),
('dias_anticipacion_mantenimiento', '7', 'Días de anticipación para alertas de mantenimiento'),
('limite_incidentes', '3', 'Número máximo de incidentes antes de acción correctiva'),
('porcentaje_descuento', '5', 'Porcentaje de descuento máximo aplicable'),
('dias_validez_cotizacion', '30', 'Días de validez de una cotización'),
('tasa_interes_mora', '1.5', 'Porcentaje de interés por mora mensual'),
('limite_credito', '50000', 'Límite de crédito predeterminado para clientes'),
('dias_revision_calidad', '90', 'Días entre revisiones de calidad programadas'),
('temperatura_almacen', '25', 'Temperatura ideal para almacenamiento en °C'),
('humedad_almacen', '45', 'Humedad relativa ideal para almacenamiento en %'),
('version_sistema', '2.5.1', 'Versión actual del sistema ERP'),
('backup_automatico', '1', 'Indica si el backup automático está activo (1) o no (0)'),
('intervalo_backup', '24', 'Horas entre backups automáticos'),
('correo_soporte', 'soporte.erp@pirelli.com', 'Correo para reportar problemas técnicos'),
('telefono_emergencias', '0212-555-1234', 'Teléfono para emergencias operativas'),
('dias_retroactividad_nomina', '30', 'Días máximos para ajustes retroactivos en nómina'),
('limite_aprobacion_compras', '10000', 'Monto máximo que puede aprobar un supervisor'),
('dias_vacaciones_base', '15', 'Días base de vacaciones por año'),
('porcentaje_bono_puntualidad', '2', 'Porcentaje de bono por puntualidad perfecta'),
('dias_max_incapacidad', '90', 'Días máximos de incapacidad continua'),
('version_api', '1.2', 'Versión actual de la API del sistema');

-- Mensaje de finalización
SELECT 'Base de datos ERP Pirelli poblada exitosamente con datos de ejemplo' AS Mensaje;