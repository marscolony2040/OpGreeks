# Options Greeks Visualizer

## Disclaimer
This program is not designed to be used for trading purposes. It is purely a mathematical parody. The reason why I say this is because the options being imported are American Options and the formulas being used are European Greeks. Simply they are not compatible. You may however pick up greek patterns and compare them to the inputted stocks but remember I am not responsible if you choose to use this application to make trades with. It is not designed for real-time trading.

## Snapshot
![alt](https://github.com/marscolony2040/OpGreeks/blob/main/images/runner.png)

## Instructions
In order to get this program running you will need to have NPM and React.js installed (there are many tutorials online for installing on the Windows, Mac, or Linux). Additionally you will need the python libraries aiohttp, websockets, numpy, and scipy installed.

## Running
To run this app you need to navigate to its root directly and open two terminals. In the first terminal type in ``` python server``` and in the second terminal type in ``` npm start```

## Rate Limits
This apps payload is very heavy and will require lots of requests. I would advise you to use a max of three to five stocks in the visualizer as to not get ratelimited.

## Explination
Using the options greek formulas I found on https://www.macroption.com/option-greeks-excel/ I was able to calculate them by inputting the appropriate variables. 

The variables for each greek are S=StockPrice, K=StrikePrice, r=RiskFreeRate, q=Dividend, v=Volatility, and t=Expiration. The stock price and dividend rate was imported using the quote portion of the Options Chain API. The strike price, volatility, and expiration were all imported from the options section of the Options Chain API. The Risk Free Rate was imported by inputting the Treasury Yield Curve rates manually into a list and matching the maturity date of the bond with the options expiration date. Overall this was a fun mathematical visualization that I have created using these brilliant formulas.


