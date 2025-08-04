import array
from ctypes import Array
from turtle import reset
from flask import Blueprint, request, jsonify
from werkzeug.wrappers import response
from app.services.partners import PartnerService

# Crear blueprint para partners
bp = Blueprint('partners', __name__, url_prefix='/api/partners')

@bp.route('/', methods=['GET'])
def getAllPartners():
    partnerService = PartnerService()
    data = partnerService.getAllPartners()
    if "Error" in data[0]:
        response = jsonify({
            "status": "error",
            "message": str(data)
        })
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

@bp.route('/search', methods=['GET'])
def getPartnerByName():
    partnerService = PartnerService()
    partnerName = request.args.get('name', '##')
    if(partnerName == "##"):
        return jsonify({
            "status": "error",
            "message": "El nombre del partner es requerido"
        }), 400
    data = partnerService.getPartnerByName(partnerName)
    
    if type(data) is list:
        response = jsonify({
            "status": "error",
            "message": str(data[0])
        })
        if "solicitar acceso" in data[0]:
            return response, 401
        elif "no encontrado" in data[0]:
            return response, 404
        else: 
            return response, 500
    else:
        return jsonify({
            "status": "success",
            "client": data
        }), 200