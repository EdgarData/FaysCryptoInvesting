# Librerías
import os
import sys
import pandas as pd
from datetime import datetime
import pytz

# Paquetes
from CryptoInvesting.binance import BinanceClient

# Parámetros de entrada
script_start = datetime.now(pytz.timezone('Europe/Madrid')).strftime('%Y-%m-%d %H:%M:%S')

def download_data(base_dir, symbols=None, interval='1h'):
    """
    Descargar los datos de mercado.
    :param base_dir: Directorio de almacenamiento
    :param interval: Período de vela
    :return: None
    """
    binance_client = BinanceClient(base_dir, flag_live=True)
    #binance_client.get_account()
    binance_client.get_exchange_info()
    symbol_list = sorted(binance_client.get_all_coins_info())

    if not symbols:
        # Descargar todos los datos de los activos seleccionados
        market_data = binance_client.download_crypto(symbol_list, interval=interval)
    else:
        assert not(False in [crypto in symbol_list for crypto in symbols])
        market_data = binance_client.download_crypto(symbols, interval=interval)
    return None

def generar_dataset(base_dir, interval='1h'):
    """
    Generar dataset y almacenarlo en fichero csv
    :param base_dir: Directorio base de almacenamiento de los datos descargados
    :param interval: Período de vela
    :return:
    """
    # Leer los csv almacenados en el direcotrio
    files = os.listdir(base_dir)
    data = list()
    for file in files:
        # Directorio de almacenamiento
        filename = base_dir + file

        # Medir progreso de lectura
        progreso = len(data) / len(files) * 100
        print('Read "{}"\t-\tProgress: {:3,.2f} %'.format(filename, progreso))

        # Lectura del csv
        df = pd.read_csv(filename, sep=';', encoding='utf-8-sig')
        data.append(df.copy())

        # Liberar memoria
        del df, filename

    # Comprobación de seguridad (Se ha realizado la lectura de todos los ficheros).
    assert len(data) == len(files)
    print('Read completed!')

    result = pd.concat(data, axis=0)
    result.to_csv('data/binance_data.csv', sep=';', encoding='utf-8-sig', index=False)
    print()
    print('Dataset generado correctamente!')# Parámetros de entrada

if __name__ == '__main__':

    # Parámetros de entrada
    interval = '1h'
    base_dir = f'data/binance/{script_start}/'

    # Crear directorio dentro de la carpeta data de almacenamiento
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    # Descargar datos
    #symbols = ['BTCUSDT', 'ETHUSDT', 'BTCBUSD', 'ADAUSDT', 'DOGEUSDT']
    #download_data(base_dir, interval=interval, symbols=symbols)
    download_data(base_dir, interval=interval)

    # Generar dataset
    # generar_dataset(base_dir, interval)
