# sdexbot - A custom trading bot built in Python to trade on the Stellar Decentralized Exchange

Hi! Looks like you found my trading bot. It's still a work-in-progress, but feel free to look around.
My goal is to create a custom bot which trades whatever assets I want on the Stellar network (Learn more about Stellar [here](https://stellar.org/learn/intro-to-stellar)).
<br><br>

## Disclaimer

I don't plan to create some user-friendly program with a nice GUI that's super easy for anyone to use. I'm just writing some code for trading on Stellar, and then writing programs for the actual strategy/trading bot.
If you are familiar with Python, you might be able to use this, but I am just simply creating a bot for myself, and I wanted it to be open source.
(Also, the code isn't commented very well so good luck if you're trying to use it.)
<br><br>

## Some details

<br>

### Dependencies:

Python 3 (>=3.6 - I used 3.6.9)

[stellar-sdk](https://pypi.org/project/stellar-sdk/)

Note: The stellar-sdk requires a C++ compiler for some of its cryptography stuff. So if you're on Windows, it'll tell you to install Microsoft Visual Studio Build Tools 2019.<br>
I use Ubuntu, so gcc is already installed, and I didn't need this step.

<br>

### Project Info

The project is structured like this -

- snippets.md - not part of the bot; contains code snippets in Python for actions on the Stellar Network

- src - contains all the actual code

  - trader.py - contains a Trader class which can be initialized for an SDEX pair and then used to make trades

  - logger.py - contains a Logger class which can be used to log trades; most useful as a handler when listening to a trading stream from your bot account

  - data_utils.py - contains functions to do things like: get historical data, calculate regular averages and moving averages, calculate momentum, etc.

  - other

<br><br>
Thanks for checking out my project! Hope you'll find it interesting or useful. Feel free to fork it or use it yourself or anything else.
