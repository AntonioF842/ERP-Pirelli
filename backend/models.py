# backend/models.py
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime, date, time
from config import db  # Importa db desde config en lugar de crear una nueva instancia
# db = SQLAlchemy()

# Usuario
class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.Enum('admin', 'supervisor', 'empleado'), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Añade este método para Flask-Login
    def get_id(self):
        return str(self.id_usuario)  # Debe devolver un string

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

# Área de Trabajo
class AreaTrabajo(db.Model):
    __tablename__ = 'areas_trabajo'
    id_area = db.Column(db.Integer, primary_key=True)
    nombre_area = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    responsable = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'))
    responsable_usuario = db.relationship('Usuario', backref='areas_trabajo')

# Empleado
class Empleado(db.Model):
    __tablename__ = 'empleados'
    id_empleado = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    id_area = db.Column(db.Integer, db.ForeignKey('areas_trabajo.id_area'))
    puesto = db.Column(db.String(100))
    salario = db.Column(db.Numeric(10, 2))
    fecha_contratacion = db.Column(db.Date)
    activo = db.Column(db.Boolean, default=True)
    area = db.relationship('AreaTrabajo', backref='empleados')

# Asistencia
class Asistencia(db.Model):
    __tablename__ = 'asistencia'
    id_asistencia = db.Column(db.Integer, primary_key=True)
    id_empleado = db.Column(db.Integer, db.ForeignKey('empleados.id_empleado'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    hora_entrada = db.Column(db.Time)
    hora_salida = db.Column(db.Time)
    estado = db.Column(db.Enum('presente', 'ausente', 'tardanza'), default='presente')
    empleado = db.relationship('Empleado', backref='asistencias')

# Proveedor
class Proveedor(db.Model):
    __tablename__ = 'proveedores'
    id_proveedor = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    contacto = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    direccion = db.Column(db.Text)
    tipo_material = db.Column(db.Enum('caucho', 'acero', 'quimicos', 'otros'), nullable=False)

# Material
class Material(db.Model):
    __tablename__ = 'materiales'
    id_material = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    unidad_medida = db.Column(db.String(20))
    stock_minimo = db.Column(db.Integer)
    stock_maximo = db.Column(db.Integer)

# Inventario
class Inventario(db.Model):
    __tablename__ = 'inventario'
    id_inventario = db.Column(db.Integer, primary_key=True)
    id_material = db.Column(db.Integer, db.ForeignKey('materiales.id_material'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    ubicacion = db.Column(db.String(100))
    lote = db.Column(db.String(50))
    fecha_ingreso = db.Column(db.Date)
    material = db.relationship('Material', backref='inventarios')

# Orden de Compra
class OrdenCompra(db.Model):
    __tablename__ = 'ordenes_compra'
    id_orden_compra = db.Column(db.Integer, primary_key=True)
    id_proveedor = db.Column(db.Integer, db.ForeignKey('proveedores.id_proveedor'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    fecha_entrega_esperada = db.Column(db.Date)
    estado = db.Column(db.Enum('pendiente', 'aprobada', 'recibida', 'cancelada'), default='pendiente')
    total = db.Column(db.Numeric(12, 2))
    proveedor = db.relationship('Proveedor', backref='ordenes_compra')
    usuario = db.relationship('Usuario', backref='ordenes_compra')

# Detalle Orden de Compra
class DetalleOrdenCompra(db.Model):
    __tablename__ = 'detalle_ordenes_compra'
    id_detalle = db.Column(db.Integer, primary_key=True)
    id_orden_compra = db.Column(db.Integer, db.ForeignKey('ordenes_compra.id_orden_compra'), nullable=False)
    id_material = db.Column(db.Integer, db.ForeignKey('materiales.id_material'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2))
    subtotal = db.Column(db.Numeric(12, 2))
    orden_compra = db.relationship('OrdenCompra', backref='detalles')
    material = db.relationship('Material', backref='detalles_ordenes_compra')

# Producto
class Producto(db.Model):
    __tablename__ = 'productos'
    id_producto = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    categoria = db.Column(db.Enum('automovil', 'motocicleta', 'camion', 'industrial'), nullable=False)

# Orden de Producción
class OrdenProduccion(db.Model):
    __tablename__ = 'ordenes_produccion'
    id_orden_produccion = db.Column(db.Integer, primary_key=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id_producto'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date)
    estado = db.Column(db.Enum('planificada', 'en_proceso', 'completada', 'cancelada'), default='planificada')
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    producto = db.relationship('Producto', backref='ordenes_produccion')
    usuario = db.relationship('Usuario', backref='ordenes_produccion')

# Receta de Producción
class RecetaProduccion(db.Model):
    __tablename__ = 'recetas_produccion'
    id_receta = db.Column(db.Integer, primary_key=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id_producto'), nullable=False)
    id_material = db.Column(db.Integer, db.ForeignKey('materiales.id_material'), nullable=False)
    cantidad = db.Column(db.Numeric(10, 2), nullable=False)
    producto = db.relationship('Producto', backref='recetas')
    material = db.relationship('Material', backref='recetas')

# Control de Calidad
class ControlCalidad(db.Model):
    __tablename__ = 'control_calidad'
    id_control = db.Column(db.Integer, primary_key=True)
    id_orden_produccion = db.Column(db.Integer, db.ForeignKey('ordenes_produccion.id_orden_produccion'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    resultado = db.Column(db.Enum('aprobado', 'rechazado', 'reparacion'), nullable=False)
    observaciones = db.Column(db.Text)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    orden_produccion = db.relationship('OrdenProduccion', backref='controles_calidad')
    usuario = db.relationship('Usuario', backref='controles_calidad')

# Cliente
class Cliente(db.Model):
    __tablename__ = 'clientes'
    id_cliente = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    contacto = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    direccion = db.Column(db.Text)
    tipo = db.Column(db.Enum('distribuidor', 'mayorista', 'minorista', 'OEM'))

# Venta
class Venta(db.Model):
    __tablename__ = 'ventas'
    id_venta = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey('clientes.id_cliente'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    total = db.Column(db.Numeric(12, 2), nullable=False)
    estado = db.Column(db.Enum('pendiente', 'completada', 'cancelada'), default='pendiente')
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    cliente = db.relationship('Cliente', backref='ventas')
    usuario = db.relationship('Usuario', backref='ventas')

# Detalle Venta
class DetalleVenta(db.Model):
    __tablename__ = 'detalle_ventas'
    id_detalle = db.Column(db.Integer, primary_key=True)
    id_venta = db.Column(db.Integer, db.ForeignKey('ventas.id_venta'), nullable=False)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id_producto'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(12, 2), nullable=False)
    venta = db.relationship('Venta', backref='detalles')
    producto = db.relationship('Producto', backref='detalles_venta')

# Nómina
class Nomina(db.Model):
    __tablename__ = 'nominas'
    id_nomina = db.Column(db.Integer, primary_key=True)
    id_empleado = db.Column(db.Integer, db.ForeignKey('empleados.id_empleado'), nullable=False)
    periodo = db.Column(db.String(20), nullable=False)
    fecha_pago = db.Column(db.Date, nullable=False)
    salario_bruto = db.Column(db.Numeric(10, 2), nullable=False)
    deducciones = db.Column(db.Numeric(10, 2))
    bonos = db.Column(db.Numeric(10, 2))
    salario_neto = db.Column(db.Numeric(10, 2), nullable=False)
    empleado = db.relationship('Empleado', backref='nominas')

# Proyecto I+D
class ProyectoID(db.Model):
    __tablename__ = 'proyectos_i_d'
    id_proyecto = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    fecha_inicio = db.Column(db.Date)
    fecha_fin_estimada = db.Column(db.Date)
    presupuesto = db.Column(db.Numeric(12, 2))
    estado = db.Column(db.Enum('planificacion', 'en_desarrollo', 'completado', 'cancelado'), default='planificacion')

# Normativa Legal
class NormativaLegal(db.Model):
    __tablename__ = 'normativas_legales'
    id_normativa = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.Enum('ambiental', 'seguridad', 'laboral', 'calidad'), nullable=False)
    descripcion = db.Column(db.Text)
    fecha_actualizacion = db.Column(db.Date)
    aplicable_a = db.Column(db.String(100))

# Incidente
class Incidente(db.Model):
    __tablename__ = 'incidentes'
    id_incidente = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.Enum('seguridad', 'calidad', 'logistica'), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    id_area = db.Column(db.Integer, db.ForeignKey('areas_trabajo.id_area'))
    id_empleado_reporta = db.Column(db.Integer, db.ForeignKey('empleados.id_empleado'))
    estado = db.Column(db.Enum('reportado', 'investigacion', 'resuelto'), default='reportado')
    area = db.relationship('AreaTrabajo', backref='incidentes')
    empleado_reporta = db.relationship('Empleado', backref='incidentes_reportados')

# Activo de Producción
class ActivoProduccion(db.Model):
    __tablename__ = 'activos_produccion'
    id_activo = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.Enum('maquinaria', 'herramienta', 'equipo'), nullable=False)
    id_area = db.Column(db.Integer, db.ForeignKey('areas_trabajo.id_area'))
    fecha_adquisicion = db.Column(db.Date)
    estado = db.Column(db.Enum('operativo', 'mantenimiento', 'baja'), default='operativo')
    area = db.relationship('AreaTrabajo', backref='activos')

# Mantenimiento
class Mantenimiento(db.Model):
    __tablename__ = 'mantenimiento'
    id_mantenimiento = db.Column(db.Integer, primary_key=True)
    id_activo = db.Column(db.Integer, db.ForeignKey('activos_produccion.id_activo'), nullable=False)
    tipo = db.Column(db.Enum('preventivo', 'correctivo'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    descripcion = db.Column(db.Text)
    costo = db.Column(db.Numeric(10, 2))
    id_empleado = db.Column(db.Integer, db.ForeignKey('empleados.id_empleado'))
    activo = db.relationship('ActivoProduccion', backref='mantenimientos')
    empleado = db.relationship('Empleado', backref='mantenimientos_realizados')

# Configuración del Sistema
class ConfiguracionSistema(db.Model):
    __tablename__ = 'configuracion_sistema'
    id_config = db.Column(db.Integer, primary_key=True)
    parametro = db.Column(db.String(50), unique=True, nullable=False)
    valor = db.Column(db.Text)
    descripcion = db.Column(db.Text)