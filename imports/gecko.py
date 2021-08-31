"""

"""
__version__ = '0.0.1'

# Librerías
import requests
import json
from datetime import datetime
import pandas as pd
import pytz
import ntplib

class CoinGeckoClient():

    def __init__(self):
        """
        Constructor
        """
        self.local_timezone = pytz.timezone('Europe/Madrid')
        self.ntp_servers = ['0.uk.pool.ntp.org', '1.uk.pool.ntp.org', '2.uk.pool.ntp.org', '3.uk.pool.ntp.org']
        self.list_requests = list()
        self.ping()

    def requestTimeFromNtp(self):
        """
        Conexión a un servidor NTP para obtener la hora independientemente de la máquina de ejecución de
        la aplicación
        """
        response = None

        client = ntplib.NTPClient()

        for i, ntp_serv in enumerate(self.ntp_servers):
            try:
                response = client.request(ntp_serv)
            except Exception as e:
                continue
            else:
                print(f'Conexión establecida con el servidor {self.ntp_servers[i]}')
                break

        if response is not None:
            return datetime.fromtimestamp(response.tx_time, pytz.timezone(self.local_timezone))
        else:
            raise ('No se estableción conexión con ningún servidor NTP')

    def request_url(self, url, headers=None):
        """

        :param url:
        :param headers:
        :return:
        """
        requests_datetime  = self.requestTimeFromNtp() #datetime.now(self.local_timezone).strftime('%Y-%m-%d %H:%M:%S')
        try:
            if headers:
                response = requests.get(url, headers=headers)
            else:
                response = requests.get(url)
        except Exception as e:
            raise(e)
        else:
            return response

    def ping(self):
        """
        Check API server status
        :return:
        """
        url = 'https://api.coingecko.com/api/v3/ping'
        response = self.request_url(url)

    def get_tick(self, base_currency, traded_currency):
        """

        :param base_currency:
        :param traded_currency:
        :return:
        """
        url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true&include_last_updated_at=true'
        headers = {'accept': 'application/json'}
        try:
            response = requests.get(url=url, headers=headers)
        except Exception as e:
            print(e)
        else:
            data = response.json()

            # Formatear salida
            data['bitcoin']['last_updated_at'] = datetime.fromtimestamp(data['bitcoin']['last_updated_at']).strftime('%Y-%m-%d %H:%M:%S')
            data_series = pd.Series({'symbol'})
            print(data)