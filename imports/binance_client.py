"""
Tutorial:
    - https://algotrading101.com/learn/binance-python-api-guide/


Test out your Python trading script on the Binance API testnet:
    - https://testnet.binance.vision/
"""

# Librerías
import sys
import os
from datetime import datetime
import time
import dateparser
import pandas as pd
import pytz
import json
import asyncio
from binance.client import Client, AsyncClient
from binance import BinanceSocketManager, ThreadedWebsocketManager
import pytz


class BinanceClient:
    """

    """

    def __init__(self, symbol, interval):
        """
        Constructor de clase. Los parámetros que definen el objeto son:
            - e: "kline",				# event type
            - E: 1499404907056,			# event time
            - s: "ETHBTC",				# symbol
            - t: 1499404860000, 		# start time of this bar
            - T: 1499404919999, 		# end time of this bar
            - s: "ETHBTC",				# symbol
            - i: "1m",					# interval
            - f: 77462,					# first trade id
            - L: 77465,					# last trade id
            - o: "0.10278577",			# open
            - c: "0.10278645",			# close
            - h: "0.10278712",			# high
            - l: "0.10278518",			# low
            - v: "17.47929838",			# volume
            - n: 4,						# number of trades
            - x: false,					# whether this bar is final
            - q: "1.79662878",			# quote volume
            - V: "2.34879839",			# volume of active buy
            - Q: "0.24142166",			# quote volume of active buy
            - B: "13279784.01349473"	# can be ignored
        """
        self.symbol = symbol
        self.interval = interval
        self.historical_klines = list()
        self.number_of_candles = 0

        # Instanciar cliente asincrono de binance
        self.thread_web_scoket = ThreadedWebsocketManager(
            os.environ['BINANCE_API_KEY'],
            os.environ['BINANCE_API_SECRET_KEY']
        )

        # Lanzar lopp interior del hilo (requerido)
        self.thread_web_scoket.start()
        time.sleep(5)
        print('BinanceSocketThread waiting for running...')

    # Métodos públicos
    def run(self):
        """
        Lanzar hilos de API.
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.__get_historical_klines())

    def get_klines(self):
        """
        Devolver historical klines en formato dataframe
        """
        df_klines = pd.DataFrame(self.historical_klines)

        if df_klines.shape != (0,0):
            columns_ordered = [
                'start_time', 'end_time', 'symbol',
                'open', 'close', 'high', 'low',
                'volume', 'number_of_trades',
                'event_type', 'interval','event_type']

            df_klines['start_time'] = pd.to_datetime(df_klines['start_time'], format='%Y-%m-%d %H:%M:%S')
            df_klines['end_time'] = pd.to_datetime(df_klines['end_time'], format='%Y-%m-%d %H:%M:%S')

            return df_klines[columns_ordered].copy()

        else:
            return None

    def download_klines(self, start_str, end_str):
        """
        [
          [
            1499040000000,      // Open time
            "0.01634790",       // Open
            "0.80000000",       // High
            "0.01575800",       // Low
            "0.01577100",       // Close
            "148976.11427815",  // Volume
            1499644799999,      // Close time
            "2434.19055334",    // Quote asset volume
            308,                // Number of trades
            "1756.87402397",    // Taker buy base asset volume
            "28.46694368",      // Taker buy quote asset volume
            "17928899.62484339" // Ignore.
          ]
        ]
        """
        client = Client(
            os.environ['BINANCE_API_KEY'],
            os.environ['BINANCE_API_SECRET_KEY']
        )
        klines = client.get_historical_klines(symbol = self.symbol,
                                              interval = self.interval,
                                              start_str = start_str,
                                              end_str = end_str,
                                              limit=1000)
        df_klines = list()

        for kl in klines:
            kl_d = {
                "event_type": 'kline',           # event type
                "symbol": self.symbol,           # symbol
                "start_time": kl[0],             # start time of this bar
                "end_time": kl[6],               # end time of this bar
                "interval": self.interval,       # interval
                "open": float(kl[1]),            # open
                "close": float(kl[4]),           # close
                "high": float(kl[2]),            # high
                "low": float(kl[3]),             # low
                "volume": float(kl[5]),          # volume
                "number_of_trades": int(kl[8]),  # number of trades
            }

            # Formato fecha
            kl_d['start_time'] = datetime.fromtimestamp(kl_d['start_time'] / 1e3).strftime('%Y-%m-%d %H:%M:%S')
            kl_d['end_time'] = datetime.fromtimestamp(kl_d['end_time'] / 1e3).strftime('%Y-%m-%d %H:%M:%S')

            df_klines.append(kl_d)

        self.historical_klines = df_klines

    # Métodos privados
    def __decode_response(self, msg):
        """
        Decodificación del mensaje obtenido en la respuesta

        Args:
        ------
            msg [{}]

        Returns:
        ------
            data [{dict}] Diccionario decodificado
        """

        kline = {
            "event_type": msg['e'],  # event type
            "symbol": msg['s'],  # symbol
            "start_time": msg['k']['t'],  # start time of this bar
            "end_time": msg['k']['T'],  # end time of this bar
            "interval": msg['k']['i'],  # interval
            "open": float(msg['k']['o']),  # open
            "close": float(msg['k']['c']),  # close
            "high": float(msg['k']['h']),  # high
            "low": float(msg['k']['l']),  # low
            "volume": float(msg['k']['v']),  # volume
            "number_of_trades": int(msg['k']['n']),  # number of trades
        }

        # Formato fecha
        kline['start_time'] = datetime.fromtimestamp(kline['start_time'] / 1e3).strftime('%Y-%m-%d %H:%M:%S')
        kline['end_time'] = datetime.fromtimestamp(kline['end_time'] / 1e3).strftime('%Y-%m-%d %H:%M:%S')

        return kline

    def __process(self, msg):
        """

        :param msg:
        :return:
        """
        # print(f'[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Received data!')

        kline = self.__decode_response(msg)
        if self.number_of_candles == 0:
            self.historical_klines.append(kline)
            self.number_of_candles += 1

        else:
            if kline['start_time'] != self.historical_klines[-1]['start_time']:
                # Actualizar historico de datos recibidos
                self.historical_klines.append(kline)
                self.number_of_candles += 1

    async def __get_historical_klines(self):
        """
        Método asíncrono que se ejecuta para obtener los datos de velas (klines) utilizando la API de binance. La
        respuesta de la API contiene la siguiente información:
        - e: "kline",					# event type
        - E: 1499404907056,				# event time
        - s: "ETHBTC",					# symbol
        - k:
            - t: 1499404860000, 		# start time of this bar
            - T: 1499404919999, 		# end time of this bar
            - s: "ETHBTC",				# symbol
            - i: "1m",					# interval
            - f: 77462,					# first trade id
            - L: 77465,					# last trade id
            - o: "0.10278577",			# open
            - c: "0.10278645",			# close
            - h: "0.10278712",			# high
            - l: "0.10278518",			# low
            - v: "17.47929838",			# volume
            - n: 4,						# number of trades
            - x: false,					# whether this bar is final
            - q: "1.79662878",			# quote volume
            - V: "2.34879839",			# volume of active buy
            - Q: "0.24142166",			# quote volume of active buy
            - B: "13279784.01349473"	# can be ignored

        Args:
        -----
        symbol [{str}] -- Simbolo del exhange.
        interval [{str}: Intervalo de Binance Kline

        Returns:
            Actualización de los datos recogidos.
        """

        # Lanzar socket para obtener los datos de vela para todos los exchanges y la profundidad de mercado
        self.thread_web_scoket.start_kline_socket(callback=self.__process, symbol=self.symbol, interval=self.interval)
