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
('Admin Pirelli', 'admin@pirelli.com', SHA2('PirelliAdmin123', 256), 'admin'),
('María González', 'maria.gonzalez@pirelli.com', SHA2('Supervisor456', 256), 'supervisor'),
('Carlos Mendoza', 'carlos.mendoza@pirelli.com', SHA2('Empleado789', 256), 'empleado'),
('Laura Ramírez', 'laura.ramirez@pirelli.com', SHA2('Super789', 256), 'supervisor'),
('Juan Pérez', 'juan.perez@pirelli.com', SHA2('Emple123', 256), 'empleado'),
('Ana Sánchez', 'ana.sanchez@pirelli.com', SHA2('AnaPass123', 256), 'empleado'),
('Pedro Rodríguez', 'pedro.rodriguez@pirelli.com', SHA2('PedroPass456', 256), 'empleado');

-- 2. Áreas de Trabajo (asignar responsables que existen en la tabla usuarios)
INSERT INTO areas_trabajo (nombre_area, descripcion, responsable) VALUES
('Producción', 'Área de fabricación de neumáticos', 2),  -- María González (supervisor)
('Logística', 'Almacén y distribución de productos', 4),  -- Laura Ramírez (supervisor)
('Calidad', 'Control de calidad de productos', 2),        -- María González
('Mantenimiento', 'Mantenimiento de maquinaria', 4),     -- Laura Ramírez
('I+D', 'Investigación y desarrollo de nuevos productos', 1),  -- Admin Pirelli
('Ventas', 'Gestión comercial y atención al cliente', 4),      -- Laura Ramírez
('Recursos Humanos', 'Gestión del personal', 1);               -- Admin Pirelli

-- 3. Empleados (asegurar que id_area exista en areas_trabajo)
INSERT INTO empleados (nombre, apellidos, id_area, puesto, salario, fecha_contratacion, activo) VALUES
('María', 'González', 1, 'Supervisor de Producción', 25000.00, '2018-05-15', TRUE),
('Carlos', 'Mendoza', 1, 'Operario de Máquinas', 18000.00, '2020-02-10', TRUE),
('Laura', 'Ramírez', 2, 'Jefa de Logística', 23000.00, '2019-03-22', TRUE),
('Juan', 'Pérez', 3, 'Inspector de Calidad', 20000.00, '2021-01-05', TRUE),
('Ana', 'Sánchez', 4, 'Técnico de Mantenimiento', 21000.00, '2020-07-30', TRUE),
('Pedro', 'Rodríguez', 5, 'Ingeniero de Desarrollo', 28000.00, '2019-11-15', TRUE),
('Sofía', 'Martínez', 6, 'Ejecutiva de Ventas', 22000.00, '2022-03-10', TRUE),
('Luis', 'Gómez', 1, 'Operario de Máquinas', 17500.00, '2023-01-20', TRUE);

-- 4. Asistencia (asegurar que id_empleado exista)
INSERT INTO asistencia (id_empleado, fecha, hora_entrada, hora_salida, estado) VALUES
(1, '2023-11-01', '08:00:00', '17:00:00', 'presente'),
(1, '2023-11-02', '08:05:00', '17:10:00', 'presente'),
(1, '2023-11-03', '08:15:00', '17:05:00', 'tardanza'),
(2, '2023-11-01', '07:55:00', '16:58:00', 'presente'),
(2, '2023-11-02', NULL, NULL, 'ausente'),
(3, '2023-11-01', '08:02:00', '17:10:00', 'presente'),
(3, '2023-11-02', '08:00:00', '17:00:00', 'presente'),
(4, '2023-11-01', '07:58:00', '16:55:00', 'presente'),
(5, '2023-11-01', '08:10:00', '17:15:00', 'tardanza');

-- 5. Proveedores
INSERT INTO proveedores (nombre, contacto, telefono, email, direccion, tipo_material) VALUES
('Cauchos del Norte', 'Ing. Roberto Jiménez', '+584125556789', 'ventas@cauchosdelnorte.com', 'Zona Industrial Norte, Valencia', 'caucho'),
('Aceros Industriales SA', 'Lic. Patricia Gómez', '+582129876543', 'pgomez@acerosindustriales.com', 'Av. Principal, Caracas', 'acero'),
('Química Avanzada', 'Dr. Luis Rojas', '+582127654321', 'lrojas@quimicaavanzada.com', 'Polígono Industrial Sur, Maracay', 'quimicos'),
('Suministros Globales', 'Sra. Carmen Díaz', '+584147891234', 'cdiaz@suministrosglobales.com', 'Calle Comercial Este, Barquisimeto', 'otros'),
('Polímeros del Sur', 'Ing. Fernando López', '+582128765432', 'flopez@polimerosdelsur.com', 'Zona Franca, Puerto Ordaz', 'caucho'),
('Metales Nacionales', 'Sr. José Pérez', '+584146543210', 'jperez@metalesnacionales.com', 'Av. Industrial, Maracaibo', 'acero');

