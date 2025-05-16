from flask import Blueprint, jsonify
from models import (
    Venta, OrdenProduccion, Inventario, Empleado, Material, 
    Asistencia, Proveedor, OrdenCompra, Producto, 
    ControlCalidad, Cliente, Nomina, Incidente, 
    ActivoProduccion, Mantenimiento, DetalleVenta
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
    distribucion_materiales = {nombre: cantidad for nombre, cantidad in materiales_distribucion}

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

    # 4. Asistencias del mes (presentes vs ausentes)
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

    # 5. Órdenes de compra pendientes
    ordenes_compra_pendientes = db.session.query(OrdenCompra).filter(
        OrdenCompra.estado == 'pendiente'
    ).count()

    # 6. Productos más vendidos (top 5)
    productos_mas_vendidos = db.session.query(
        Producto.nombre,
        func.sum(DetalleVenta.cantidad).label('total_vendido')
    ).join(DetalleVenta).group_by(Producto.nombre).order_by(
        func.sum(DetalleVenta.cantidad).desc()
    ).limit(5).all()

    # 7. Estado de activos de producción
    activos_estado = db.session.query(
        ActivoProduccion.estado,
        func.count(ActivoProduccion.id_activo)
    ).group_by(ActivoProduccion.estado).all()

    # 8. Incidentes recientes
    incidentes_recientes = db.session.query(Incidente).order_by(
        Incidente.fecha.desc()
    ).limit(5).all()

    # 9. Actividades recientes (combinado)
    actividades_recientes = []
    
    # Últimas ventas
    ultimas_ventas = db.session.query(Venta).order_by(Venta.fecha.desc()).limit(2).all()
    for v in ultimas_ventas:
        actividades_recientes.append({
            "titulo": f"Venta #{v.id_venta} - {v.cliente.nombre if v.cliente else 'Cliente'}",
            "tiempo": v.fecha.strftime("%d/%m/%Y %H:%M"),
            "tipo": "venta",
            "monto": v.total
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
        
        # Datos para gráficos
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