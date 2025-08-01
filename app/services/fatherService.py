from dotenv import load_dotenv
import os

load_dotenv()

class FatherService():
    def __init__(self):
        self._URL = os.getenv('ODOO_URL')
        self._Db = os.getenv('ODOO_DB')
        self._Username = os.getenv('ODOO_USERNAME')
        self._Password = os.getenv('ODOO_PASSWORD')