-- 6. Materiales
INSERT INTO materiales (nombre, descripcion, unidad_medida, stock_minimo, stock_maximo) VALUES
('Caucho natural', 'Caucho natural grado industrial', 'kg', 5000, 20000),
('Negro de humo', 'Negro de humo N550 para refuerzo', 'kg', 3000, 15000),
('Acero radial', 'Alambre de acero para cinturón radial', 'kg', 2000, 10000),
('Azufre', 'Azufre industrial para vulcanización', 'kg', 1000, 5000),
('Aditivos químicos', 'Paquete de aceleradores y antioxidantes', 'kg', 500, 2500),
('Caucho sintético SBR', 'Caucho estireno-butadieno', 'kg', 4000, 18000),
('Silica precipitada', 'Refuerzo alternativo al negro de humo', 'kg', 2500, 12000),
('Aceites plastificantes', 'Aceites para mejorar procesabilidad', 'litro', 1000, 5000);

-- 7. Inventario (asegurar que id_material exista)
INSERT INTO inventario (id_material, cantidad, ubicacion, lote, fecha_ingreso) VALUES
(1, 15000, 'Almacén A, Estante 4', 'LOTE-CAU-2023-10', '2023-10-15'),
(2, 8000, 'Almacén B, Estante 1', 'LOTE-NEG-2023-11', '2023-11-01'),
(3, 4500, 'Almacén C, Estante 3', 'LOTE-ACE-2023-09', '2023-09-20'),
(4, 3000, 'Almacén A, Estante 2', 'LOTE-AZU-2023-10', '2023-10-25'),
(5, 1200, 'Almacén B, Estante 5', 'LOTE-ADQ-2023-11', '2023-11-05'),
(6, 10000, 'Almacén D, Estante 1', 'LOTE-SBR-2023-10', '2023-10-20'),
(7, 5000, 'Almacén C, Estante 2', 'LOTE-SIL-2023-11', '2023-11-03'),
(8, 3500, 'Almacén A, Estante 5', 'LOTE-ACE-2023-10', '2023-10-18');

-- 8. Productos
INSERT INTO productos (codigo, nombre, descripcion, precio, categoria) VALUES
('PZR-001', 'P Zero Rosso', 'Neumático alto rendimiento para autos deportivos', 350.00, 'automovil'),
('PZR-002', 'P Zero Nero', 'Neumático ultra alto rendimiento', 380.00, 'automovil'),
('DSA-101', 'Diablo Supercorsa', 'Neumático para motocicletas deportivas', 280.00, 'motocicleta'),
('CMH-201', 'Cinturato MH', 'Neumático para camiones medianos', 420.00, 'camion'),
('IND-301', 'Industrial TR-1', 'Neumático para maquinaria industrial', 550.00, 'industrial'),
('SCP-102', 'Scorpion Verde', 'Neumático SUV ecológico', 320.00, 'automovil'),
('DRA-202', 'Dragón Sport', 'Neumático para motocicletas de alto cilindraje', 300.00, 'motocicleta'),
('CPL-302', 'Carrier PL-45', 'Neumático para camiones pesados', 480.00, 'camion');

-- 9. Recetas de Producción (asegurar que id_producto e id_material existan)
INSERT INTO recetas_produccion (id_producto, id_material, cantidad) VALUES
(1, 1, 25.5), (1, 2, 12.3), (1, 3, 8.7), (1, 4, 1.2), (1, 5, 0.8),
(2, 1, 27.0), (2, 2, 13.5), (2, 3, 9.0),
(3, 1, 18.0), (3, 6, 10.0),
(4, 1, 35.0), (4, 3, 15.0);

-- 10. Clientes
INSERT INTO clientes (nombre, contacto, telefono, email, direccion, tipo) VALUES
('Autos Deportivos SA', 'Sr. Alejandro Martínez', '+582127891234', 'ventas@autosdeportivos.com', 'Av. Principal, Caracas', 'distribuidor'),
('Motores Veloces', 'Ing. Sofía Rivas', '+584147896543', 's.rivas@motoresveloces.com', 'Zona Industrial Este, Valencia', 'mayorista'),
('Transporte Pesado CA', 'Sr. José González', '+582128765432', 'jgonzalez@transportepesado.com', 'Polígono Industrial, Maracay', 'OEM'),
('Taller Rápido', 'Sra. Carmen Díaz', '+584141234567', 'cdiaz@tallerrapido.com', 'Calle Comercial, Barquisimeto', 'minorista'),
('Concesionaria Líder', 'Sr. Roberto Sánchez', '+582129876543', 'rsanchez@concesionarialider.com', 'Av. Bolívar, Puerto La Cruz', 'distribuidor'),
('MotoParts', 'Sr. Luis Fernández', '+584148765432', 'lfernandez@motoparts.com', 'Carrera 15, San Cristóbal', 'mayorista'),
('Constructora Andina', 'Ing. Carlos Pérez', '+582127654321', 'cperez@constructoraandina.com', 'Av. Los Andes, Mérida', 'OEM');

