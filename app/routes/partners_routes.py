from flask import Blueprint, request, jsonify
from app.services.partners import PartnerService

# Crear blueprint para partners
bp = Blueprint('partners', __name__, url_prefix='/api/partners')

@bp.route('/', methods=['GET'])
def getAllPartners():
    partnerService = PartnerService()
    partners = partnerService.getPartnersList()
    return jsonify(partners)
