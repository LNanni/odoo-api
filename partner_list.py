import xmlrpc.client
from endpoint import models
from establish import *

#list_partners = models.execute_kw(db, uid, password, 'res.partner', 'search', [[
#    ['is_company', '=', True], #Input False for person
#    ['customer', '=', True], #Input False for Vendor
#]])

list_partners = models.execute_kw(
    db, uid, password,
    'res.partner', 'search',
    [[  ['comment', 'ilike', 'try']#,
        #['name', 'ilike', 'Iñaki']
    ]],  # sin filtros
)

partners = models.execute_kw(db, uid, password,
    'res.partner', 'read', [list_partners], {'fields': ['name', 'phone', 'comment']})

for partner in partners:
    print(partner)