-- 11. Órdenes de Compra (asegurar que id_proveedor e id_usuario existan)
INSERT INTO ordenes_compra (id_proveedor, id_usuario, fecha, fecha_entrega_esperada, estado, total) VALUES
(1, 1, '2023-10-10', '2023-10-20', 'recibida', 150000.00),
(2, 1, '2023-10-15', '2023-10-25', 'recibida', 85000.00),
(3, 2, '2023-11-01', '2023-11-10', 'aprobada', 45000.00),
(4, 2, '2023-11-05', '2023-11-15', 'pendiente', 32000.00),
(5, 1, '2023-11-10', '2023-11-20', 'pendiente', 75000.00);

-- 12. Detalles de Órdenes de Compra (asegurar que id_orden_compra e id_material existan)
INSERT INTO detalle_ordenes_compra (id_orden_compra, id_material, cantidad, precio_unitario, subtotal) VALUES
(1, 1, 10000, 15.00, 150000.00),
(2, 3, 5000, 17.00, 85000.00),
(3, 5, 1500, 30.00, 45000.00),
(4, 8, 2000, 16.00, 32000.00),
(5, 6, 5000, 15.00, 75000.00);

-- 13. Órdenes de Producción (asegurar que id_producto e id_usuario existan)
INSERT INTO ordenes_produccion (id_producto, cantidad, fecha_inicio, fecha_fin, estado, id_usuario) VALUES
(1, 500, '2023-11-01', '2023-11-05', 'completada', 2),
(2, 300, '2023-11-06', NULL, 'en_proceso', 2),
(3, 200, '2023-11-10', NULL, 'planificada', 2),
(4, 150, '2023-10-25', '2023-10-30', 'completada', 2),
(5, 100, '2023-11-15', NULL, 'planificada', 2);

-- 14. Control de Calidad (asegurar que id_orden_produccion e id_usuario existan)
INSERT INTO control_calidad (id_orden_produccion, fecha, resultado, observaciones, id_usuario) VALUES
(1, '2023-11-05', 'aprobado', 'Todos los neumáticos cumplen con los estándares de calidad', 4),
(1, '2023-11-05', 'reparacion', '5 unidades requieren ajustes menores', 4),
(4, '2023-10-30', 'aprobado', 'Lote aprobado sin observaciones', 4),
(4, '2023-10-30', 'rechazado', '2 unidades con defectos de fabricación', 4);

-- 15. Ventas (asegurar que id_cliente e id_usuario existan)
INSERT INTO ventas (id_cliente, fecha, total, estado, id_usuario) VALUES
(1, '2023-11-02', 17500.00, 'completada', 3),
(2, '2023-11-03', 8400.00, 'pendiente', 3),
(3, '2023-11-05', 12600.00, 'completada', 3),
(4, '2023-10-28', 5600.00, 'completada', 3),
(5, '2023-11-10', 19200.00, 'pendiente', 3),
(6, '2023-11-12', 9000.00, 'completada', 3);

-- 16. Detalles de Ventas (asegurar que id_venta e id_producto existan)
INSERT INTO detalle_ventas (id_venta, id_producto, cantidad, precio_unitario, subtotal) VALUES
(1, 1, 50, 350.00, 17500.00),
(2, 2, 20, 420.00, 8400.00),
(3, 3, 30, 420.00, 12600.00),
(4, 4, 10, 560.00, 5600.00),
(5, 5, 30, 640.00, 19200.00),
(6, 6, 25, 360.00, 9000.00),
(1, 2, 5, 420.00, 2100.00),
(3, 1, 10, 350.00, 3500.00);

-- 17. Nóminas (asegurar que id_empleado exista)
INSERT INTO nominas (id_empleado, periodo, fecha_pago, salario_bruto, deducciones, bonos, salario_neto) VALUES
(1, 'Octubre 2023', '2023-11-05', 25000.00, 3750.00, 2000.00, 23250.00),
(2, 'Octubre 2023', '2023-11-05', 18000.00, 2700.00, 1000.00, 16300.00),
(3, 'Octubre 2023', '2023-11-05', 23000.00, 3450.00, 1500.00, 21050.00),
(4, 'Octubre 2023', '2023-11-05', 20000.00, 3000.00, 1200.00, 18200.00),
(5, 'Octubre 2023', '2023-11-05', 21000.00, 3150.00, 1000.00, 18850.00),
(6, 'Octubre 2023', '2023-11-05', 28000.00, 4200.00, 2500.00, 26300.00),
(7, 'Octubre 2023', '2023-11-05', 22000.00, 3300.00, 1500.00, 20200.00);

