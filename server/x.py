import asyncio
import websockets
import aiohttp
import json
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class Options:

    def __init__(self):
        self.ticker = 'GS'

    def go(self):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.opt())

    def house(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(websockets.serve(self.opt, 'localhost', 8080))
        loop.run_forever()
        

    async def opt(self, ws, path):
        url = 'https://query2.finance.yahoo.com/v7/finance/options/{}'
        url2 = 'https://query2.finance.yahoo.com/v7/finance/options/{}?date={}'

        async def request(on=False):
            async with aiohttp.ClientSession() as sess:
                async with sess.get(url2.format(self.ticker, on) if on else url.format(self.ticker)) as resp:
                    r = await resp.text()
                    r = json.loads(r)
                    return r

        r = await request()
        expiration = r['optionChain']['result'][0]['expirationDates']
        strikes = r['optionChain']['result'][0]['strikes']
        hold = {i:{j:np.nan for j in strikes} for i in expiration}

        for ex in expiration:
            r = await request(on=ex)
            for i in r['optionChain']['result'][0]['options'][0]['calls']:
                strike = i['strike']
                iv = i['impliedVolatility']
                hold[ex][strike] = float(iv)

        xx, yy = np.meshgrid(strikes, expiration)
        zz = []
        for i in range(len(xx)):
            temp = []
            for j in range(len(xx[0])):
                temp.append(hold[yy[i][j]][xx[i][j]])
            zz.append(temp)
        xx, yy = xx.tolist(), yy.tolist()
            
        await ws.send(json.dumps({'x':xx, 'y':yy, 'z': zz}))


Options().house()

on = False
if on:
    xm, ym, zm = Options().go()
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    fig.tight_layout()
    ax.scatter(xm, ym, zm, color='red')
    plt.show()
