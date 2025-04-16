from flask import Blueprint, jsonify
from models import Venta, OrdenProduccion, Inventario, Empleado, Material
from sqlalchemy import func
from config import db

dashboard_bp = Blueprint('dashboard_bp', __name__)

@dashboard_bp.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    # Ventas mensuales (suma del mes actual)
    ventas_mensuales = db.session.query(func.sum(Venta.total)).filter(
        func.extract('month', Venta.fecha) == func.extract('month', func.now()),
        func.extract('year', Venta.fecha) == func.extract('year', func.now())
    ).scalar() or 0

    # Producción mensual (suma del mes actual)
    produccion_mensual = db.session.query(func.sum(OrdenProduccion.cantidad)).filter(
        func.extract('month', OrdenProduccion.fecha_inicio) == func.extract('month', func.now()),
        func.extract('year', OrdenProduccion.fecha_inicio) == func.extract('year', func.now())
    ).scalar() or 0

    # Nivel de inventario (cantidad total)
    inventario = db.session.query(Inventario).first()
    nivel_inventario = inventario.cantidad if inventario else 0

    # Empleados activos
    empleados_activos = db.session.query(Empleado).filter_by(activo=True).count()

    # Distribución de materiales (ejemplo: suma por nombre)
    materiales = db.session.query(Material.nombre, func.sum(Inventario.cantidad))\
        .join(Inventario, Material.id_material == Inventario.id_material)\
        .group_by(Material.nombre).all()
    distribucion_materiales = {nombre: cantidad for nombre, cantidad in materiales}

    # Ventas vs Producción (últimos 5 meses)
    ventas_vs_produccion = {
        "ventas": [],
        "produccion": [],
        "categorias": []
    }
    from datetime import datetime, timedelta
    import calendar

    now = datetime.now()
    for i in range(5, 0, -1):
        # Calcular el primer día del mes correspondiente
        mes_dt = (now.replace(day=1) - timedelta(days=1)).replace(day=1)
        for _ in range(i-1):
            mes_dt = (mes_dt - timedelta(days=1)).replace(day=1)
        mes_num = mes_dt.month
        anio_num = mes_dt.year
        mes_nombre = calendar.month_abbr[mes_num].capitalize()

        ventas_mes = db.session.query(func.sum(Venta.total)).filter(
            func.extract('month', Venta.fecha) == mes_num,
            func.extract('year', Venta.fecha) == anio_num
        ).scalar() or 0
        prod_mes = db.session.query(func.sum(OrdenProduccion.cantidad)).filter(
            func.extract('month', OrdenProduccion.fecha_inicio) == mes_num,
            func.extract('year', OrdenProduccion.fecha_inicio) == anio_num
        ).scalar() or 0
        ventas_vs_produccion["ventas"].append(ventas_mes)
        ventas_vs_produccion["produccion"].append(prod_mes)
        ventas_vs_produccion["categorias"].append(mes_nombre)

    # Actividades recientes (últimas 4 actividades)
    actividades_recientes = []
    ultimas_ventas = db.session.query(Venta).order_by(Venta.fecha.desc()).limit(2).all()
    for v in ultimas_ventas:
        actividades_recientes.append({
            "titulo": f"Venta #{v.id_venta} registrada",
            "tiempo": v.fecha.strftime("%d/%m/%Y %H:%M")
        })
    ultimas_producciones = db.session.query(OrdenProduccion).order_by(OrdenProduccion.fecha_inicio.desc()).limit(2).all()
    for p in ultimas_producciones:
        actividades_recientes.append({
            "titulo": f"Producción #{p.id_orden_produccion} registrada",
            "tiempo": p.fecha_inicio.strftime("%d/%m/%Y")
        })

    # Ordenar por fecha
    actividades_recientes = sorted(actividades_recientes, key=lambda x: x["tiempo"], reverse=True)[:4]

    return jsonify({
        "ventas_mensuales": ventas_mensuales,
        "produccion_mensual": produccion_mensual,
        "nivel_inventario": nivel_inventario,
        "empleados_activos": empleados_activos,
        "distribucion_materiales": distribucion_materiales,
        "ventas_vs_produccion": ventas_vs_produccion,
        "actividades_recientes": actividades_recientes
    })
