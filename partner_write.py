import xmlrpc.client
from endpoint import models
from establish import *
import sys

list_partners = models.execute_kw(
    db, uid, password,
    'res.partner', 'search',
    [[['id', '=', 16]]],
)

if len(list_partners) <= 0:
    sys.exit("No existe usuario con id dado")

"""
Para el write es necesesario enviar solo el numero de id como primer argumento 
[[12], {'field': "modificacion"}]
"""

for partner in list_partners:
    models.execute_kw(
        db, uid, password,
        'res.partner', 'write',
        [[partner], {'comment': "Commented via API, new try 1"}],
    )

partners = models.execute_kw(db, uid, password,
    'res.partner', 'read', [list_partners], {'fields': ['name', 'phone', 'comment']})

print(partners)