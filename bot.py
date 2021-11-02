import websocket, json, pprint, talib, numpy
import config
from binance.client import Client
from binance.enums import *

#Type de flux Binance (ws/<symbol>@kline_<interval>).
#Documentation en ligne : https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-streams.md
#Catégorie : Kline/Candlestick Streams
SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"
#La période RSI est égal à 14
RSI_PERIOD = 14
#Un RSI suracheté est égal à 70
RSI_OVERBOUGHT = 70
#Un RSI survendu est égal à 30
RSI_OVERSOLD = 30
#Symbole commercial
TRADE_SYMBOL = 'ETHUSDT'
#Montant minimal à déposer (50$ = ~ 0.013 ETH)
TRADE_QUANTITY = 0.001

#Variable globale sous forme de list vide
closes = []

#Suivi de l'état
in_position = False

#Instanciation client API binance
client = Client(config.API_KEY, config.API_SECRET)

#Fonction de commande Achat/Vente Binance
def order(side, quantity, symbol, order_type = ORDER_TYPE_MARKET):
    try:
        print('Chargement de la commande...')
        #Récupération des données indiquées dans les positions de surachat / survente
        order = client.create_order(symbol = symbol, side = side, type = order_type, quantity = quantity)
        #Affichage des informations de la création de la commande
        print(order)
    except Exception as e:
        return False

    return True

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

    #Prix de fermeture de la bougie.
    close = candle['c']

    #Si la bougie à été fermée
    if is_candle_closed:
        #Obtenir un message avec l'affichage de la somme sur laquelle la bougie à fermé.
        print('Bougie fermé à {}'.format(close))
        #Point de fermetures la plus proche
        closes.append(float(close))
        #Affichages globaux des fermetures.
        print("Fermetures :")
        #Affichages des fermetures réelles.
        print(closes)

        #Si la longueur des fermetures est supérieur à 14
        if len(closes) > RSI_PERIOD:
            #np_closes est égal à un tableau numpy incluant les points de fermetures.
            np_closes = numpy.array(closes)
            #Calcul du RSI (RSI est égal à talib, appeler la fonction RSI lui donnant la valeur np_closes et la période par défaut)
            #Si nous modifions la période RSI à 10, la valeur s'exécutera ici et commencera à calculer les valeurs RSI.
            #Dès que nous obtiendrons 15 fermetures, nous obtiendrons une valeur RSI, à la 16 èmes fermetures, nous obtiendrons la deuxième valeur RSI, ainsi de suite...
            rsi = talib.RSI(np_closes, RSI_PERIOD)
            #Affichage des calculs RSI.
            print("Tous les RSI calculés jusqu'à présent")
            print(rsi)
            #Obtention du dernier RSI calculé et le définir égal à la dernière valeur de cette série.
            last_rsi = rsi[-1]
            print("Le RSI actuel est {}".format(last_rsi))

            #Si le dernier calcul RSI est supérieur à notre surachat
            if last_rsi > RSI_OVERBOUGHT:
                #Si nous sommes en position au moment du surachat
                if in_position:
                    #Affichage du message de vente.
                    print("Surachat ! Vente d'Ethereum (ETH) !")
                    #Logique de vente Binance.
                    order_succeeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                    #Si la commande de vente à réussi
                    if order_succeeded:
                        #En position false, la continuité de vente est suspendu.
                        in_position = False
                else:
                    print("Il est suracheté, mais nous n'en possédons pas. Rien à faire")

            #Si le dernier calcul RSI est inférieur à notre survente
            if last_rsi < RSI_OVERSOLD:
                #Si nous sommes en position au moment de la survente
                if in_position:
                    #Affichage du message de possession du RSI survendu.
                    print("Il est survendu, mais vous le possédez déjà, rien à faire.")
                else:
                    #Affichage du message d'achat.
                    print("Survendu ! Achat d'Ethereum (ETH) !")
                    #Logique d'achat Binance.
                    order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                    #Si la commande d'achat à reussi
                    if order_succeeded:
                        #En position true, la continuité d'achat est actif, nous possédons bien l'Ethereum
                        in_position = True

#Création d'un nouveau client websocket via un type de flux
ws = websocket.WebSocketApp(SOCKET, on_open=onOpen, on_close=onClose, on_message=onMessage)
#Exécution du websocket
ws.run_forever()