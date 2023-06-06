import asyncio
import websockets
import aiohttp
import json
import numpy as np
import time
from scipy.stats import norm
from yields import risk_free_rates
from greek import Greeks as GZ

# Extracts Tickers
def extract_ticks(f):
    def handle(*a, **b):
        z = f(*a, **b)
        x, y = np.array(z).T.tolist()
        return y
    return handle

@extract_ticks
def cleanup(x):
    k = []
    for i, j in x.items():
        tag = int(i.replace('S',''))
        k.append([tag, j])
    return list(sorted(k, key=lambda z: z[0]))

# Parses Options Expiration Dates
def parse_expiry(x):
    return x['optionChain']['result'][0]['expirationDates']

# Parses Stocks Dividend Rate
def parse_dividend(x):
    base = x['optionChain']['result'][0]['quote']
    if 'trailingAnnualDividendYield' in base.keys():
        return base['trailingAnnualDividendYield']
    else:
        return 0

# Parses Stock Prices
def parse_price(x):
    return x['optionChain']['result'][0]['quote']['regularMarketPrice']

# Parses Call and Put Data
def parse_op_data(x, tag):
    return x['optionChain']['result'][0]['options'][0][tag]

# Matches appropriate Risk-Free Rate to Treasury Yield
def match_rf(x, yields):
    for i, j in enumerate(yields['mat']):
        if x <= j:
            return yields['yield'][i]
    return 0

# Converts timestamp to month/year format
def dt(x):
    t0 = int(time.time())
    dT = x - t0
    ds = dT/(60*60*24*30)/12
    if ds < 0:
        return -ds
    elif ds <= pow(10, -4):
        return 0
    else:
        return ds

# Catches error (not used)
def opp_err(f):
    def g(*a, **b):
        try:
            return f(*a, **b)
        except:
            return 0
    return g

class Misc:

    def strike_filter(self, tick, op, price):
        n = len(self.x[op][tick])
        m0 = float(np.max(price*0.5, 0))
        m1 = price*1.5
        strike, mat, vol = [], [], []
        for ix, iy, iz in zip(self.x[op][tick], self.y[op][tick], self.z[op][tick]):
            if ix >= m0 and ix <= m1:
                strike.append(ix)
                mat.append(iy)
                vol.append(iz)
        return strike, mat, vol
    
    def gamma_filter(self, tick, op):
        n = len(self.gamma[op][tick])
        mu = np.mean(self.gamma[op][tick])
        sd = np.std(self.gamma[op][tick])
        hold = []
        for i in range(n):
            value = self.gamma[op][tick][i]
            z_score = (value - mu)/sd
            prob = norm.cdf(z_score)
            if value <= 1.0:
                hold.append(value)
            else:
                hold.append(0)
        return hold

    def theta_filter(self, tick, op):
        n = len(self.theta[op][tick])
        mu = np.mean(self.theta[op][tick])
        sd = np.std(self.theta[op][tick])
        hold = []
        for i in range(n):
            value = self.theta[op][tick][i]
            z_score = (value - mu)/sd
            prob = norm.cdf(z_score)
            if prob >= 0.2:
                hold.append(value)
            else:
                hold.append(0)
        return hold



class OpServer(Misc):

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
        
    def start(self):
        loop = asyncio.get_event_loop()
        serve = websockets.serve(self.serving, 'localhost', 8080)
        loop.run_until_complete(serve)
        loop.run_forever()

    def testing(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.serving(None, None))


    async def serving(self, ws, path):
        print("Booted Server..............")
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as sess:
            
            # Fetch treasury rates
            t_rates = await risk_free_rates(sess, 2023)
            self.yields = {'mat':[1/12,2/12,3/12,4/12,6/12,12/12,24/12,36/12,60/12,84/12,120/12,240/12,360/12], 'yield': t_rates}
            
            while True:
                # Fetch Initial Tickers
                resp = await ws.recv()
                resp = json.loads(resp)
                self.tickers = cleanup(resp)

                # Initialize Dictionaries and import data
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
                        await asyncio.sleep(0.1)
                        
                
                # Fetch all data

                slow = False

                if slow == True:
                    for tick in self.tickers:
                        for i in self.expire[tick]:
                            await self.request(sess, tick, mat=i)
                            await asyncio.sleep(0.5)
                else:
                    await asyncio.wait([asyncio.ensure_future(self.request(sess, tick, mat=mat)) for mat in self.expire[tick] for tick in self.tickers])

                # Solve for the greeks
                colur = {'call':['limegreen','black'],'put':['red','white']}

                for op in ('call', 'put'):
                    for tick in self.tickers:
                        s = self.stock_price[tick]
                        q = self.dividend[tick]
			

                        self.x[op][tick], self.y[op][tick], self.z[op][tick] = self.strike_filter(tick, op, s)
                        
                        LZ = len(self.x[op][tick])
                        for ii, (strike, mat, vol) in enumerate(zip(self.x[op][tick], self.y[op][tick], self.z[op][tick])):
                            rf = match_rf(mat, self.yields)
                          
                            delta, gamma, theta, vega, rho = GZ(s, strike, rf, q, vol, mat, op)
                            self.delta[op][tick].append(delta)
                            self.gamma[op][tick].append(gamma)
                            self.theta[op][tick].append(theta)
                            self.vega[op][tick].append(vega)
                            self.rho[op][tick].append(rho)

                            title = f'Parsing {tick} for {op} option | Left: {LZ - ii}'
                            await ws.send(json.dumps({'title': title, 'color': colur[op][0], 'color2':colur[op][1], 'NX': round(ii/LZ*100, 2)}))
                                
                # Final Message to send to client
                msg = {'x': self.x, 
                       'y': self.y, 
                       'vol': self.z, 
                       'delta': self.delta, 
                       'gamma': self.gamma,
                       'theta': self.theta,
                       'vega': self.vega,
                       'rho': self.rho, 
                       'tickers': self.tickers}
                
                print("Writing to Web-App")
                await ws.send(json.dumps(msg))
                print("Written")

    async def request(self, sess, ticker, mat=False):
        print("Fetching {} at Maturity = {}".format(ticker, dt(mat) if mat != False else ''))
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
                
            

                
    
OpServer().start()
#OpServer().testing()
