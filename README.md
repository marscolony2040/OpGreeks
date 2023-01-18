# Options Greeks Visualizer

## Instructions
In order to get this program running you will need to have NPM and React.js installed (there are many tutorials online for installing on the Windows, Mac, or Linux). Additionally you will need the python libraries aiohttp, websockets, numpy, and scipy installed.

## Running
To run this app you need to navigate to its root directly and open two terminals. In the first terminal type in ``` python server``` and in the second terminal type in ``` npm start```

## Rate Limits
This apps payload is very heavy and will require lots of requests. I would advise you to use a max of three to five stocks in the visualizer as to not get ratelimited.

## Visual
![alt](https://github.com/marscolony2040/OpGreeks/blob/main/images/front.png)

## Explination
Using the options greek formulas I found on https://www.macroption.com/option-greeks-excel/ I was able to calculate them by inputting the appropriate variables. For the risk free rate I created a list full of the latest treasury rates and matched their maturities with the options expiration dates. Initially the options expiration dates came in timestamp form but I managed to convert it into month/year format. Additionally I imported Implied Volatilities and Dividend Yields to input into the formulas.
