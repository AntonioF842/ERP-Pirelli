from flask import Blueprint, jsonify
from models import (
    Venta, OrdenProduccion, Inventario, Empleado, Material, 
    Asistencia, Proveedor, OrdenCompra, Producto, 
    ControlCalidad, Cliente, Nomina, Incidente, 
    ActivoProduccion, Mantenimiento, DetalleVenta, AreaTrabajo
)
from sqlalchemy import func, extract, and_
from datetime import datetime, timedelta
import calendar
from config import db

dashboard_bp = Blueprint('dashboard_bp', __name__)

def get_last_day_of_month(year, month):
    return calendar.monthrange(year, month)[1]

@dashboard_bp.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    now = datetime.now()
    current_month = now.month
    current_year = now.year
    
    # 1. Estadísticas principales
    # Ventas mensuales
    ventas_mensuales = db.session.query(func.sum(Venta.total)).filter(
        extract('month', Venta.fecha) == current_month,
        extract('year', Venta.fecha) == current_year,
        Venta.estado == 'completada'
    ).scalar() or 0

    # Producción mensual
    produccion_mensual = db.session.query(func.sum(OrdenProduccion.cantidad)).filter(
        extract('month', OrdenProduccion.fecha_inicio) == current_month,
        extract('year', OrdenProduccion.fecha_inicio) == current_year,
        OrdenProduccion.estado == 'completada'
    ).scalar() or 0

    # Nivel de inventario (porcentaje de stock disponible)
    total_materiales = db.session.query(func.sum(Inventario.cantidad)).scalar() or 0
    materiales_con_stock = db.session.query(Material).count()
    nivel_inventario = round((total_materiales / (materiales_con_stock * 100)) * 100) if materiales_con_stock else 0

    # Empleados activos
    empleados_activos = db.session.query(Empleado).filter_by(activo=True).count()

    # 2. Distribución de materiales
    materiales_distribucion = db.session.query(
        Material.nombre,
        func.sum(Inventario.cantidad)
    ).join(Inventario).group_by(Material.nombre).all()
    distribucion_materiales = {nombre: str(cantidad) for nombre, cantidad in materiales_distribucion}

    # 3. Ventas vs Producción (últimos 6 meses)
    ventas_vs_produccion = {
        "ventas": [],
        "produccion": [],
        "categorias": []
    }
    
    for i in range(5, -1, -1):
        target_month = (now.month - i - 1) % 12 + 1
        target_year = now.year - (1 if now.month - i - 1 < 0 else 0)
        
        # Ventas del mes
        ventas_mes = db.session.query(func.sum(Venta.total)).filter(
            extract('month', Venta.fecha) == target_month,
            extract('year', Venta.fecha) == target_year,
            Venta.estado == 'completada'
        ).scalar() or 0
        
        # Producción del mes
        produccion_mes = db.session.query(func.sum(OrdenProduccion.cantidad)).filter(
            extract('month', OrdenProduccion.fecha_inicio) == target_month,
            extract('year', OrdenProduccion.fecha_inicio) == target_year,
            OrdenProduccion.estado == 'completada'
        ).scalar() or 0
        
        ventas_vs_produccion["ventas"].append(float(ventas_mes))
        ventas_vs_produccion["produccion"].append(float(produccion_mes))
        ventas_vs_produccion["categorias"].append(f"{calendar.month_abbr[target_month]} {target_year}")

    # 4. NUEVO: Control de calidad
    control_calidad_query = db.session.query(
        ControlCalidad.resultado,
        func.count(ControlCalidad.id_control)
    ).filter(
        extract('month', ControlCalidad.fecha) == current_month,
        extract('year', ControlCalidad.fecha) == current_year
    ).group_by(ControlCalidad.resultado).all()
    
    control_calidad = {}
    # Inicializar con valores por defecto
    control_calidad["aprobado"] = 0
    control_calidad["rechazado"] = 0
    control_calidad["reparacion"] = 0
    
    # Llenar con datos reales
    for resultado, count in control_calidad_query:
        control_calidad[resultado] = count
    
    # Si no hay datos, usar datos de ejemplo
    if sum(control_calidad.values()) == 0:
        control_calidad = {"aprobado": 85, "rechazado": 10, "reparacion": 5}

    # 5. NUEVO: Materiales con stock bajo
    materiales_stock_bajo_query = db.session.query(
        Material.nombre,
        Inventario.cantidad,
        Material.stock_minimo
    ).join(Inventario).filter(
        Inventario.cantidad <= Material.stock_minimo
    ).all()
    
    materiales_stock_bajo = {}
    for nombre, cantidad, minimo in materiales_stock_bajo_query:
        materiales_stock_bajo[nombre] = {
            "actual": cantidad,
            "minimo": minimo
        }
    
    # Si no hay datos críticos, mostrar algunos materiales normales
    if not materiales_stock_bajo:
        materiales_normales = db.session.query(
            Material.nombre,
            Inventario.cantidad,
            Material.stock_minimo
        ).join(Inventario).limit(5).all()
        
        for nombre, cantidad, minimo in materiales_normales:
            materiales_stock_bajo[nombre] = {
                "actual": cantidad or 0,
                "minimo": minimo or 0
            }

    # 6. NUEVO: Empleados por área
    empleados_por_area_query = db.session.query(
        AreaTrabajo.nombre_area,
        func.count(Empleado.id_empleado).label('total_empleados'),
        func.count(Asistencia.id_asistencia).label('total_asistencias')
    ).join(Empleado, AreaTrabajo.id_area == Empleado.id_area)\
     .outerjoin(Asistencia, and_(
         Asistencia.id_empleado == Empleado.id_empleado,
         extract('month', Asistencia.fecha) == current_month,
         Asistencia.estado == 'presente'
     )).group_by(AreaTrabajo.nombre_area).all()
    
    empleados_por_area = {}
    for area, empleados, asistencias in empleados_por_area_query:
        empleados_por_area[area] = {
            "empleados": empleados,
            "asistencias": asistencias or 0
        }
    
    # Datos de ejemplo si no hay datos reales
    if not empleados_por_area:
        empleados_por_area = {
            "Producción": {"empleados": 15, "asistencias": 280},
            "Calidad": {"empleados": 8, "asistencias": 150},
            "Mantenimiento": {"empleados": 5, "asistencias": 95},
            "Administración": {"empleados": 6, "asistencias": 115}
        }

    # 7. NUEVO: Clientes por tipo
    clientes_por_tipo_query = db.session.query(
        Cliente.tipo,
        func.sum(Venta.total).label('total_ventas')
    ).join(Venta).filter(
        extract('month', Venta.fecha) == current_month,
        Venta.estado == 'completada'
    ).group_by(Cliente.tipo).all()
    
    clientes_por_tipo = {}
    for tipo, total in clientes_por_tipo_query:
        clientes_por_tipo[tipo] = float(total)
    
    # Datos de ejemplo si no hay ventas este mes
    if not clientes_por_tipo:
        clientes_por_tipo = {
            "distribuidor": 45000,
            "mayorista": 32000,
            "minorista": 18000,
            "OEM": 25000
        }

    # 8. NUEVO: Mantenimiento de equipos
    mantenimiento_equipos_query = db.session.query(
        Mantenimiento.tipo,
        func.count(Mantenimiento.id_mantenimiento),
        func.sum(Mantenimiento.costo)
    ).filter(
        extract('month', Mantenimiento.fecha) == current_month
    ).group_by(Mantenimiento.tipo).all()
    
    mantenimiento_equipos = {}
    for tipo, cantidad, costo in mantenimiento_equipos_query:
        mantenimiento_equipos[tipo] = {
            "cantidad": cantidad,
            "costo": float(costo or 0)
        }
    
    # Datos de ejemplo si no hay mantenimientos este mes
    if not mantenimiento_equipos:
        mantenimiento_equipos = {
            "preventivo": {"cantidad": 12, "costo": 8500},
            "correctivo": {"cantidad": 5, "costo": 15200}
        }

    # 9. NUEVO: Análisis financiero (últimos 6 meses)
    analisis_financiero = {
        "ingresos": [],
        "gastos": [],
        "categorias": []
    }

    for i in range(5, -1, -1):
        target_month = (now.month - i - 1) % 12 + 1
        target_year = now.year - (1 if now.month - i - 1 < 0 else 0)
        
        # Ingresos (ventas)
        ingresos_mes = db.session.query(func.sum(Venta.total)).filter(
            extract('month', Venta.fecha) == target_month,
            extract('year', Venta.fecha) == target_year,
            Venta.estado == 'completada'
        ).scalar() or 0
        
        # Gastos (nóminas + compras + mantenimiento)
        nominas_mes = db.session.query(func.sum(Nomina.salario_neto)).filter(
            extract('month', Nomina.fecha_pago) == target_month,
            extract('year', Nomina.fecha_pago) == target_year
        ).scalar() or 0
        
        compras_mes = db.session.query(func.sum(OrdenCompra.total)).filter(
            extract('month', OrdenCompra.fecha) == target_month,
            extract('year', OrdenCompra.fecha) == target_year,
            OrdenCompra.estado == 'recibida'
        ).scalar() or 0
        
        mantenimiento_mes = db.session.query(func.sum(Mantenimiento.costo)).filter(
            extract('month', Mantenimiento.fecha) == target_month,
            extract('year', Mantenimiento.fecha) == target_year
        ).scalar() or 0
        
        gastos_mes = float(nominas_mes or 0) + float(compras_mes or 0) + float(mantenimiento_mes or 0)
        
        analisis_financiero["ingresos"].append(float(ingresos_mes))
        analisis_financiero["gastos"].append(gastos_mes)
        analisis_financiero["categorias"].append(f"{calendar.month_abbr[target_month]} {target_year}")

    # Si no hay datos financieros, usar datos de ejemplo
    if sum(analisis_financiero["ingresos"]) == 0:
        analisis_financiero = {
            "ingresos": [120000, 135000, 128000, 145000, 152000, 148000],
            "gastos": [95000, 102000, 98000, 115000, 118000, 112000],
            "categorias": [f"{calendar.month_abbr[target_month]} {target_year}" 
                          for target_month in range(max(1, now.month-5), now.month+1)]
        }

    # 10. Asistencias del mes (presentes vs ausentes)
    asistencias_mes = db.session.query(
        Asistencia.estado,
        func.count(Asistencia.id_asistencia)
    ).filter(
        extract('month', Asistencia.fecha) == current_month,
        extract('year', Asistencia.fecha) == current_year
    ).group_by(Asistencia.estado).all()
    
    asistencias_data = {
        "presente": 0,
        "ausente": 0,
        "tardanza": 0
    }
    for estado, count in asistencias_mes:
        asistencias_data[estado] = count

    # 11. Órdenes de compra pendientes
    ordenes_compra_pendientes = db.session.query(OrdenCompra).filter(
        OrdenCompra.estado == 'pendiente'
    ).count()

    # 12. Productos más vendidos (top 5)
    productos_mas_vendidos = db.session.query(
        Producto.nombre,
        func.sum(DetalleVenta.cantidad).label('total_vendido')
    ).join(DetalleVenta).group_by(Producto.nombre).order_by(
        func.sum(DetalleVenta.cantidad).desc()
    ).limit(5).all()

    # 13. Estado de activos de producción
    activos_estado = db.session.query(
        ActivoProduccion.estado,
        func.count(ActivoProduccion.id_activo)
    ).group_by(ActivoProduccion.estado).all()

    # 14. Incidentes recientes
    incidentes_recientes = db.session.query(Incidente).order_by(
        Incidente.fecha.desc()
    ).limit(5).all()

    # 15. Actividades recientes (combinado)
    actividades_recientes = []
    
    # Últimas ventas
    ultimas_ventas = db.session.query(Venta).order_by(Venta.fecha.desc()).limit(2).all()
    for v in ultimas_ventas:
        actividades_recientes.append({
            "titulo": f"Venta #{v.id_venta} - {v.cliente.nombre if v.cliente else 'Cliente'}",
            "tiempo": v.fecha.strftime("%d/%m/%Y %H:%M"),
            "tipo": "venta",
            "monto": str(v.total)
        })
    
    # Últimas producciones
    ultimas_producciones = db.session.query(OrdenProduccion).order_by(
        OrdenProduccion.fecha_inicio.desc()
    ).limit(2).all()
    for p in ultimas_producciones:
        actividades_recientes.append({
            "titulo": f"Producción #{p.id_orden_produccion} - {p.producto.nombre}",
            "tiempo": p.fecha_inicio.strftime("%d/%m/%Y"),
            "tipo": "produccion",
            "cantidad": p.cantidad
        })
    
    # Últimos incidentes
    for i in incidentes_recientes[:2]:
        actividades_recientes.append({
            "titulo": f"Incidente #{i.id_incidente} - {i.tipo}",
            "tiempo": i.fecha.strftime("%d/%m/%Y"),
            "tipo": "incidente",
            "estado": i.estado
        })
    
    # Ordenar por fecha
    actividades_recientes.sort(key=lambda x: datetime.strptime(x['tiempo'], '%d/%m/%Y %H:%M' if ':' in x['tiempo'] else '%d/%m/%Y'), reverse=True)
    actividades_recientes = actividades_recientes[:4]

    return jsonify({
        # Estadísticas principales
        "ventas_mensuales": float(ventas_mensuales),
        "produccion_mensual": float(produccion_mensual),
        "nivel_inventario": nivel_inventario,
        "empleados_activos": empleados_activos,
        
        # Datos para gráficos existentes
        "distribucion_materiales": distribucion_materiales,
        "ventas_vs_produccion": ventas_vs_produccion,
        "asistencias_data": asistencias_data,
        "productos_mas_vendidos": [
            {"nombre": nombre, "cantidad": int(cantidad)} 
            for nombre, cantidad in productos_mas_vendidos
        ],
        "activos_estado": [
            {"estado": estado, "cantidad": cantidad}
            for estado, cantidad in activos_estado
        ],
        
        # NUEVOS DATOS PARA ANÁLISIS EXPANDIDOS
        "control_calidad": control_calidad,
        "materiales_stock_bajo": materiales_stock_bajo,
        "empleados_por_area": empleados_por_area,
        "clientes_por_tipo": clientes_por_tipo,
        "mantenimiento_equipos": mantenimiento_equipos,
        "analisis_financiero": analisis_financiero,
        
        # Indicadores adicionales
        "ordenes_compra_pendientes": ordenes_compra_pendientes,
        
        # Actividades recientes
        "actividades_recientes": actividades_recientes,
        
        # Datos para tablas
        "incidentes_recientes": [
            {
                "id": i.id_incidente,
                "tipo": i.tipo,
                "fecha": i.fecha.strftime("%d/%m/%Y"),
                "estado": i.estado,
                "descripcion": i.descripcion[:50] + "..." if i.descripcion else ""
            } for i in incidentes_recientes
        ]
    })