-- 18. Proyectos I+D
INSERT INTO proyectos_i_d (nombre, descripcion, fecha_inicio, fecha_fin_estimada, presupuesto, estado) VALUES
('Neumático Eco-Friendly', 'Desarrollo de neumáticos con materiales reciclados', '2023-01-15', '2024-06-30', 500000.00, 'en_desarrollo'),
('Compuesto Ultra-Durable', 'Investigación de nuevos compuestos para mayor durabilidad', '2023-05-10', '2023-12-15', 250000.00, 'en_desarrollo'),
('Sistema Run-Flat', 'Tecnología para rodar sin aire', '2023-03-01', '2024-03-01', 750000.00, 'en_desarrollo'),
('Caucho Autoregenerante', 'Material que repara pequeños daños automáticamente', '2023-07-20', '2024-09-30', 600000.00, 'planificacion');

-- 19. Normativas Legales
INSERT INTO normativas_legales (nombre, tipo, descripcion, fecha_actualizacion, aplicable_a) VALUES
('ISO 9001:2015', 'calidad', 'Sistemas de gestión de calidad', '2023-01-01', 'Producción'),
('ISO 14001:2015', 'ambiental', 'Gestión ambiental', '2023-01-01', 'Toda la empresa'),
('LOTTT', 'laboral', 'Ley Orgánica del Trabajo', '2022-05-01', 'RRHH'),
('Normas COVENIN', 'seguridad', 'Normas de seguridad industrial', '2023-06-15', 'Producción/Mantenimiento'),
('Reglamento de Neumáticos', 'calidad', 'Estándares de calidad para neumáticos', '2023-03-20', 'Producción/Calidad');

-- 20. Incidentes (asegurar que id_area e id_empleado_reporta existan)
INSERT INTO incidentes (tipo, descripcion, fecha, id_area, id_empleado_reporta, estado) VALUES
('calidad', 'Lote de caucho con impurezas detectado', '2023-10-28', 3, 4, 'resuelto'),
('seguridad', 'Derrame químico menor en área de mezclado', '2023-11-02', 1, 2, 'investigacion'),
('logistica', 'Retraso en entrega de materiales', '2023-10-30', 2, 3, 'resuelto'),
('seguridad', 'Equipo de protección dañado', '2023-11-05', 1, 5, 'investigacion');

-- 21. Activos de Producción (asegurar que id_area exista)
INSERT INTO activos_produccion (nombre, tipo, id_area, fecha_adquisicion, estado) VALUES
('Mezcladora X-200', 'maquinaria', 1, '2020-01-15', 'operativo'),
('Prensa Hidráulica PH-500', 'maquinaria', 1, '2021-03-20', 'operativo'),
('Vulcanizadora VUL-300', 'maquinaria', 1, '2019-05-10', 'mantenimiento'),
('Kit Herramientas Calidad', 'herramienta', 3, '2022-02-05', 'operativo'),
('Extrusora E-400', 'maquinaria', 1, '2020-08-12', 'operativo'),
('Báscula Industrial', 'equipo', 2, '2021-11-30', 'operativo'),
('Montadora de Neumáticos', 'maquinaria', 1, '2022-05-15', 'operativo');

-- 22. Mantenimiento (asegurar que id_activo e id_empleado existan)
INSERT INTO mantenimiento (id_activo, tipo, fecha, descripcion, costo, id_empleado) VALUES
(3, 'correctivo', '2023-11-01', 'Reemplazo de bandas transportadoras', 1200.00, 5),
(1, 'preventivo', '2023-10-15', 'Mantenimiento programado trimestral', 800.00, 5),
(5, 'preventivo', '2023-11-10', 'Lubricación y ajuste de componentes', 650.00, 5),
(7, 'correctivo', '2023-10-25', 'Reparación de sistema hidráulico', 1500.00, 5);

-- 23. Configuración del Sistema
INSERT INTO configuracion_sistema (parametro, valor, descripcion) VALUES
('IVA', '16', 'Porcentaje de IVA aplicable'),
('moneda', 'USD', 'Moneda principal del sistema'),
('dias_stock_minimo', '7', 'Días de stock mínimo para alertas'),
('email_notificaciones', 'notificaciones@pirelli.com', 'Email para notificaciones del sistema'),
('tasa_cambio', '35.50', 'Tasa de cambio USD a moneda local');

-- Mensaje de finalización
SELECT 'Base de datos ERP Pirelli poblada exitosamente con datos de ejemplo' AS Mensaje;