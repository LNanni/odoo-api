from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.services.partner_service import PartnerService
from app.utils.exceptions import OdooError, PartnerNotFoundError
from app.utils.validators import PartnerSchema, PartnerUpdateSchema
from app.utils.helpers import create_response, create_error_response

# Crear blueprint para partners
bp = Blueprint('partners', __name__, url_prefix='/api/partners')

# Instanciar esquemas de validación
partner_schema = PartnerSchema()
partner_update_schema = PartnerUpdateSchema()


@bp.route('/', methods=['GET'])
def list_partners():
    """
    GET /api/partners/
    Listar todos los partners con filtros opcionales
    """
    try:
        # Obtener parámetros de query
        filters = {}
        fields = None
        
        # Filtros desde query params
        if request.args.get('is_company'):
            filters['is_company'] = request.args.get('is_company').lower() == 'true'
        if request.args.get('customer'):
            filters['customer'] = request.args.get('customer').lower() == 'true'
        if request.args.get('vendor'):
            filters['vendor'] = request.args.get('vendor').lower() == 'true'
        if request.args.get('name'):
            filters['name'] = request.args.get('name')
        if request.args.get('email'):
            filters['email'] = request.args.get('email')
        
        # Campos específicos
        if request.args.get('fields'):
            fields = request.args.get('fields').split(',')
        
        # Límite de resultados
        limit = request.args.get('limit', type=int, default=50)
        
        # Crear servicio y obtener partners
        service = PartnerService()
        partners = service.list_partners(filters, fields)
        
        # Aplicar límite
        if limit and len(partners) > limit:
            partners = partners[:limit]
        
        return create_response(
            success=True,
            data=partners,
            message=f"Se encontraron {len(partners)} partners",
            count=len(partners)
        )
        
    except OdooError as e:
        return create_error_response(str(e), 500)
    except Exception as e:
        return create_error_response(f"Error interno del servidor: {str(e)}", 500)


@bp.route('/<int:partner_id>', methods=['GET'])
def get_partner(partner_id):
    """
    GET /api/partners/{partner_id}
    Obtener un partner específico por ID
    """
    try:
        # Campos específicos
        fields = None
        if request.args.get('fields'):
            fields = request.args.get('fields').split(',')
        
        # Crear servicio y obtener partner
        service = PartnerService()
        partner = service.get_partner(partner_id, fields)
        
        return create_response(
            success=True,
            data=partner,
            message=f"Partner {partner_id} obtenido correctamente"
        )
        
    except PartnerNotFoundError as e:
        return create_error_response(str(e), 404)
    except OdooError as e:
        return create_error_response(str(e), 500)
    except Exception as e:
        return create_error_response(f"Error interno del servidor: {str(e)}", 500)


@bp.route('/', methods=['POST'])
def create_partner():
    """
    POST /api/partners/
    Crear un nuevo partner
    """
    try:
        # Validar datos de entrada
        data = request.get_json()
        if not data:
            return create_error_response("Datos JSON requeridos", 400)
        
        # Validar con marshmallow
        try:
            validated_data = partner_schema.load(data)
        except ValidationError as e:
            return create_error_response(f"Error de validación: {e.messages}", 400)
        
        # Crear servicio y crear partner
        service = PartnerService()
        new_partner = service.create_partner(validated_data)
        
        return create_response(
            success=True,
            data=new_partner,
            message="Partner creado correctamente",
            status_code=201
        ), 201
        
    except OdooError as e:
        return create_error_response(str(e), 500)
    except Exception as e:
        return create_error_response(f"Error interno del servidor: {str(e)}", 500)


@bp.route('/<int:partner_id>', methods=['PUT'])
def update_partner(partner_id):
    """
    PUT /api/partners/{partner_id}
    Actualizar un partner existente
    """
    try:
        # Validar datos de entrada
        data = request.get_json()
        if not data:
            return create_error_response("Datos JSON requeridos", 400)
        
        # Validar con marshmallow
        try:
            validated_data = partner_update_schema.load(data)
        except ValidationError as e:
            return create_error_response(f"Error de validación: {e.messages}", 400)
        
        # Crear servicio y actualizar partner
        service = PartnerService()
        updated_partner = service.update_partner(partner_id, validated_data)
        
        return create_response(
            success=True,
            data=updated_partner,
            message=f"Partner {partner_id} actualizado correctamente"
        )
        
    except PartnerNotFoundError as e:
        return create_error_response(str(e), 404)
    except OdooError as e:
        return create_error_response(str(e), 500)
    except Exception as e:
        return create_error_response(f"Error interno del servidor: {str(e)}", 500)


@bp.route('/<int:partner_id>', methods=['DELETE'])
def delete_partner(partner_id):
    """
    DELETE /api/partners/{partner_id}
    Eliminar un partner
    """
    try:
        # Crear servicio y eliminar partner
        service = PartnerService()
        service.delete_partner(partner_id)
        
        return create_response(
            success=True,
            message=f"Partner {partner_id} eliminado correctamente"
        )
        
    except PartnerNotFoundError as e:
        return create_error_response(str(e), 404)
    except OdooError as e:
        return create_error_response(str(e), 500)
    except Exception as e:
        return create_error_response(f"Error interno del servidor: {str(e)}", 500)


@bp.route('/search', methods=['GET'])
def search_partners():
    """
    GET /api/partners/search?q={search_term}
    Buscar partners por término de búsqueda
    """
    try:
        # Obtener término de búsqueda
        search_term = request.args.get('q')
        if not search_term:
            return create_error_response("Parámetro 'q' requerido para búsqueda", 400)
        
        # Campos específicos
        fields = None
        if request.args.get('fields'):
            fields = request.args.get('fields').split(',')
        
        # Crear servicio y buscar partners
        service = PartnerService()
        partners = service.search_partners(search_term, fields)
        
        return create_response(
            success=True,
            data=partners,
            message=f"Búsqueda completada. Se encontraron {len(partners)} partners",
            count=len(partners)
        )
        
    except OdooError as e:
        return create_error_response(str(e), 500)
    except Exception as e:
        return create_error_response(f"Error interno del servidor: {str(e)}", 500) 