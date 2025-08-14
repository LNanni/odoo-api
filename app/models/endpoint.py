import xmlrpc.client
import os
from dotenv import load_dotenv

load_dotenv()

common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(os.getenv('ODOO_URL')))
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(os.getenv('ODOO_URL')))

# common is an endpoint needed to perform login
# models is an endpoint to call methods of odoo models via execute_kw RPC Function