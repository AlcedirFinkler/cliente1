import requests
from django.conf import settings
from django.core.cache import cache
import logging

# Configure o logger
logger = logging.getLogger(__name__)

class WeconnService:
    def __init__(self):
        self.api_key = settings.WECONN_API_KEY
        self.base_url = settings.WECONN_BASE_URL
        self.tenant_slug = settings.WECONN_TENANT_SLUG
        self.headers = {
            "Authorization": f"Api-Key {self.api_key}"
        }
        # print(f"WeconnService inicializado com: URL={self.base_url}, SLUG={self.tenant_slug}")
    
    def get_tenant_info(self, use_cache=True):
        """
        Obtém informações do tenant a partir da API do Weconn.
        Utiliza cache para reduzir o número de chamadas à API.
        """
        cache_key = f"weconn_tenant_info_{self.tenant_slug}"
        
        # DEBUG: Vamos desabilitar temporariamente o cache para testes
        use_cache = False
        # print(f"Buscando informações do tenant: {self.tenant_slug}, use_cache={use_cache}")
        
        # Se não estiver em cache ou cache estiver desabilitado, faz a requisição
        try:
            url = f"{self.base_url}/api/tenant-info/?slug={self.tenant_slug}"
            # print(f"Fazendo requisição para: {url}")
            # print(f"Headers: {self.headers}")
            
            # Fazer a requisição manualmente para depurar
            import urllib.request
            import json
            
            # print("Tentando fazer a requisição usando urllib")
            req = urllib.request.Request(url)
            req.add_header("Authorization", f"Api-Key {self.api_key}")
            
            try:
                with urllib.request.urlopen(req, timeout=10) as response:
                    response_data = response.read().decode('utf-8')
                    # print(f"Resposta urllib: {response_data}")
                    data = json.loads(response_data)
                    # print(f"Dados processados: {data}")
                    cache.set(cache_key, data, 60 * 30)
                    return data
            except Exception as e:
                print(f"Erro urllib: {e}")
                
            # Tentar com requests como fallback
            # print("Tentando fallback com requests")
            response = requests.get(
                url,
                headers=self.headers,
                timeout=10
            )
            
            # print(f"Resposta da API (status): {response.status_code}")
            # print(f"Resposta da API (conteúdo): {response.text}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    # print(f"Dados obtidos da API: {data}")
                    cache.set(cache_key, data, 60 * 30)
                    return data
                except json.JSONDecodeError as e:
                    print(f"Erro ao decodificar JSON: {e}")
                    print(f"Texto da resposta: {response.text}")
            else:
                print(f"Erro na API: {response.text}")
                    
        except Exception as e:
            print(f"Erro não tratado: {type(e).__name__}: {str(e)}")
        
        # Configuração padrão em caso de falha total
        default_data = {
            'nome': self.tenant_slug,
            'access_status': 'active',  # Por padrão, permite acesso
            'plano': {
                'nome': 'Desconhecido',
                'nivel': 'nivel1',
            },
            'status_pagamento': 'em_dia',
        }
        # print(f"Usando dados padrão: {default_data}")
        return default_data
    
    def check_access_status(self):
        """
        Verifica o status de acesso do tenant.
        Retorna: 'active', 'grace_period', 'expired' ou 'blocked'
        """
        info = self.get_tenant_info()
        return info.get('access_status', 'active')
    
    def get_payment_status(self):
        """
        Obtém o status de pagamento do tenant.
        Retorna: 'em_dia', 'atraso' ou 'expirado'
        """
        info = self.get_tenant_info()
        return info.get('status_pagamento', 'em_dia')
    
    def get_plan_info(self):
        """
        Obtém informações do plano contratado.
        """
        info = self.get_tenant_info()
        return info.get('plano', {
            'nome': 'Desconhecido',
            'nivel': 'nivel1',
            'descricao': 'Plano básico'
        })