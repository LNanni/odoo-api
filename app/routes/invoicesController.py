from flask import Blueprint, request, jsonify
from app.services.invoices import InvoiceService

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
