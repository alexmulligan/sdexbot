# SDEXBOT

## A custom trading bot built in Python to trade on the Stellar Decentralized Exchange

Hi! Looks like you found my trading bot. It's still a work-in-progress, but feel free to look around.
My goal is to create a custom bot which trades whatever assets I want on the Stellar network (Learn more [here](https://stellar.org/learn/intro-to-stellar)).
<br><br>

### Disclaimer

To be up front, the plan is not to create some polished, user-friendly program with a nice GUI that anyone can use, with modular functionality like Kelp or anything. I'm just writing some generic code for trading, logging, and price history on Stellar, and then writing Python programs for the actual strategy/trading bot.
If you are familiar with Python, you'll probably be able to use this yourself, but I am just simply creating a bot for myself and then publishing it as open-source.
Maybe somewhere down the line, this'll change and I can make it more user-friendly, but for now, I'm focusing on making something that actually works.
(Also, the code isn't commented very well so good luck if you're trying to use it.)
<br><br>

### Some details

<br>
&nbsp;&nbsp;&nbsp;&nbsp;<b>Dependencies:</b>

Python 3 (idk if you need at least a specific version - I used 3.6.9)

Python Standard Library (of course)

[stellar-sdk](https://pypi.org/project/stellar-sdk/)

[stellar-base](https://pypi.org/project/stellar-base/)

Note: The stellar-sdk requires a C++ compiler for some of its cryptography stuff. So if you're on Windows, it'll tell you to install Microsoft Visual Studio Build Tools 2019. (Make sure when running the build tools installer to check the box for installing Visual C++)
I use Ubuntu, so of course gcc is already installed, so I didn't need this step.

&nbsp;&nbsp;&nbsp;&nbsp;<b>In case your interested:</b>
The project is structured like this -

- snippets.md - contains code snippets in Python for actions on the Stellar Network

- src - contains all the actual code

  - trader.py - contains a Trader class which can be used to: initialize it with the Horizon server instance, your secret key, the assets you want it to trade, and parameters for logging; and then actually make trades, etc.

  - logger.py - contains a Logger class used mainly by the Trader class. Just keeps the code separate and makes logging easier to do in the Trader class

  - data_funcs.py - contains functions to do things like: get historical price data from Horizon, get volume date from Horizon, calculate averages of different period of time, calculate simple and exponential moving averages, calculate momentum, etc.

  - <other_file>.py - other files are programs meant to be run themselves; they are actual implementations of strategies/working trading bots (they rely on the other, more generic/reusable files)

<br><br>
Thanks for checking out my project! Hope you'll find it interesting or useful. Feel free to fork it or use it yourself or anything else.
