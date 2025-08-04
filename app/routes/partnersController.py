from flask import Blueprint, request, jsonify
from app.services.partners import PartnerService

# Crear blueprint para partners
bp = Blueprint('partners', __name__, url_prefix='/api/partners')

@bp.route('/', methods=['GET'])
def getAllPartners():
    partnerService = PartnerService()
    data = partnerService.getAllPartners()
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
