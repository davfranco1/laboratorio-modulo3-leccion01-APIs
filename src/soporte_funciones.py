#Imports
from tqdm import tqdm
import requests
from time import sleep
from geopy.geocoders import Nominatim


def obtener_coordenadas(municipios):
    
    """
    Obtiene las coordenadas geográficas (latitud y longitud) de una lista de municipios.

    Parámetros:
    - municipios (list): Lista de nombres de municipios.

    Retorna:
    - dicc_coordenadas (dict): Diccionario con los nombres de los municipios como claves y sus respectivas coordenadas (latitud y longitud) como valores.
    """

    geolocator = Nominatim(user_agent="my_app")
    dicc_coordenadas = {}
    
    for municipio in tqdm(municipios):
        location = geolocator.geocode(municipio)
        dicc_coordenadas[municipio] = ((location.latitude, location.longitude))
        sleep(1)

    return dicc_coordenadas


def busca_establecimientos(latitud, longitud, id_categoria, radio, categorias, api_key):

    """
    Busca establecimientos dentro de un radio especificado alrededor de una ubicación geográfica.

    Parámetros:
    - latitud (float): Latitud de la ubicación central.
    - longitud (float): Longitud de la ubicación central.
    - id_categoria (str): ID de la categoría a buscar.
    - radio (int): Radio de búsqueda en metros.
    - categorias (list): Lista de campos a incluir en los resultados.
    - api_key (str): Clave API para acceder al servicio de Foursquare.

    Retorna:
    - dict: Respuesta JSON de la API de Foursquare con los resultados de la búsqueda.
    """

    url = "https://api.foursquare.com/v3/places/search"

    params = {
        "ll": ""+str(latitud)+","+str(longitud),
        "categories": id_categoria,
        "radius": radio,
        "sort":"DISTANCE",
        "fields": categorias
    }

    headers = {
        "Accept": "application/json",
        "Authorization": api_key
    }

    response = requests.request("GET", url, params = params, headers = headers)
    return response.json()



def establecimientos_por_municipio(df, dicc_id_cat, radio, categorias, api_key):

    """
    Busca establecimientos dentro de un radio especificado para los municipios y categorías dados.

    Parámetros:
    - df (DataFrame): DataFrame que contiene nombres de municipios, latitudes y longitudes.
    - dicc_id_cat (dict): Diccionario que mapea IDs de categorías a nombres de categorías.
    - radio (float): Radio de búsqueda en metros.
    - categorias (list): Lista de categorías en las cuales buscar.
    - api_key (str): Clave API para acceder al servicio de búsqueda de establecimientos.

    Retorna:
    - lista_df_municipios (list): Lista de diccionarios que contienen detalles de establecimientos y sus ubicaciones.
    """

    lista_id_categorias = list(dicc_id_cat.keys()) #creo lista con ids de categorías
    lista_df_municipios = [] #lista para almacenar resultados

    for i in tqdm(range(df.shape[0])): #itero sobre el primer df (municipio, lat, long)
        municipio = df.iloc[i, 0] #extraigo municipio, latitud y longitud del primer df
        latitud = float(df.iloc[i, 1])
        longitud = float(df.iloc[i, 2])

        for id_categoria in lista_id_categorias: #segunda iteración para cada categoría (5 en total)
            lista_dics = busca_establecimientos(latitud, longitud, id_categoria, radio, categorias, api_key)["results"]
            for dicc in lista_dics: #tercera iteración sobre los establecimientos
                dicc_final = {
                    "Municipio": municipio, #municipio, lat y long traídos del primer df
                    "Latitud": latitud,
                    "Longitud": longitud,
                    "Nombre": dicc["name"], #extraigo nombre, cat, distancia y dirección
                    "Categoria": dicc_id_cat[id_categoria],
                    "Distancia": dicc["distance"],
                    "Dirección": dicc["location"]["formatted_address"]
                }
                lista_df_municipios.append(dicc_final)

    return lista_df_municipios #devuelvo lista dicc
