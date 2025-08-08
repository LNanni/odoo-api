from typing import Any, Dict
from dotenv import load_dotenv
from app.models.endpoint import *

class PartnerService(FatherService):
    def __init__(self):
        super().__init__()

    def getAllPartners(self):
        try:
            uid = super().authenticate()
            
            if(type(uid) != int and "Autenticacion" in uid):
                return ["Error: Autenticacion fallida"]
            
            # Ahora usar el uid para ejecutar la consulta
            listPartners = models.execute_kw(
                self._Db, uid, self._Password,
                'res.partner', 'search_read',
                [[  #['comment', 'ilike', 'try'],
                ]],  # sin filtros
                {'fields': ['name', 'phone', 'email', 'comment']}
            )

            return listPartners
        except Exception as e:
            return ["Error: " + str(e)]

    def getPartnerByName(self, name):
        try:
            uid = super().authenticate()

            if(type(uid) != int and "Autenticacion" in uid):
                return ["Error: Autenticacion fallida"]

            listPartners = models.execute_kw(
                    self._Db, uid, self._Password,
                    'res.partner', 'search_read',
                    [[  
                        ['name', 'ilike', name],
                    ]],  
                    {'fields': ['id', 'name']}
                )

            if len(listPartners) == 1:
                return listPartners[0]
            else: 
                return ["Error: Partner no encontrado"]
        except Exception as e:
            return ["Error: "+ str(e)]

    def createParner(self, body: Dict[str, Any]):
        try:
            uid = super().authenticate()

            verifyNotExist = self.getPartnerByName(body.get('name'))
            if(type(verifyNotExist) is dict):
                return {"status":"error", "message": "Cliente ya existe en el sistema"}

            partnerCreated = models.execute_kw(
                    self._Db, uid, self._Password,
                    'res.partner', 'create',
                    [{
                        "vat_label": body.get('id_label'),
                        "company_type": body.get('company_type'),
                        "name": body.get('name'),
                        "email": body.get('email'),
                        "phone": body.get('phone'),
                        "type_address_label": "Dirección",
                        "street": body.get('location'),
                        "city": body.get('city'),
                        "state_id": 570,
                        "zip": body.get('cp'),
                        "country_id": 10,
                        "partner_vat_placeholder": "20055361682, o no aplicable",
                        "l10n_latam_identification_type_id": 6,
                        "vat": body.get('cuil'),
                        "lang": "es_ES",
                        "property_product_pricelist": 1,
                        "industry_id": False,
                        "is_company": False,
                        "active": True,
                        "type": "contact",
                        "fiscal_country_codes": "AR",
                        "active_lang_count": 1,
                        "display_name": body.get('name')
                    }]
                )
            return {"status": "Succes", "data": partnerCreated }
        except Exception as e:
            return {"status": "error", "message": str(e)}