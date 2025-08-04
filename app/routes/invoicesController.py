from flask import Blueprint, request, jsonify
from app.services.invoices import InvoiceService
from app.clients.mikrowisp import MikrowispClient

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
    invoiceService = InvoiceService()
    data = invoiceService.createInvoices()
    if isinstance(data, dict) and data.get('status') == 'success':
        return jsonify(data), 201
    else:
        return jsonify({
            "status": "error",
            "message": data.get('error')
        }), 500