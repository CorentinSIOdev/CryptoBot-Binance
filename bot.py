import websocket, json, pprint

SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"

#Variable globale sous forme de list vide
closes = []

#Message de connection à binance.
def onOpen(ws):
    print('Ouverture de la connexion')

#Message de déconnexion à binance.
def onClose(ws):
    print('Fermeture de la connexion')

#Message de binance.
def onMessage(ws, message):
    #Obtention d'une référence pour effectué des fermetures globales
    global closes

    #Test d'obtention des données.
    print('Données reçu :')

    #Transformation des données reçu sous la forme json.
    json_message = json.loads(message)

    #Structuration des données.
    pprint.pprint(json_message)

    #Références aux valeurs communiquées par binance.
    candle = json_message['k']

    #Fermeture du chandelier lorsque la bougie x est sur la valeur true.
    is_candle_closed = candle['x']

    #Prix de cloture de la bougie.
    close = candle['c']

    #Si la bougie à été fermée
    if is_candle_closed:
        #Obtenir un message avec l'affichage de la somme sur laquelle la bougie à clôturé.
        print('Bougie clôturé à {}'.format(close))
        #Point de clôturation le plus proche
        closes.append(close)
        #Affichages globales des fermetures
        print("clôturation")
        #Affichages des clôturations réelles
        print(closes)

ws = websocket.WebSocketApp(SOCKET, on_open=onOpen, on_close=onClose, on_message=onMessage)
ws.run_forever()