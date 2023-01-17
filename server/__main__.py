import asyncio
import websockets
import aiohttp
import json
import numpy as np
import time

def parse_expiry(x):
    return x['optionChain']['result'][0]['expirationDates']

def parse_op_data(x, tag):
    return x['optionChain']['result'][0]['options'][0][tag]

def dt(x):
    t0 = int(time.time())
    dT = x - t0
    ds = dT/(60*60*24*30)/12
    return ds

class OpServer:

    def __init__(self, tickers=['SPY','MSFT']):
        self.tickers = tickers
        self.url = 'https://query2.finance.yahoo.com/v7/finance/options/{}'
        self.url2 = 'https://query2.finance.yahoo.com/v7/finance/options/{}?date={}'
        self.expire = {}
        self.x = {'call':{}, 'put':{}}
        self.y = {'call':{}, 'put':{}}
        self.z = {'call':{}, 'put':{}}
        
    def start(self):
        loop = asyncio.get_event_loop()
        serve = websockets.serve(self.serving, 'localhost', 8080)
        loop.run_until_complete(serve)
        loop.run_forever()

    async def serving(self, ws, path):
        async with aiohttp.ClientSession() as sess:
            for op in ('call', 'put'):
                for tick in self.tickers:
                    s = await self.request(sess, tick)
                    self.expire[tick] = parse_expiry(s)
                    self.x[op][tick] = []
                    self.y[op][tick] = []
                    self.z[op][tick] = []
                    
            
            tasks = [asyncio.ensure_future(self.request(sess, tick, mat=i)) for i in self.expire[tick] for tick in self.tickers]
            await asyncio.wait(tasks)

            msg = {'x': self.x, 'y': self.y, 'vol': self.z, 'tickers': self.tickers}
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
            await asyncio.wait(0.07)

                
    
OpServer().start()