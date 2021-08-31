
class BinanceClient():
    """
    Cliente de Binance que permite comunicarse con la plataforma de exchange.

   Limites de la API de Binance:
    - 1200 solicitudes por minuto
    - 10 órdenes por segundo
    - 100000 órdenes por 24hrs
    """
    def __init__(self, flag_live=True):
        """
        Constructor del cliente de Binance. Estable la conexión con la API.

        Args:
            flag_live: Bandera para establecer el cliente con la API oficial (True) o con la demo de testnet(False)
        """

        # Binance client
        try:
            # Initialize client
            if flag_live:
                client = Client(api_key=os.environ['BINANCE_API_KEY'], api_secret=os.environ['BINANCE_API_SECRET_KEY'])
            else:
                client = Client(api_key=os.environ['TESTNET_BINANCE_API_KEY'],
                                api_secret=os.environ['TESTNET_BINANCE_SECRET_KEY'])

                # Demo environment TestNet
                client.API_URL = 'https://testnet.binance.vision/api'

        except Exception as e:
            print(e, file=sys.stderr)
        else:
            print('Connection successfull!')
            self.client = client
            self.available_intervals = ['12h', '15m', '1d', '1h', '1m', '1M', '1w', '2h', '30m', '3d', '3m', '4h',
                                        '5m' ,'6h', '8h']

    def get_account(self):
        """
        Print all of account details for every currency available on the platform. It will also provide some other info such as the
        current commission rate and if account is enabled for margin trading
        :return: None
        """
        print( 5 *'-')
        print(f'Binance account details:\n{self.client.get_account()}')

    def get_exchange_info(self):
        """
        Get exchange info
        :return:
        """
        print( 5 *'-')
        print('Getting exchange info...')
        info = self.client.get_exchange_info()

        # Server Time UTC
        server_time_utc = datetime.utcfromtimestamp(info['serverTime' ] /1e3)
        server_time_local = datetime.fromtimestamp(info['serverTime' ] /1e3)
        print(f'Server Time (UTC): {server_time_utc}.\nServer Time (Local): {server_time_local}')

        # Symbols
        print('List exchanges')
        symbol s =list() # Lista de simbolos
        for num, crypto_asset in enumerate(info['symbols']):
            symbols.append(crypto_asset["symbol"])
            print \
                (f'{num}. Symbol: {crypto_asset["symbol"]}. Base: {crypto_asset["baseAsset"]}. Quote: {crypto_asset["quoteAsset"]}')

        # Guardar en la clase
        self.available_symbols = symbols

    def get_all_coins_info(self):
        """
        Get information of coins (available for deposit and withdraw) for user
        :return: Symbol list
        """
        print( 5 *'-')
        print('Getting list crypto currency')

        # Solicitud a la API
        info = self.client.get_all_tickers()
        symbol_list = list()

        # Almacenar respuesta
        for i, coin_info in enumerate(info):
            symbol_list.append(coin_info['symbol'])

        return symbol_list

    def get_candlesticks(self, symbol, interval):
        """
        Obtener en formato DataFrame las velas descargadas

        Args:
            symbol: Simbolo del activo
            interval: Intervalo de vela.
        """
        if (interval in self.available_intervals) and (symbol in self.available_symbols):
            candles = self.client.get_historical_klines(symbol=symbol,
                                                        interval=interval,
                                                        start_str='1 Jan, 2018',
                                                        limit=1000)

            # Guardar información como dataframe
            api_cols = ['OpenTime', 'Open', 'High', 'Low', 'Close', 'Volume', 'CloseTime', 'QuoteAssetVolume',
                        'NumberTrades', 'TakerBuyBaseAssetVolume', 'TakerBuyQuoteAssetVolume', 'Ignore']
            df_candlestick = pd.DataFrame(candles, columns=api_cols)

            # Formateo del df.
            # Formato Fecha
            columns_date = ['OpenTime', 'CloseTime']
            for col in columns_date:
                df_candlestick[col] = df_candlestick[col].astype(float)
                df_candlestick[col] = df_candlestick[col] * 1000000  # <<<<<<<<<<<this one
                df_candlestick[col] = pd.to_datetime(df_candlestick[col])

            # Formato numericos
            columns_float = ['Open', 'High', 'Low', 'Close', 'Volume', 'QuoteAssetVolume', 'NumberTrades',
                             'TakerBuyBaseAssetVolume', 'TakerBuyQuoteAssetVolume']
            df_candlestick[columns_float].apply(pd.to_numeric)

            # Orden de las columnas
            df_candlestick['Symbol'] = symbol
            columns = ['Symbol', 'OpenTime', 'CloseTime', 'Open', 'High' ,'Low', 'Close', 'Volume', 'QuoteAssetVolume', 'NumberTrades',
                       'TakerBuyBaseAssetVolume', 'TakerBuyQuoteAssetVolume']
            df_candlestick = df_candlestick[columns]

        else:
            print('Interval not found!', file=sys.stderr)

        return df_candlestick

    def download_crypto(self, symbol_list, interval):
        """
        Descarga la información de mercado (OHLV) de una lista de activos en un determinado período de vela.

        Args:
            symbol: Lista de cryptos a descargar.
            interval: Intervalo de vela.

        Returns:
            data: Diccionario de dataframes con los datos de vela (OHLC)
        """

        data = dict()
        for i, symbol in enumerate(symbol_list):
            print(f'{i} - Downloading {symbol} market data. Please wait...')
            # Obtener datos
            df_data = self.get_candlesticks(symbol=symbol, interval=interval)

            # Guardar datos
            filename = self.base_dir + f'{symbol}_{interval}.csv'
            df_data.to_csv(filename, sep=';', index=False, encoding='utf-8-sig')
            data[symbol] = df_data.copy()

            del df_data, i, symbol

        return data


