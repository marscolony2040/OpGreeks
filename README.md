# Options Greeks Visualizer

## Disclaimer
This program should in no way, shape, or form be used for actual trading. This program was created for purely Quantitative Finance and Math methods. Plus the data takes long to load in the visualizer, and options greeks fluctuate very quick to be sitting around using this program.

## Snapshot
![alt](https://github.com/marscolony2040/OpGreeks/blob/main/images/pic.png)

## Instructions
In order to get this program running you will need to have NPM and React.js installed (there are many tutorials online for installing on the Windows, Mac, or Linux). Additionally you will need the python libraries aiohttp, websockets, numpy, and scipy installed.

## Running
To run this app you need to navigate to its root directly and open two terminals. In the first terminal type in ``` python server``` and in the second terminal type in ``` npm start```

## Rate Limits
This apps payload is very heavy and will require lots of requests. I would advise you to use a max of three to five stocks in the visualizer as to not get ratelimited.

## Programs Methods
1. Sends a request to fetch the latest Treasury Yields to be used as the risk free rates
2. Recieves a list of tickers to fetch for the visualization
3. Fetches options chain data in order to extract the expirations list
4. Sends mass asynchronus request to get all of the options data
5. Implied volatility and expiry are then used to match the correct treasury rate to the calculations by matching expiry dates
6. Additionally the dividend yield is imported as well and all of the inputs are pushed through the trinomial tree and greeks are returned.

