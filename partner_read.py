import xmlrpc.client
from endpoint import models
from establish import *

"""
Importante filtrar los campos, sino falla por falta de permisos (Aun siendo admin)
"""

[partner] = models.execute_kw(db, uid, password, 
    'res.partner', 'read', [[16]], {'fields': ['id', 'name', 'email', 'phone', 'vat']})


print(partner)