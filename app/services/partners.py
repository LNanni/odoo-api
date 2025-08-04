import xmlrpc.client
import os
from dotenv import load_dotenv
from app.models.endpoint import *
from app.services.fatherService import FatherService

load_dotenv()

class PartnerService(FatherService):
    def __init__(self):
        super().__init__()

    def getAllPartners(self):
        try:
            uid = super().authenticate()
            
            if(type(uid) != int and "Autenticacion" in uid):
                return ["Error: Autenticacion fallida"]
            
            # Ahora usar el uid para ejecutar la consulta
            list_partners = models.execute_kw(
                self._Db, uid, self._Password,
                'res.partner', 'search_read',
                [[  #['comment', 'ilike', 'try'],
                ]],  # sin filtros
                {'fields': ['name', 'phone', 'email', 'comment']}
            )

            return list_partners
        except Exception as e:
            print(e)
            return ["Error: " + str(e)]