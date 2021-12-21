import re
import requests

from data.func import translate


def validate_wallet(wallet):
    if not re.match('P\d{7,12}$', wallet):
        return False


class PayeerAPIException(Exception):
    pass


class PayeerAPI:
    def __init__(self, account, apiId, apiPass):
        self.account = account
        self.apiId = apiId
        self.apiPass = apiPass
        self.api_url = 'https://payeer.com/ajax/api/api.php'
        self.auth_data = {'account': self.account, 'apiId': self.apiId, 'apiPass': self.apiPass}

    def request(self, **kwargs):
        data = self.auth_data
        if kwargs:
            data.update(kwargs)
        resp = requests.post(url=self.api_url, data=data).json()
        error = resp.get('errors')
        if error:
            raise PayeerAPIException(error)
        else:
            return resp

    def auth_check(self):
        try:
            resp = self.request()
        except PayeerAPIException:
            return False

    def get_balance(self):
        try:
            balance = list()
            for key, value in self.request(action='balance')['balance'].items():
                if float(value['BUDGET']) > 0:
                    balance.append(f'{value["BUDGET"]} {key}')
            balance = ', '.join(balance)
            return balance
        except PayeerAPIException as e:
            message = translate(e)
            message = message[6:-6]
            return message

    def check_user(self, user):
        try:
            self.request(action='checkUser', user=user)
        except PayeerAPIException:
            return False
        return True

    def get_exchange_rate(self, output='N'):
        return self.request(action='getExchangeRate', output=output)['rate']

    def get_pay_systems(self):
        return self.request(action='getPaySystems')['list']

    def get_history_info(self, history_id):
        return self.request(action='historyInfo', historyId=history_id)['info']

    def shop_order_info(self, shop_id, order_id):
        return self.request(action='shopOrderInfo', shopId=shop_id, orderId=order_id)

    def transfer(self, sum, to, cur_in='USD', cur_out='USD',
                 comment=None, protect=None, protect_period=None, protect_code=None):
        validate_wallet(to)
        data = {'action': 'transfer', 'sum': sum, 'to': to, 'curIn': cur_in, 'curOut': cur_out}
        if comment:
            data['comment'] = comment
        if protect:
            data['protect'] = protect
            if protect_period:
                data['protectPeriod'] = protect_period
            if protect_code:
                data['protectCode'] = protect_code
        try:
            resp = self.request(**data)
            if resp.get('historyId', 0) > 0:
                return True
            else:
                return False
        except PayeerAPIException as e:
            return e

    def check_output(self, ps, ps_account, sum_in, cur_in='USD', cur_out='USD'):
        data = {'action': 'initOutput', 'ps': ps, 'param_ACCOUNT_NUMBER': ps_account,
                'sumIn': sum_in, 'curIn': cur_in, 'curOut': cur_out}
        try:
            self.request(**data)
        except PayeerAPIException:
            return False
        return True

    def output(self, ps, ps_account, sum_in, cur_in='USD', cur_out='USD'):
        data = {'action': 'output', 'ps': ps, 'param_ACCOUNT_NUMBER': ps_account,
                'sumIn': sum_in, 'curIn': cur_in, 'curOut': cur_out}
        return self.request(**data)

    def history(self, **kwargs):
        kwargs['action'] = 'history'
        return self.request(**kwargs)['history']
