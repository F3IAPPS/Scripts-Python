from binance.client import Client
from secrets import api_key,api_secret

cliente = Client(api_key, api_secret)

status = cliente.get_account_status()
print(status)

#pegar informações da conta
info = cliente.get_account()
print(info)
