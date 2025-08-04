import xmlrpc.client
from flask import jsonify
from app.models.endpoint import *
from app.services.fatherService import FatherService
from app.services.partners import PartnerService
#from app.clients.mikrowisp import MikrowispClient
from dotenv import load_dotenv

load_dotenv()

class InvoiceService(FatherService):
    def __init__(self):
        super().__init__()

    def getAllInvoices(self):
        try:
            uid = super().authenticate()
            
            if(type(uid) != int and "Autenticacion" in uid):
                return ["Error: Autenticacion fallida"]

            list_invoices = models.execute_kw(
                self._Db, uid, self._Password,
                'account.move', 'search_read',
                [[]],  # sin filtros
                {'fields': ['name', 'date', 'state', 'amount_total']}
            )
            return list_invoices
        except Exception as e:
            return ["Error: " + str(e)]
    
    def createInvoices(self):
        try:
            uid = super().authenticate()

            if (type(uid) != int and "Autenticacion" in uid):
                return ["Error: Autenticacion fallida"]

            invoiceList = []#MikrowispClient.getAllInvoices()

            for invoice in invoiceList:
                partnerService = PartnerService()
                partnerId = partnerService.getPartnerByName(invoice.nombre)

                if(type(partnerId) is str):
                    print("Partner not found: ", invoice.nombre)
                    continue

                linesIds = []
                for item in invoice:
                    linesIds.append(jsonify({
                        'name': item.descripcion,
                        'quantity': item.unidades,
                        'price_unit': item.cantidad,
                        'account_id': 1891,
                        'currency_id': 19,
                        'move_type': 'in_invoice',
                        'tax_ids': [81] #81 es IVA No Corresp
                    }))

                try:
                    create_invoice = models.execute_kw(
                        self._Db, uid, self._Password,
                        'account.move', 'create',
                        [{
                            'partner_id': 1,        # Dependera si es proveedor o cliente
                            'ref': invoice.nfactura,
                            'currency_id': 19,      # 19 es ARS
                            'date': invoice.emitido,
                            'journal_id': 18,           # 18 es para Compras (18) o Ventas (17)
                            'move_type': 'in_invoice',  #in_invoice o out_invoice
                            'state': 'draft',           #No se permite crear directamente en posted
                            'name': invoice.nombre,
                            'display_name': invoice.nombre,    #Repetir nombre de la factura
                            'invoice_date_due': invoice.vencimiento,
                            'invoice_date': invoice.emitido,       #Repetir date
                            'l10n_latam_document_type_id': 6 if invoice.tipo == "Servicios" else 1,   #1 es Factura A, 6 es Factura B
                            'l10n_latam_document_number': str.join('0001-',) if invoiceList.invoiceType == "A" else '0002-',     #0001 para Factura A, 0002 para Factura B. Repetir número de la factura
                            'sequence_number': 3232,
                            'invoice_line_ids': [
                                (0, 0, linesIds)
                            ]
                        }]
                    )
                except Exception as e:
                    print(str(e))
        except Exception as e:
            return ["Error: " + str(e)]