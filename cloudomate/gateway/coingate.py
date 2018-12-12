from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json

from fake_useragent import UserAgent
from future import standard_library
from mechanicalsoup import StatefulBrowser
from websocket import create_connection

from cloudomate.gateway.gateway import Gateway, PaymentInfo

standard_library.install_aliases()


class CoinGate(Gateway):

    @staticmethod
    def get_gateway_fee():
        return 0.0

    @staticmethod
    def get_name():
        return "coingate"

    @staticmethod
    def has_pay_amount(data):
        if 'message' not in data:
            return False
        if 'type' in data:
            return False
        return isinstance(data['message'], dict) and 'pay_amount' in data['message'] and data['message']['pay_amount']

    @staticmethod
    def extract_info(url):
        user_agent = UserAgent(fallback="Mozilla/5.0 (X11; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0")
        browser = StatefulBrowser(user_agent=user_agent.random)
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9',
            'upgrade-insecure-requests': '1',
        }
        response = browser.open(url, headers=headers)
        cookies = []
        for cookie in response.cookies:
            cookie = cookie
            cookies.append('{}: {}'.format(cookie.name, cookie.value))
        ws = create_connection("wss://coingate.com/cable", cookie='; '.join(cookies), origin='https://coingate.com')

        invoice_id = url.split('/')[-1]

        debug_log = []

        identifier = json.dumps({
            "channel": "InvoiceChannel",
            "invoice_uuid": invoice_id
        })
        data1 = json.dumps({
            "command": "subscribe",
            "identifier": identifier
        })
        debug_log.append('> ' + data1)
        ws.send(data1)

        data2 = json.dumps({
            "command": "message",
            "identifier": identifier,
            "data": json.dumps({"invoice_uuid": invoice_id, "action": "check"})
        })
        debug_log.append('> ' + data2)
        ws.send(data2)
        data3 = json.dumps({
            "command": "message",
            "identifier": identifier,
            "data": json.dumps({
                "pay_currency_id": 8,
                "email": "",
                "ln": False,
                "action": "select_pay_currency"
            })
        })
        debug_log.append('> ' + data3)
        ws.send(data3)

        for i in range(0, 6):
            result = ws.recv()
            debug_log.append('< ' + result)
            result_json = json.loads(result)
            if CoinGate.has_pay_amount(result_json):
                return PaymentInfo(float(result_json['message']['pay_amount']), result_json['message']['address'])
        print("CoinGate: No payment amount found \nDebug information: \n{}".format('\n'.join(debug_log)))
        return None


if __name__ == '__main__':
    CoinGate.extract_info('https://coingate.com/invoice/5112d1ec-a160-4f84-958d-d0c73543b034')
