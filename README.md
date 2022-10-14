# LindowBot

A bot with several utilities. It's main function is that of a dictionary bot, allowing one to look
up words using the official Merriam-Webster API, add them to a master vocab list, and run an MC
quiz based on said list.

## Dependencies

- Python 3.9
- Everything in requirements.txt

## Instructions:

- Install Python 3.9 and run the following:

        $ pip install -r requirements.txt

- Create a file called `super_secret.py` with the following variables:

        token = # Insert your own bot authentication token
        api_key = # Insert your own Merriam-Webster API key
        guild_id = # Insert the ID of your own guild/server
        betterwords_id = # Insert the ID of a channel in your server to use for `add_betterwords`
