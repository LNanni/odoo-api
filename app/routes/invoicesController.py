from flask import Blueprint, request, jsonify
from app.services.invoices import InvoiceService
from datetime import datetime

# Crear blueprint para partners
bp = Blueprint('invoices', __name__, url_prefix='/api/invoices')

@bp.route('/', methods=['GET'])
def getAllInvoices():
    invoicesService = InvoiceService()
    data = invoicesService.getAllInvoices()
    if "Error" in data[0]:
        response = jsonify(
                {
                    "status": "error",
                    "message": str(data)
                }
            )
        if "solicitar acceso" in data[0]:
            return response, 401
        else:
            return response, 500
    else:
        return jsonify(
            {
                "status": "success",
                "clients": data,
                "length": len(data)
            }), 200  

@bp.route('/', methods=['POST'])
def createInvoices():
    params = {
        "p": int(request.args.get('p')),
        "s": int(request.args.get('s')),
        "emitido_inicio": datetime.strptime(request.args.get('emitido_inicio'), "%Y-%m-%d").date(),
        "emitido_fin": datetime.strptime(request.args.get('emitido_fin'), "%Y-%m-%d").date(),
        "vencimiento_inicio": datetime.strptime(request.args.get('vencimiento_inicio'), "%Y-%m-%d").date(),
        "vencimiento_fin": datetime.strptime(request.args.get('vencimiento_fin'), "%Y-%m-%d").date(),
        "include_items": True if request.args.get('include_items').lower == 'true' else False,
    }
    invoiceService = InvoiceService()
    data = invoiceService.createInvoices(params)
    if isinstance(data, dict) and data.get('status') == 'success':
        return jsonify(data), 201
    else:
        return jsonify({
            "status": "error",
            "message": data.get('error')
        }), 500