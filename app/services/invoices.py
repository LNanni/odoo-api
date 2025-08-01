import xmlrpc.client
import os
from app.models.endpoint import *
from app.services.fatherService import FatherService
from dotenv import load_dotenv

load_dotenv()

class InvoiceService(FatherService):
    def __init__(self):
        super().__init__()

    def getInvoicesList(self):
        try:
            uid = common.authenticate(self._Db, self._Username, self._Password, {})
            if not uid:
                return ["Error: Autenticacion fallida"]
            
            list_invoices = models.execute_kw(
                self._Db, uid, self._Password,
                'account.move', 'search',
                [[  #['comment', 'ilike', 'try'],
                ]],  # sin filtros
            )
            return list_invoices
        except Exception as e:
            return ["Error: " + str(e)]