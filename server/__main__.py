import asyncio
import websockets
import aiohttp
import json
import numpy as np



class OpServer:

    def __init__(self, tickers=['AAPL','GOOGL','AMZN']):
        self.tickers = tickers
        self.url = 'https://query2.finance.yahoo.com/v7/finance/options/{}'
        self.url2 = 'https://query2.finance.yahoo.com/v7/finance/options/{}?date={}'
        self.data = {}
        
    def start(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.serving())

    async def serving(self):
        async with aiohttp.ClientSession() as sess:
            for tick in self.tickers:
                s = await self.request(sess, tick)
                self.data[tick] = s

    async def request(self, sess, ticker, mat=False):
        async sess.get(self.url.format(ticker) if mat == False else self.url.format(ticker, mat)) as response:
            r = await response.text()
            return json.loads(r)

    
