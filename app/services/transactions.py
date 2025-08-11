from typing import Dict, Any
from app.models.endpoint import *
from app.services.fatherService import FatherService
from app.services.partners import PartnerService
from app.services.invoices import InvoiceService

class TransactionService(FatherService):
    def __init__(self):
        super().__init__()

    def getAllTransactions(self):
        try:
            uid = super().authenticate()
            
            if(type(uid) != int and "Autenticacion" in uid):
                return "Error: Autenticacion fallida, solicitar acceso"
            
            # Ahora usar el uid para ejecutar la consulta
            listTransactios = models.execute_kw(
                self._Db, uid, self._Password,
                'account.payment', 'search_read',
                [[]],
                {'fields': ['id', 'name', 'amount', 'partner_id', 'reconciled_invoice_ids']}
            )

            return listTransactios
        except Exception as e:
            return f"Error: {str(e)}" 

    def createTransaction(self, body: Dict[str, Any]):
        try:
            uid = super().authenticate()

            if(type(uid) != int and "Autenticacion" in uid):
                return "Error: fallo de autenticacion, solicite acceso"

            partnerService = PartnerService()
            partner = partnerService.getPartnerByName(body.get('nombre'))
            if(type(partner) is list):
                return "Error: Partner de la transaccion no encontrado"

            invoiceService = InvoiceService()
            invoice = invoiceService.getInvoiceByRef(body.get('nfactura'))
            if(invoice is str and "Error" in invoice):
                return "Error: Factura de la transaccion no encontrada"
            elif (len(invoice) == 0):
                return "Error: Factura de la transaccion no encontrada"

            invoicesIds = [item.get('id') for item in invoice]

            # payment_methods = models.execute_kw(
            #         self._Db, uid, self._Password,
            #         'account.payment.method.line', 'search_read',
            #         [[]],
            #         {'fields': ['id', 'name', 'code', 'payment_method_id']}
            #     )
            # print(payment_methods)
            transactionCreated = models.execute_kw(
                    self._Db, uid, self._Password,
                    'account.payment', 'create',
                    [{
                        "payment_type": "inbound",
                        "company_id": 1,
                        "currency_id": 19,
                        "state": "draft",
                        "partner_type": "customer" if partner.get('company_type') == "person" else "supplier",
                        "name": f"Pago factura {body.get('nfactura')}",
                        "partner_id": partner.get('id'),
                        "date": body.get('fecha_pago'),
                        "amount": body.get('cobrado'),
                        "reconciled_invoice_ids": [(6, 0, invoicesIds)],
                        # "journal_id": 17,
                        # "payment_method_line_id": 14
                        #Como lo asocio con una factura uwu
                    }]
                )
            self.__paymentRegister(body, uid, invoicesIds)

            invoiceUpdate = invoiceService.payInvoice(body.get('nfactura'), transactionCreated)
            return transactionCreated
        except Exception as e:
            return f"Error: {str(e)}"

    def __paymentRegister(self, body: Dict[str, Any], uid: int, invoicesIds: list):
        try:
            # Paso 1: Crear el wizard con las facturas como contexto
            wizard_vals = {
                'payment_date': body.get('fecha_pago'),
                'amount': float(body.get('cobrado')),
                'communication': f"Pago factura {body.get('nfactura')}",
                'partner_type': 'customer',
                'payment_type': 'inbound',
            }
            
            # Crear el wizard con el contexto de las facturas
            wizard_id = models.execute_kw(
                self._Db, uid, self._Password,
                'account.payment.register', 'create',
                [wizard_vals],
                {
                    'context': {
                        'active_model': 'account.move',
                        'active_ids': invoicesIds,
                        'active_id': invoicesIds[0],
                    }
                }
            )
            
            # Paso 2: Ejecutar el wizard para crear el pago
            payment_result = models.execute_kw(
                self._Db, uid, self._Password,
                'account.payment.register', 'action_create_payments',
                [wizard_id]
            )
            print("Pago creado exitosamente:", payment_result)
        
        except Exception as e:
            print("Error al crear pago:", e)