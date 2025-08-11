from flask import Blueprint, request, jsonify
from urllib3 import response
from app.services.transactions import TransactionService

bp = Blueprint('transactions', __name__, url_prefix='/api/transactions')

@bp.route('/', methods=['GET'])
def getAllTransactions():
    transactionService = TransactionService()
    data = transactionService.getAllTransactions()
    if "Error" in data:
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

@bp.route('/', methods=['POST'])
def createTransaction():
    transactionData = request.get_json()

    if not transactionData:
        return jsonify({
            "status": "error",
            "message": "Datos de tansaccion requeridos"
        }), 400

    transactionService = TransactionService()
    result = transactionService.createTransaction(transactionData)

    if(type(result) is str and "Error" in result):
        response = jsonify({
            "status": "error",
            "message": result
        })
        if "solicite acceso" in result:
            return response, 401
        elif "no encontra" in result:
            return response, 404
        else:
            return response, 500
    else:
        return jsonify({
            "status": "ok",
            "data": result
        }), 201
