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
