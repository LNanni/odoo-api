import xmlrpc.client
from endpoint import models
from establish import *

document_types = models.execute_kw(db, uid, password, 'l10n_latam.document.type', 'search_read', [[]], {'fields': ['id', 'name', 'code']})

for document_type in document_types:
    print(document_type)