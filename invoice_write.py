import xmlrpc.client
from endpoint import models
from establish import *

# aux = models.execute_kw(db, uid, password, 'account.account', 'search_read', [[]], {'fields': ['id', 'name', 'code']})
# for a in aux:
#     print(a)    

# Crear una factura
new_invoice = models.execute_kw(db, uid, password, 'account.move', 'create', [{
    'partner_id': 1,        # Dependera si es proveedor o cliente
    'ref': '22222',
    #'auto_post': True,
    'currency_id': 19,      # 19 es ARS
    'date': '2025-07-28',
    'journal_id': 18,           # 18 es para Compras (18) o Ventas (17)
    'move_type': 'in_invoice',  #in_invoice o out_invoice
    'state': 'draft',           #No se permite crear directamente en posted
    'name': 'Factura 2',
    'display_name': 'Factura 22222',    #Repetir nombre de la factura
    'invoice_date_due': '2025-08-28',
    'invoice_date': '2025-07-28',       #Repetir date
    'l10n_latam_document_type_id': 6,   #1 es Factura A, 6 es Factura B
    'l10n_latam_document_number': '0002-22222',     #0001 para Factura A, 0002 para Factura B. Repetir número de la factura
    'invoice_line_ids': [
        (0, 0, {
            'name': 'Linea 1',
            'quantity': 1,
            'price_unit': 1111,
            'account_id': 1891,
            'currency_id': 19,
            'move_type': 'in_invoice',
            'tax_ids': [81] #81 es IVA No Corresp
        })
    ]
}])

print(new_invoice)

#invoice_confirmed = models.execute_kw(db, uid, password, 'account.move', 'write', [[new_invoice], {'state': 'posted'}])