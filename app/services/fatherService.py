from dotenv import load_dotenv
import os
from app.models.endpoint import *

load_dotenv()

class FatherService():
    def __init__(self):
        self._URL = os.getenv('ODOO_URL')
        self._Db = os.getenv('ODOO_DB')
        self._Username = os.getenv('ODOO_USERNAME')
        self._Password = os.getenv('ODOO_PASSWORD')

    def authenticate(self): 
        try:
            uid = common.authenticate(self._Db, self._Username, self._Password, {})
            if not uid:
                return ["Error: Autenticacion fallida"]
            else: 
                return uid
        except Exception as e:
            return str(e)
