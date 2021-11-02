import requests as r
import json

class SistemaSETE():

    def __init__(self, user, password):
        self.baseUrl = "https://sete.transportesufg.eng.br"
        #self.baseUrl = "https://virtserver.swaggerhub.com/umarley/SistemaSETE/1.0.0"
        self.url = ""
        self.user = user
        self.password = password
        self.token = ""

    def AuthenticatorP(self):
        self.url = f"{self.baseUrl}/authenticator/sete"
        self.headers = {
            "accept": "application/json",
            "content-type" : "application/json"
        }
        self.PARAMS = dict(
            usuario=self.user,
            senha=self.password
        )
        self.dadosJSON = json.dumps(self.PARAMS)
        self.response = r.post(self.url, data=self.dadosJSON, headers=self.headers)
        if self.response.ok:
            self.token = self.response.json()["access_token"]["access_token"]
            return (self.response.json(), True)
        else:
            return (self.response.json(), False)

    def AuthenticatorG(self):
        self.url = f"{self.baseUrl}/authenticator/sete"
        self.headers = {
            "accept": "application/json",
            "Authorization": self.token
        }
        self.response = r.get(self.url, headers=self.headers)
        if self.response.ok:
            return (self.response.json(), True)
        else:
            return (self.response.json(), False)

    def Logout(self):
        self.url = f"{self.baseUrl}​/users​/logout"
        self.headers = {
            "accept": "application/json",
            "Authorization": self.token
        }
        self.response = r.get(self.url, headers=self.headers)
        if self.response.ok:
            return (self.response.json(), True)
        else:
            return (self.response.json(), False)