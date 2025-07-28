import xmlrpc.client
from endpoint import models
from establish import *

invoices = models.execute_kw(db, uid, password, 'account.move', 'search', [[]])

invoices_data = models.execute_kw(db, uid, password, 'account.move', 'read', [invoices], 
    {'fields': ['name', 'date', 'state', 'amount_untaxed', 'amount_total', 'partner_id', 'invoice_line_ids', 'ref', 'move_type']})


#invoices_lines = models.execute_kw(db, uid, password, 'account.move.line', 'search', [invoices_data[0]['invoice_line_ids']], {})

for invoice in invoices_data:
    print(invoice)
