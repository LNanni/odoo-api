import xmlrpc.client
import os
from app.models.endpoint import *
from app.services.fatherService import FatherService
from dotenv import load_dotenv

load_dotenv()

class InvoiceService(FatherService):
    def __init__(self):
        super().__init__()

    def getAllInvoices(self):
        try:
            uid = super().authenticate()
            
            if(type(uid) != int and "Autenticacion" in uid):
                return ["Error: Autenticacion fallida"]

            list_invoices = models.execute_kw(
                self._Db, uid, self._Password,
                'account.move', 'search_read',
                [[]],  # sin filtros
                {'fields': ['name', 'date', 'state', 'amount_total']}
            )
            return list_invoices
        except Exception as e:
            return ["Error: " + str(e)]