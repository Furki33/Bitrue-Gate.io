from __future__ import print_function
import gate_api
from bitrue.client import Client
from bitrue.enums import *
import requests
import time
import hashlib
import hmac

configuration = gate_api.Configuration(
    host="https://api.gateio.ws/api/v4",
    key="******",
    secret="*****")


def gen_sign(method, url, query_string=None, payload_string=None):
    key = '******'
    secret = '*****'

    t = time.time()
    m = hashlib.sha512()
    m.update((payload_string or "").encode('utf-8'))
    hashed_payload = m.hexdigest()
    s = '%s\n%s\n%s\n%s\n%s' % (method, url, query_string or "", hashed_payload, t)
    sign = hmac.new(secret.encode('utf-8'), s.encode('utf-8'), hashlib.sha512).hexdigest()
    return {'KEY': key, 'Timestamp': str(t), 'SIGN': sign}


while True:
    host = "https://api.gateio.ws"
    prefix = "/api/v4"
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    url1 = '/spot/order_book'
    query_param = 'currency_pair=CSPR_USDT'
    r = requests.request('GET', host + prefix + url1 + "?" + query_param, headers=headers)

    url2 = '/wallet/total_balance'
    query_param = ''
    sign_headers = gen_sign('GET', prefix + url2, query_param)
    headers.update(sign_headers)
    q1 = round(float(((requests.request('GET', host + prefix + url2, headers=headers)).json()['total'])['amount']), 5)
    g11 = float(r.json()['asks'][0][0])
    g12 = float(r.json()['asks'][1][0])
    g21 = float(r.json()['asks'][0][1])
    g22 = float(r.json()['asks'][1][1])
    gt2=(g21 + g22)
    gsa = round(float((g11*g21)+(g12*g22))/gt2, 5)
    g31 = float(r.json()['bids'][0][0])
    g32 = float(r.json()['bids'][1][0])
    g41 = float(r.json()['bids'][0][1])
    g42 = float(r.json()['bids'][1][1])
    gt4 = float(g41 + g42)
    gba = round(float((g31 * g41) + (g32 * g42)) / gt4, 5)
    api_instance = gate_api.WalletApi(gate_api.ApiClient(configuration))
    v3 = round(float(api_instance.get_total_balance(currency='USD').total.amount), 5)
    v8 = (q1-v3) / g11
    api_key = '******'
    api_secret = '*****'
    client = Client(api_key, api_secret)
    bms = round(float(float(client.get_order_book(symbol='CSPRUSDT', limit=1)['asks'][0][0])) - 0.00001, 5)
    bmb = round(float(float(client.get_order_book(symbol='CSPRUSDT', limit=1)['bids'][0][0])) + 0.00001, 5)
    fcb = int(float(client.get_asset_balance(asset='CSPR')['free']))
    lcb = int(float(client.get_asset_balance(asset='CSPR')['locked']))
    tsm = int(fcb + lcb + v8)
    fub = int(float(client.get_asset_balance(asset='USDT')['free']))
    lub = int(float(client.get_asset_balance(asset='USDT')['locked']))
    tub = int(fub + lub + v3)
    if lcb > 0:
        sId1 = str(client.get_open_orders(symbol='CSPRUSDT')[0]['orderId'])
        sop1 = round(float(client.get_open_orders(symbol='CSPRUSDT')[0]['price']), 5)
        fcb1 = int(float(client.get_asset_balance(asset='cspr')['free']))
        lcb1 = float(client.get_asset_balance(asset='cspr')['locked'])
        tsm1 = fcb1 + lcb1 + v8
        pp1 = round(float(client.get_order_book(symbol='CSPRUSDT', limit=1)['asks'][0][0]), 5)
        if pp1 < sop1 and g11*1.008 < sop1:
            result = client.cancel_order(
            symbol='CSPRUSDT',
            orderId=sId1)
    time.sleep(2)
    if gsa*1.008 <= bms and fcb > 160:
        client.create_order(
            symbol='CSPRUSDT',
            side=SIDE_SELL,
            type=ORDER_TYPE_LIMIT,
            timeInForce=TIME_IN_FORCE_GTC,
            quantity=fcb,
            price=bms)
        sId2 = str(client.get_open_orders(symbol='CSPRUSDT')[0]['orderId'])
        sop2 = round(float(client.get_open_orders(symbol='CSPRUSDT')[0]['price']), 6)
        fcb2 = float(client.get_asset_balance(asset='cspr')['free'])
        lcb2 = float(client.get_asset_balance(asset='cspr')['locked'])
        tsm2 = fcb2 + lcb2 + v8

    mba = str(5715 - tsm)
    fiat = str(g11)
    mba1 = int(5715 - tsm)
    api_instance3 = gate_api.SpotApi(gate_api.ApiClient(configuration))
    if tsm < 5700 and mba1 > 160:
        gob = gate_api.Order(currency_pair='cspr_usdt',
                             side='buy',
                             amount=mba,
                             price=fiat, )
        api_response = api_instance3.create_order(gob)
    if (fcb+lcb) < 160:
        break
    time.sleep(1)

