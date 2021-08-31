import time

print(5*'-' + ' Candle App WebScoket Started! '+5*'-')

# Librerías
print('Importing libs...')
import sys
from datetime import datetime

# Añadir paquetes de Fays Crypto Investing
print('Importing pkgs...')
sys.path.append('imports')
from imports.binance_client import BinanceClient


if __name__ == '__main__':
    """
    """
    interval_seconds = 5 # Tiempo de actualización en segundos.
    start_str = '2021-08-30 00:00:00' # Hora inicio del período
    end_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Hora final del período

    # Binance Socket Thread
    bc = BinanceClient(symbol='BNBBTC', interval='5m')

    # Descargar data histórica.
    bc.download_klines(start_str=start_str, end_str=end_str)

    bc.run()

    prev_kline = ''
    while True:
        df_klines = bc.get_klines()

        if df_klines is not None:
            last_kline = df_klines.iloc[-1]
            if prev_kline != last_kline['start_time'].strftime('%Y-%m-%d %H:%M:%S'):
                dt_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f'[{dt_str}] Received {last_kline["start_time"]} kline data!')
                prev_kline = last_kline['start_time'].strftime('%Y-%m-%d %H:%M:%S')
                #time.sleep(interval_seconds)

        time.sleep(interval_seconds)

    print(5 * '-' + ' Candle App WebScoket Finished! ' + 5 * '-')


