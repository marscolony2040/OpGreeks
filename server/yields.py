from bs4 import BeautifulSoup
import numpy as np
import pandas as pd

url = 'https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value={}'

def parse(f):

    def organize(x, v):
        hold = []
        for i in v:
            hold.append(x[i])
        z = np.array(hold).T.tolist()
        return z

    async def handle(*a, **b):
        z = await f(*a, **b)
        z = z.split('\n')
        z = [i for i in z if i != '']
        
        n = len(z)
        b = 0
        index = []
        cols = []
        vals = (1, 2, 3, 4, 6, 12, 24, 36, 60, 84, 120, 240, 360)
        qz = (10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22)
        hold = {k:[] for k in vals}
        while b < n:
            index.append(z[b])
            for u, v in zip(vals, qz):
                if b == 0:
                    cols.append(z[v + b].replace(' ',''))
                else:
                    yd = z[v + b].replace(' ','')
                    if yd == "N/A":
                        hold[u].append(np.nan)
                    else:
                        try:
                            hold[u].append(float(yd))
                        except:
                            hold[u].append(np.nan)
            b += 23
        z = organize(hold, vals)
        del index[0]
        return pd.DataFrame(data=z, index=index, columns=cols)
    return handle

@parse
async def get_yields(session, url):
    async with session.get(url) as resp:
        r = await resp.text()
    s = BeautifulSoup(r, 'html.parser')
    b = s.find('table', attrs={'class':'usa-table views-table views-view-table cols-23'})
    data = b.text.strip()
    return data

async def risk_free_rates(session, year):
    resp = await get_yields(session, url.format(year))
    rf = resp.values[-1]
    return [i/100 for i in rf.tolist()]


