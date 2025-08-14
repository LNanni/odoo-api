import stat
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
            if type(result.get('res_id', '')) != int:
                raise ValueError(result)

            return result
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
            """if statementLineId:
                reconciliation_result = self.__reconcileTransactions(uid, statementLineId, invoicesIds, float(body.get('cobrado')))
                if type(reconciliation_result) != str or "Error" in reconciliation_result:
                    print(f"Advertencia: {reconciliation_result}")
                else:
                    print("Transacciones conciliadas automáticamente")"""
            
            print("Pago creado exitosamente:", payment_result)
            return payment_result
        
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
                "is_reconciled": True
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

    """def __reconcileTransactions(self, uid: int, statement_line_id: int, invoicesIds: list, payment_amount: float) -> str:
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
            
            # Obtener información de las facturas para calcular el monto total
            invoices_info = models.execute_kw(
                self._Db, uid, self._Password,
                'account.move', 'read',
                [invoicesIds],
                {'fields': ['id', 'amount_total', 'amount_residual', 'payment_state']}
            )
            
            if not invoices_info:
                return "Error: No se encontraron las facturas para conciliar"
            
            # Calcular el monto total de las facturas
            total_invoice_amount = sum(invoice.get('amount_residual', 0) for invoice in invoices_info)
            
            print(f"Monto pagado: {payment_amount}, Monto total facturas: {total_invoice_amount}")
            
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
            
            # Si el monto pagado es mayor al de las facturas, crear un crédito para el excedente
            if payment_amount > total_invoice_amount:
                excess_amount = payment_amount - total_invoice_amount
                print(f"Creando crédito por excedente: {excess_amount}")
                
                # Crear una línea de crédito para el excedente
                credit_line_id = self.__createCreditLine(uid, invoicesIds[0], excess_amount, partner_id=line_data.get('partner_id'))
                if credit_line_id:
                    print(f"Línea de crédito creada: {credit_line_id}")
            
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

    def __createCreditLine(self, uid: int, invoice_id: int, excess_amount: float, partner_id: int = None) -> int:
        #Crea una línea de crédito para el excedente del pago
        try:
            # Obtener información de la factura para usar la misma cuenta
            invoice_info = models.execute_kw(
                self._Db, uid, self._Password,
                'account.move', 'read',
                [[invoice_id]],
                {'fields': ['id', 'partner_id', 'journal_id', 'company_id']}
            )
            
            if not invoice_info:
                return None
            
            invoice_data = invoice_info[0]
            
            # Crear un asiento contable para el crédito
            credit_move_vals = {
                'ref': f'Crédito excedente pago factura {invoice_id}',
                'journal_id': invoice_data.get('journal_id'),
                'company_id': invoice_data.get('company_id'),
                'partner_id': partner_id or invoice_data.get('partner_id'),
                'date': models.fields.Date.today(),
                'move_type': 'entry',
                'line_ids': [
                    (0, 0, {
                        'account_id': 1,  # Cuenta de caja/bancos (ajustar según tu configuración)
                        'debit': excess_amount,
                        'credit': 0,
                        'name': f'Crédito excedente pago factura {invoice_id}',
                        'partner_id': partner_id or invoice_data.get('partner_id'),
                    }),
                    (0, 0, {
                        'account_id': 2,  # Cuenta de clientes (ajustar según tu configuración)
                        'debit': 0,
                        'credit': excess_amount,
                        'name': f'Crédito excedente pago factura {invoice_id}',
                        'partner_id': partner_id or invoice_data.get('partner_id'),
                    })
                ]
            }
            
            credit_move_id = models.execute_kw(
                self._Db, uid, self._Password,
                'account.move', 'create',
                [credit_move_vals]
            )
            
            # Publicar el asiento
            models.execute_kw(
                self._Db, uid, self._Password,
                'account.move', 'action_post',
                [[credit_move_id]]
            )
            
            return credit_move_id
            
        except Exception as e:
            print(f"Error al crear línea de crédito: {str(e)}")
            return None
        """