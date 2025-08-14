import xmlrpc
import os
from dotenv import load_dotenv
from endpoint import common

load_dotenv()
# Authenticating Connection
uid = common.authenticate(
        os.getenv('ODOO_DB'), 
        os.getenv('ODOO_USERNAME'), 
        os.getenv('ODOO_PASSWORD'), 
        {}
    )