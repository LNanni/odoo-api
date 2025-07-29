import xmlrpc.client
import os
from dotenv import load_dotenv
from models.endpoint import models
from models.establish import *

load_dotenv()

class PartnerService:
    def __init__(self):
        self._URL = os.getenv('ODOO_URL')
        self._Db = os.getenv('ODOO_DB')
        self._Username = os.getenv('ODOO_USERNAME')
        self._Password = os.getenv('ODOO_PASSWORD')

    def getPartnersList(self):
        try:
            list_partners = models.execute_kw(
                self._Db, self._Username, self._Password,
                'res.partner', 'search',
                [[  #['comment', 'ilike', 'try'],
                    #['name', 'ilike', 'Iñaki']
                ]],  # sin filtros
            )

            return list_partners
        except Exception as e:
            print(e)
            return []