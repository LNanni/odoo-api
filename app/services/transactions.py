import stat
from typing import Dict, Any
from uu import Error
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

            """transactionCreated = models.execute_kw(
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
                        #Como lo asocio con una factura uwu
                    }]
                )
            invoiceUpdate = invoiceService.payInvoice(body.get('nfactura'), transactionCreated)
            """
            result = self.__paymentRegister(body, uid, invoicesIds, partner)
            if type(result) != int:
                raise ValueError(result)

            return 1
        except Exception as e:
            return f"Error: {str(e)}"

    def __paymentRegister(self, body: Dict[str, Any], uid: int, invoicesIds: list, partner: Dict[str, Any]):
        try:
            # Paso 1: Crear el wizard con las facturas como contexto
            wizard_vals = {
                'payment_date': body.get('fecha_pago'),
                'amount': float(body.get('cobrado')),
                'communication': f"Pago factura {body.get('nfactura')}",
                'partner_type': "customer" if partner.get('company_type') == "person" else "supplier",
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
            
            # Paso 3: Crear línea de extracto bancario
            statement_line_id = None
            if payment_result and 'res_id' in payment_result:
                payment_id = payment_result['res_id']
                statementLineId = self.__createBankStatementLine(body, uid, payment_id, invoicesIds, partner)
                if type(statementLineId) != int:
                    raise ValueError(statementLineId)
            
            # Paso 4: Conciliar automáticamente
            if statement_line_id:
                reconciliation_result = self.__reconcileTransactions(uid, statementLineId, invoicesIds)
                if type(reconciliation_result) != int:
                    print(f"Advertencia: {reconciliation_result}")
                else:
                    print("Transacciones conciliadas automáticamente")
            
            print("Pago creado exitosamente:", payment_result)
        
        except Exception as e:
            return f"Error al crear pago: {e}"

    def __createBankStatementLine(self, body: Dict[str, Any], uid: int, payment_id: int, invoicesIds: list, partner: Dict[str, Any]):
        try:
            # Obtener o crear extracto bancario
            statement_id = self.__getOrCreateBankStatement(uid, body.get('fecha_pago'))
            if(statement_id == -1):
                raise ValueError("Error al obtener o crear extracto bancario")
            
            # Datos para la línea de extracto bancario
            statement_line_data = {
                "statement_id": statement_id,  # ID del extracto bancario
                "date": body.get('fecha_pago'),
                "amount": float(body.get('cobrado')),
                "payment_ref": f"Pago factura {body.get('nfactura')}",
                "partner_id": partner.get('id') if isinstance(partner, dict) else None,
                "name": f"Pago factura {body.get('nfactura')} - {body.get('nombre')}",
                "ref": body.get('nfactura'),  # Referencia de la factura
                "journal_id": 29,  # Diario bancario
                "currency_id": body.get('currency_id', 19),  # Moneda (ARS)
                "sequence": body.get('sequence', 1),  # Orden en el extracto
                "account_number": body.get('account_number', 12),  # Número de cuenta (opcional)
                "transaction_type": "customer",  # Tipo de transacción
            }
            
            # Crear línea de extracto bancario
            statement_line_id = models.execute_kw(
                self._Db, uid, self._Password,
                'account.bank.statement.line', 'create',
                [statement_line_data]
            )
            
            print(f"Línea de extracto bancario creada: {statement_line_id}")
            return statement_line_id
            
        except Exception as e:
            return f"Error al crear línea de extracto bancario: {str(e)}"            

    def __getOrCreateBankStatement(self, uid: int, date: str) -> int:
        try:
            # Buscar extracto bancario existente para la fecha
            existing_statements = models.execute_kw(
                self._Db, uid, self._Password,
                'account.bank.statement', 'search_read',
                [[
                    ['date', '=', date],
                    ['journal_id', '=', 29]  # Mismo journal_id que usas
                ]],
                {'fields': ['id', 'name', 'date']}
            )
            
            if existing_statements:
                # Usar el extracto existente
                return existing_statements[0]['id']
            else:
                # Crear nuevo extracto bancario
                statement_data = {
                    "name": f"Extracto bancario {date}",
                    "date": date,
                    "journal_id": 29,  # Diario bancario
                    "balance_start": 0.0,
                    "balance_end_real": 0.0
                }
                
                statement_id = models.execute_kw(
                    self._Db, uid, self._Password,
                    'account.bank.statement', 'create',
                    [statement_data]
                )
                
                print(f"Nuevo extracto bancario creado: {statement_id}")
                return statement_id
                
        except Exception as e:
            print(f"Error al obtener/crear extracto bancario: {str(e)}")
            # Fallback: usar extracto por defecto
            return -1

    def __reconcileTransactions(self, uid: int, statement_line_id: int, invoicesIds: list) -> str:
        """
        Conciliar automáticamente las transacciones usando el método estándar de Odoo
        """
        try:
            # Obtener la línea de extracto bancario
            statement_line = models.execute_kw(
                self._Db, uid, self._Password,
                'account.bank.statement.line', 'read',
                [[statement_line_id]],
                {'fields': ['id', 'amount', 'partner_id', 'payment_ref', 'statement_id']}
            )
            
            if not statement_line:
                return "Error: No se encontró la línea de extracto bancario"
            
            line_data = statement_line[0]
            
            # Buscar líneas de factura para conciliar
            invoice_lines = models.execute_kw(
                self._Db, uid, self._Password,
                'account.move.line', 'search_read',
                [[
                    ['move_id', 'in', invoicesIds],
                    ['account_id.reconcile', '=', True],
                    ['reconciled', '=', False]
                ]],
                {'fields': ['id', 'debit', 'credit', 'amount_residual', 'account_id', 'move_id']}
            )
            
            if not invoice_lines:
                return "Error: No se encontraron líneas de factura para conciliar"
            
            # Actualizar la línea de extracto bancario con la información de conciliación
            update_data = {
                'partner_id': line_data['partner_id'],
                'payment_ref': line_data['payment_ref'],
                'amount': line_data['amount'],
                'move_id': "",
            }
            
            # Si hay líneas de factura, asociar la primera
            if invoice_lines:
                update_data['move_id'] = invoice_lines[0]['id']
            
            # Actualizar la línea de extracto bancario
            models.execute_kw(
                self._Db, uid, self._Password,
                'account.bank.statement.line', 'write',
                [[statement_line_id], update_data]
            )
            
            # Marcar las facturas como pagadas
            for invoice_id in invoicesIds:
                models.execute_kw(
                    self._Db, uid, self._Password,
                    'account.move', 'write',
                    [[invoice_id], {'payment_state': 'paid'}]
                )
            
            print(f"Conciliación completada para línea {statement_line_id}")
            return "Conciliación exitosa"
            
        except Exception as e:
            return f"Error en conciliación automática: {str(e)}"