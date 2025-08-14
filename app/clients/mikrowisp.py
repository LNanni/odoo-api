from datetime import date
from dateutil.relativedelta import relativedelta
import requests
import json
from typing import Dict, Any, Optional
from requests.exceptions import RequestException
from dotenv import load_dotenv
import os

load_dotenv()

class MikrowispClient:
    def __init__(self):
        self.base_url = os.getenv('MIKROWISPHELPER_URL')
        self.api_key = os.getenv('MIKROWISPHELPER_TOKEN')
        self.session = requests.Session()
        
        # Configurar headers por defecto
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        # Agregar bearer token si existe
        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}'
            })

    def getInvoices(self, params: Dict[str, Any] = None):
        # Valores por defecto
        if params is None: params = {}
        
        if params.get('p') is None: params['p'] = 0
        if params.get('s') is None: params['s'] = 50
        if params.get('emitido_inicio') is None: params['emitido_inicio'] = date.today()
        if params.get('emitido_fin') is None: params['emitido_fin'] = date.today() + relativedelta(months=6)
        if params.get('vencimiento_inicio') is None: params['vencimiento_inicio'] = date.today()
        if params.get('vencimiento_fin') is None: params['vencimiento_fin'] = date.today() + relativedelta(months=6)
        if params.get('include_items') is None: params['include_items'] = True

        try:
            url = f"{self.base_url}invoices"
            response = self.session.get(url, params=params, timeout=5000)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            return {"error": str(e)}

