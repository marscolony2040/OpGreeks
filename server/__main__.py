import asyncio
import websockets
import aiohttp
import json
import numpy as np
import time
from scipy.stats import norm

def parse_expiry(x):
    return x['optionChain']['result'][0]['expirationDates']

def parse_dividend(x):
    base = x['optionChain']['result'][0]['quote']
    if 'trailingAnnualDividendYield' in base.keys():
        return base['trailingAnnualDividendYield']
    else:
        return 0

def parse_price(x):
    return x['optionChain']['result'][0]['quote']['regularMarketPrice']

def parse_op_data(x, tag):
    return x['optionChain']['result'][0]['options'][0][tag]

def match_rf(x, yields):
    for i, j in enumerate(yields['mat']):
        if x <= j:
            return yields['yield'][i]
    return 0

def dt(x):
    t0 = int(time.time())
    dT = x - t0
    ds = dT/(60*60*24*30)/12
    return ds

class Greeks:

    def d2(self, d1, v, t):
        return d1 - v*np.sqrt(t)

    def d1(self, s, k, r, q, v, t):
        A = np.log(s/k) + (r - q + 0.5*v**2)*t
        B = v*np.sqrt(t)
        return A / B

    def N(self, x):
        return norm.cdf(x)

    def N1(self, x):
        return norm.pdf(x)

    def Delta(self, s, k, r, q, v, t, optype='call'):
        D1 = self.d1(s, k, r, q, v, t)
        D2 = self.d2(D1, v, t)
        if optype == 'call':
            return np.exp(-q*t)*self.N(D1)
        else:
            return np.exp(-q*t)*(self.N(D1) - 1)

    def Gamma(self, s, k, r, q, v, t):
        D1 = self.d1(s, k, r, q, v, t)
        D2 = self.d2(D1, v, t)
        return (np.exp(-q*t)/(s*v*np.sqrt(t)))*self.N1(D1)

    def Theta(self, s, k, r, q, v, t, optype='call'):
        D1 = self.d1(s, k, r, q, v, t)
        D2 = self.d2(D1, v, t)
        a = -(s*v*np.exp(-q*t))*self.N1(D1)/(2*np.sqrt(t))
        if optype == 'call':
            b = r*k*np.exp(-r*t)*self.N(D2) + q*s*np.exp(-q*t)*self.N(D1)
            return (1/252)*(a - b)
        else:
            b = r*k*np.exp(-r*t)*self.N(-D2) - q*s*np.exp(-q*t)*self.N(-D1)
            return (1/252)*(a + b)

    def Vega(self, s, k, r, q, v, t):
        D1 = self.d1(s, k, r, q, v, t)
        return (1/100)*s*np.exp(-q*t)*np.sqrt(t)*self.N1(D1)

    def Rho(self, s, k, r, q, v, t, optype='call'):
        D1 = self.d1(s, k, r, q, v, t)
        D2 = self.d2(D1, v, t)
        if optype == 'call':
            return (1/100)*k*t*np.exp(-r*t)*self.N(D2)
        else:
            return -(1/100)*k*t*np.exp(-r*t)*self.N(-D2)

class OpServer(Greeks):

    def __init__(self, tickers=['SPY','MSFT']):
        self.tickers = tickers
        self.url = 'https://query2.finance.yahoo.com/v7/finance/options/{}'
        self.url2 = 'https://query2.finance.yahoo.com/v7/finance/options/{}?date={}'
        self.expire = {}
        self.dividend = {}
        self.stock_price = {}
        self.x = {'call':{}, 'put':{}}
        self.y = {'call':{}, 'put':{}}
        self.z = {'call':{}, 'put':{}}
        self.delta = {'call':{}, 'put':{}}
        self.gamma = {'call':{}, 'put':{}}
        self.theta = {'call':{}, 'put':{}}
        self.vega = {'call':{}, 'put':{}}
        self.rho = {'call':{}, 'put':{}}
        self.yields = {'mat':[1/12,2/12,3/12,4/12,6/12,12/12,24/12,36/12,60/12,84/12,120/12,240/12,360/12], 'yield': [0.0458,0.0459,0.0467,0.0473,0.0477,0.0469,0.0422,0.0388,0.036,0.0355,0.0349,0.0379,0.0361]}
        
    def start(self):
        loop = asyncio.get_event_loop()
        serve = websockets.serve(self.serving, 'localhost', 8080)
        loop.run_until_complete(serve)
        loop.run_forever()

    def testing(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.serving(None, None))


    async def serving(self, ws, path):
        async with aiohttp.ClientSession() as sess:
            for op in ('call', 'put'):
                for tick in self.tickers:
                    s = await self.request(sess, tick)
                    self.expire[tick] = parse_expiry(s)
                    self.dividend[tick] = parse_dividend(s)
                    self.stock_price[tick] = parse_price(s)
                    self.x[op][tick] = []
                    self.y[op][tick] = []
                    self.z[op][tick] = []
                    self.delta[op][tick] = []
                    self.gamma[op][tick] = []
                    self.theta[op][tick] = []
                    self.vega[op][tick] = []
                    self.rho[op][tick] = []
                    
            
            tasks = [asyncio.ensure_future(self.request(sess, tick, mat=i)) for i in self.expire[tick] for tick in self.tickers]
            await asyncio.wait(tasks)

            for op in ('call', 'put'):
                for tick in self.tickers:
                    s = self.stock_price[tick]
                    q = self.dividend[tick]
                    
                    for strike, mat, vol in zip(self.x[op][tick], self.y[op][tick], self.z[op][tick]):
                        rf = match_rf(mat, self.yields)
                        self.delta[op][tick].append(self.Delta(s, strike, rf, q, vol, mat, optype=op))
                        self.gamma[op][tick].append(self.Gamma(s, strike, rf, q, vol, mat))
                        self.theta[op][tick].append(self.Theta(s, strike, rf, q, vol, mat, optype=op))
                        self.vega[op][tick].append(self.Vega(s, strike, rf, q, vol, mat))
                        self.rho[op][tick].append(self.Rho(s, strike, rf, q, vol, mat, optype=op))

            msg = {'x': self.x, 
                   'y': self.y, 
                   'vol': self.z, 
                   'delta': self.delta, 
                   'gamma': self.gamma,
                   'theta': self.theta,
                   'vega': self.vega,
                   'rho': self.rho, 
                   'tickers': self.tickers}
            await ws.send(json.dumps(msg))

    async def request(self, sess, ticker, mat=False):
        async with sess.get(self.url.format(ticker) if mat == False else self.url2.format(ticker, mat)) as response:
            r = await response.text()
            if mat == False:
                return json.loads(r)
            else:
                resp = json.loads(r)
                for op, osp in zip(('call', 'put'), ('calls', 'puts')):
                    ux, uy, uz = np.array([[float(k['strike']), dt(float(k['expiration'])), float(k['impliedVolatility'])] for k in parse_op_data(resp, osp)]).T.tolist()
                    self.x[op][ticker] += ux
                    self.y[op][ticker] += uy
                    self.z[op][ticker] += uz
            await asyncio.sleep(0.5)

                
    
OpServer().start()