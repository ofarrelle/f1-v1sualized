# F1 V1sualized

If you're an F1 fan, interested in data visualiztion, or both, go follow the bot at https://twitter.com/F1_databot

A Twitter bot posting data visualizations after every race, including

- Lap by lap timing comparisons
- Race progression
- Championship standings
- Head to head Qualifying results
- and more

Message me on Twitter or send a pull request with suggestions! Currently still working on new features and reliability before I deploy to a server.

## Development

1. Clone and install python packages (will work on a package requirements list in the future). 
2. Create a file `account/twitter_tokens.py`. This file should contain the following variables in global scope:
```
API_KEY
API_SECRET_KEY
BEARER_TOKEN
ACCESS_TOKEN
ACCESS_TOKEN_SECRET
OAUTH2_CLIENT_ID
OAUTH2_CLIENT_SECRET
```
3. Run `bot.py`.
