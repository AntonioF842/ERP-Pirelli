from flask import Blueprint, jsonify, request
from models import Nomina, Empleado, db
from datetime import datetime

payroll_bp = Blueprint('payroll', __name__)

@payroll_bp.route('/payroll', methods=['GET'])
def get_payrolls():
    payrolls = Nomina.query.all()
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
def get_payroll(id):
    payroll = Nomina.query.get_or_404(id)
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
def create_payroll():
    data = request.get_json()
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
    return jsonify({'message': 'Payroll record created successfully'}), 201

@payroll_bp.route('/payroll/<int:id>', methods=['PUT'])
def update_payroll(id):
    payroll = Nomina.query.get_or_404(id)
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
    return jsonify({'message': 'Payroll record updated successfully'})

@payroll_bp.route('/payroll/<int:id>', methods=['DELETE'])
def delete_payroll(id):
    payroll = Nomina.query.get_or_404(id)
    db.session.delete(payroll)
    db.session.commit()
    return jsonify({'message': 'Payroll record deleted successfully'})