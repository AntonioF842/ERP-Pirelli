from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from routes.auth import role_required
from models import Nomina, Empleado, db
from datetime import datetime

payroll_bp = Blueprint('payroll', __name__)

@payroll_bp.route('/payroll', methods=['GET'])
@login_required
def get_payrolls():
    # Admin tiene acceso completo
    if current_user.rol == 'admin':
        payrolls = Nomina.query.all()
    # Supervisor solo ve nóminas de su departamento
    elif current_user.rol == 'supervisor':
        # Asumiendo que el supervisor tiene un id_area asociado
        payrolls = Nomina.query.join(Empleado).filter(
            Empleado.id_area == current_user.id_area
        ).all()
    # Empleado solo ve sus propias nóminas
    elif current_user.rol == 'empleado':
        payrolls = Nomina.query.filter_by(id_empleado=current_user.id_empleado).all()
    else:
        return jsonify({"error": "No autorizado"}), 403

    return jsonify([{
        'id_nomina': payroll.id_nomina,
        'id_empleado': payroll.id_empleado,
        'empleado_name': f"{payroll.empleado.nombre} {payroll.empleado.apellidos}",
        'periodo': payroll.periodo,
        'fecha_pago': payroll.fecha_pago.isoformat(),
        'salario_bruto': float(payroll.salario_bruto),
        'deducciones': float(payroll.deducciones) if payroll.deducciones else None,
        'bonos': float(payroll.bonos) if payroll.bonos else None,
        'salario_neto': float(payroll.salario_neto)
    } for payroll in payrolls])

@payroll_bp.route('/payroll/<int:id>', methods=['GET'])
@login_required
def get_payroll(id):
    payroll = Nomina.query.get_or_404(id)
    
    # Verificar permisos
    if current_user.rol == 'empleado' and payroll.id_empleado != current_user.id_empleado:
        return jsonify({"error": "Solo puedes ver tus propias nóminas"}), 403
    elif current_user.rol == 'supervisor':
        # Verificar si el empleado de la nómina pertenece al departamento del supervisor
        empleado = Empleado.query.get(payroll.id_empleado)
        if not empleado or empleado.id_area != current_user.id_area:
            return jsonify({"error": "No autorizado para ver esta nómina"}), 403
    
    return jsonify({
        'id_nomina': payroll.id_nomina,
        'id_empleado': payroll.id_empleado,
        'empleado_name': f"{payroll.empleado.nombre} {payroll.empleado.apellidos}",
        'periodo': payroll.periodo,
        'fecha_pago': payroll.fecha_pago.isoformat(),
        'salario_bruto': float(payroll.salario_bruto),
        'deducciones': float(payroll.deducciones) if payroll.deducciones else None,
        'bonos': float(payroll.bonos) if payroll.bonos else None,
        'salario_neto': float(payroll.salario_neto)
    })

@payroll_bp.route('/payroll', methods=['POST'])
@role_required('admin', 'supervisor')
def create_payroll():
    data = request.get_json()
    
    # Validación adicional para supervisores
    if current_user.rol == 'supervisor':
        empleado = Empleado.query.get(data['id_empleado'])
        if not empleado or empleado.id_area != current_user.id_area:
            return jsonify({"error": "Solo puedes crear nóminas para tu departamento"}), 403

    new_payroll = Nomina(
        id_empleado=data['id_empleado'],
        periodo=data['periodo'],
        fecha_pago=datetime.strptime(data['fecha_pago'], '%Y-%m-%d').date(),
        salario_bruto=data['salario_bruto'],
        deducciones=data.get('deducciones'),
        bonos=data.get('bonos'),
        salario_neto=data['salario_neto']
    )
    db.session.add(new_payroll)
    db.session.commit()
    return jsonify({'message': 'Registro de nómina creado exitosamente'}), 201

@payroll_bp.route('/payroll/<int:id>', methods=['PUT'])
@role_required('admin', 'supervisor')
def update_payroll(id):
    payroll = Nomina.query.get_or_404(id)
    
    # Validación adicional para supervisores
    if current_user.rol == 'supervisor':
        empleado = Empleado.query.get(payroll.id_empleado)
        if not empleado or empleado.id_area != current_user.id_area:
            return jsonify({"error": "Solo puedes modificar nóminas de tu departamento"}), 403

    data = request.get_json()
    payroll.id_empleado = data.get('id_empleado', payroll.id_empleado)
    payroll.periodo = data.get('periodo', payroll.periodo)
    if 'fecha_pago' in data:
        payroll.fecha_pago = datetime.strptime(data['fecha_pago'], '%Y-%m-%d').date()
    payroll.salario_bruto = data.get('salario_bruto', payroll.salario_bruto)
    payroll.deducciones = data.get('deducciones', payroll.deducciones)
    payroll.bonos = data.get('bonos', payroll.bonos)
    payroll.salario_neto = data.get('salario_neto', payroll.salario_neto)
    db.session.commit()
    return jsonify({'message': 'Registro de nómina actualizado exitosamente'})

@payroll_bp.route('/payroll/<int:id>', methods=['DELETE'])
@role_required('admin')
def delete_payroll(id):
    payroll = Nomina.query.get_or_404(id)
    db.session.delete(payroll)
    db.session.commit()
    return jsonify({'message': 'Registro de nómina eliminado exitosamente'})