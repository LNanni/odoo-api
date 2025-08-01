from flask import Blueprint, request, jsonify
from app.services.partners import PartnerService

# Crear blueprint para partners
bp = Blueprint('partners', __name__, url_prefix='/api/partners')

@bp.route('/', methods=['GET'])
def getAllPartners():
    partnerService = PartnerService()
    partners = partnerService.getAllPartners()
    if "Error" in partners[0]:
        return jsonify(
            {
                "status": "error",
                "message": partners[0].split(": ")[1]
            }
        ), 401
    else:
        return jsonify(
            {
                "status": "success",
                "clients": partners,
                "length": len(partners)
            }), 200  
