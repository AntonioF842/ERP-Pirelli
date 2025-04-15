-- Creación de la base de datos
CREATE DATABASE IF NOT EXISTS erp_pirelli;
USE erp_pirelli;

-- Tabla de Usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    rol ENUM('admin', 'supervisor', 'empleado') NOT NULL,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Áreas de Trabajo
CREATE TABLE IF NOT EXISTS areas_trabajo (
    id_area INT AUTO_INCREMENT PRIMARY KEY,
    nombre_area VARCHAR(100) NOT NULL,
    descripcion TEXT,
    responsable INT,
    FOREIGN KEY (responsable) REFERENCES usuarios(id_usuario) ON DELETE SET NULL
);

-- Tabla de Empleados
CREATE TABLE IF NOT EXISTS empleados (
    id_empleado INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    id_area INT,
    puesto VARCHAR(100),
    salario DECIMAL(10,2),
    fecha_contratacion DATE,
    activo BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (id_area) REFERENCES areas_trabajo(id_area) ON DELETE SET NULL
);

-- Tabla de Asistencia
CREATE TABLE IF NOT EXISTS asistencia (
    id_asistencia INT AUTO_INCREMENT PRIMARY KEY,
    id_empleado INT NOT NULL,
    fecha DATE NOT NULL,
    hora_entrada TIME,
    hora_salida TIME,
    estado ENUM('presente', 'ausente', 'tardanza') DEFAULT 'presente',
    FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado) ON DELETE CASCADE,
    UNIQUE KEY (id_empleado, fecha)
);

-- Tabla de Proveedores
CREATE TABLE IF NOT EXISTS proveedores (
    id_proveedor INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    contacto VARCHAR(100),
    telefono VARCHAR(20),
    email VARCHAR(100),
    direccion TEXT,
    tipo_material ENUM('caucho', 'acero', 'quimicos', 'otros') NOT NULL
);

-- Tabla de Materiales
CREATE TABLE IF NOT EXISTS materiales (
    id_material INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    unidad_medida VARCHAR(20),
    stock_minimo INT,
    stock_maximo INT
);

-- Tabla de Inventario
CREATE TABLE IF NOT EXISTS inventario (
    id_inventario INT AUTO_INCREMENT PRIMARY KEY,
    id_material INT NOT NULL,
    cantidad INT NOT NULL,
    ubicacion VARCHAR(100),
    lote VARCHAR(50),
    fecha_ingreso DATE,
    FOREIGN KEY (id_material) REFERENCES materiales(id_material) ON DELETE CASCADE
);

-- Tabla de Órdenes de Compra
CREATE TABLE IF NOT EXISTS ordenes_compra (
    id_orden_compra INT AUTO_INCREMENT PRIMARY KEY,
    id_proveedor INT NOT NULL,
    id_usuario INT NOT NULL,
    fecha DATE NOT NULL,
    fecha_entrega_esperada DATE,
    estado ENUM('pendiente', 'aprobada', 'recibida', 'cancelada') DEFAULT 'pendiente',
    total DECIMAL(12,2),
    FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor) ON DELETE RESTRICT,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE RESTRICT
);

-- Tabla de Detalles de Órdenes de Compra
CREATE TABLE IF NOT EXISTS detalle_ordenes_compra (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY,
    id_orden_compra INT NOT NULL,
    id_material INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2),
    subtotal DECIMAL(12,2),
    FOREIGN KEY (id_orden_compra) REFERENCES ordenes_compra(id_orden_compra) ON DELETE CASCADE,
    FOREIGN KEY (id_material) REFERENCES materiales(id_material) ON DELETE RESTRICT
);

-- Tabla de Productos
CREATE TABLE IF NOT EXISTS productos (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    precio DECIMAL(10,2),
    categoria ENUM('automovil', 'motocicleta', 'camion', 'industrial')
);

-- Tabla de Órdenes de Producción
CREATE TABLE IF NOT EXISTS ordenes_produccion (
    id_orden_produccion INT AUTO_INCREMENT PRIMARY KEY,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE,
    estado ENUM('planificada', 'en_proceso', 'completada', 'cancelada') DEFAULT 'planificada',
    id_usuario INT NOT NULL,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE RESTRICT,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE RESTRICT
);

-- Tabla de Recetas de Producción
CREATE TABLE IF NOT EXISTS recetas_produccion (
    id_receta INT AUTO_INCREMENT PRIMARY KEY,
    id_producto INT NOT NULL,
    id_material INT NOT NULL,
    cantidad DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE CASCADE,
    FOREIGN KEY (id_material) REFERENCES materiales(id_material) ON DELETE RESTRICT
);

-- Tabla de Control de Calidad
CREATE TABLE IF NOT EXISTS control_calidad (
    id_control INT AUTO_INCREMENT PRIMARY KEY,
    id_orden_produccion INT NOT NULL,
    fecha DATE NOT NULL,
    resultado ENUM('aprobado', 'rechazado', 'reparacion') NOT NULL,
    observaciones TEXT,
    id_usuario INT NOT NULL,
    FOREIGN KEY (id_orden_produccion) REFERENCES ordenes_produccion(id_orden_produccion) ON DELETE CASCADE,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE RESTRICT
);

-- Tabla de Clientes
CREATE TABLE IF NOT EXISTS clientes (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    contacto VARCHAR(100),
    telefono VARCHAR(20),
    email VARCHAR(100),
    direccion TEXT,
    tipo ENUM('distribuidor', 'mayorista', 'minorista', 'OEM')
);

-- Tabla de Ventas
CREATE TABLE IF NOT EXISTS ventas (
    id_venta INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT NOT NULL,
    fecha DATE NOT NULL,
    total DECIMAL(12,2),
    estado ENUM('pendiente', 'completada', 'cancelada') DEFAULT 'pendiente',
    id_usuario INT NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente) ON DELETE RESTRICT,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE RESTRICT
);

-- Tabla de Detalles de Ventas
CREATE TABLE IF NOT EXISTS detalle_ventas (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY,
    id_venta INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2),
    subtotal DECIMAL(12,2),
    FOREIGN KEY (id_venta) REFERENCES ventas(id_venta) ON DELETE CASCADE,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE RESTRICT
);

-- Tabla de Nóminas
CREATE TABLE IF NOT EXISTS nominas (
    id_nomina INT AUTO_INCREMENT PRIMARY KEY,
    id_empleado INT NOT NULL,
    periodo VARCHAR(20) NOT NULL,
    fecha_pago DATE NOT NULL,
    salario_bruto DECIMAL(10,2) NOT NULL,
    deducciones DECIMAL(10,2),
    bonos DECIMAL(10,2),
    salario_neto DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado) ON DELETE CASCADE
);

-- Tabla de Proyectos I+D
CREATE TABLE IF NOT EXISTS proyectos_i_d (
    id_proyecto INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    fecha_inicio DATE,
    fecha_fin_estimada DATE,
    presupuesto DECIMAL(12,2),
    estado ENUM('planificacion', 'en_desarrollo', 'completado', 'cancelado') DEFAULT 'planificacion'
);

-- Tabla de Normativas Legales
CREATE TABLE IF NOT EXISTS normativas_legales (
    id_normativa INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    tipo ENUM('ambiental', 'seguridad', 'laboral', 'calidad') NOT NULL,
    descripcion TEXT,
    fecha_actualizacion DATE,
    aplicable_a VARCHAR(100)
);

-- Tabla de Registro de Incidentes
CREATE TABLE IF NOT EXISTS incidentes (
    id_incidente INT AUTO_INCREMENT PRIMARY KEY,
    tipo ENUM('seguridad', 'calidad', 'logistica') NOT NULL,
    descripcion TEXT NOT NULL,
    fecha DATE NOT NULL,
    id_area INT,
    id_empleado_reporta INT,
    estado ENUM('reportado', 'investigacion', 'resuelto') DEFAULT 'reportado',
    FOREIGN KEY (id_area) REFERENCES areas_trabajo(id_area) ON DELETE SET NULL,
    FOREIGN KEY (id_empleado_reporta) REFERENCES empleados(id_empleado) ON DELETE SET NULL
);

-- Tabla de Activos de Producción
CREATE TABLE IF NOT EXISTS activos_produccion (
    id_activo INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    tipo ENUM('maquinaria', 'herramienta', 'equipo') NOT NULL,
    id_area INT,
    fecha_adquisicion DATE,
    estado ENUM('operativo', 'mantenimiento', 'baja') DEFAULT 'operativo',
    FOREIGN KEY (id_area) REFERENCES areas_trabajo(id_area) ON DELETE SET NULL
);

-- Tabla de Mantenimiento
CREATE TABLE IF NOT EXISTS mantenimiento (
    id_mantenimiento INT AUTO_INCREMENT PRIMARY KEY,
    id_activo INT NOT NULL,
    tipo ENUM('preventivo', 'correctivo') NOT NULL,
    fecha DATE NOT NULL,
    descripcion TEXT,
    costo DECIMAL(10,2),
    id_empleado INT,
    FOREIGN KEY (id_activo) REFERENCES activos_produccion(id_activo) ON DELETE CASCADE,
    FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado) ON DELETE SET NULL
);

-- Tabla de Configuración del Sistema
CREATE TABLE IF NOT EXISTS configuracion_sistema (
    id_config INT AUTO_INCREMENT PRIMARY KEY,
    parametro VARCHAR(50) UNIQUE NOT NULL,
    valor TEXT,
    descripcion TEXT
);