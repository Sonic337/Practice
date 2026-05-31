# Practice

A collection of Python scripts built while learning Python, APIs, Telegram bots, and terminal workflows.

## Setup

```bash
pip3 install -r requirements.txt
```

Create a `.env` file with the secrets each script needs (see per-script notes below):
```
CITY=Pune
TELEGRAM_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
HYPERLIQUID_WALLET=0x...
OMDB_API_KEY=your-key
MY_API_KEY=your-key
```

---

## Crypto & Portfolio

### crypto.py
Fetches trending coins from CoinGecko and prints them. Also exports `COIN_MAP` used by portfolio.py.
```bash
python3 crypto.py
```

### portfolio.py
Tracks a crypto portfolio with live prices via CoinGecko. Logs snapshots to `portfolio_history.csv`.
```bash
python3 portfolio.py add btc 0.5 42000
python3 portfolio.py add eth 2 2500
python3 portfolio.py show            # live P&L table
python3 portfolio.py history         # snapshot history
python3 portfolio.py list            # holdings list
python3 portfolio.py alert 10        # Telegram alert if ±10% from buy price
python3 portfolio.py remove btc
```
Requires: `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID` (for alerts only)

### hl_pnl.py
Fetches your open positions and P&L from Hyperliquid and sends a summary to Telegram.
```bash
python3 hl_pnl.py
```
Requires: `HYPERLIQUID_WALLET`, `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`

### hl_alert.py
Polls Hyperliquid and sends a Telegram message the moment a tracked token goes live.
```bash
python3 hl_alert.py
```
Requires: `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`

### hyper_evm_alert.py
Monitors a contract on the Hyperliquid EVM and sends a Telegram alert on activity.
```bash
python3 hyper_evm_alert.py
```
Requires: `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`

### news_scraper.py
Fetches the latest crypto headlines from the CoinDesk RSS feed. Prints top 10 and sends top 3 to Telegram.
```bash
python3 news_scraper.py
```
Requires: `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`

---

## Finance Tracker

### finance.py
CLI personal finance tracker. Stores transactions in `finance.json`.
```bash
python3 finance.py income 50000 salary "June salary"
python3 finance.py expense 1200 food "lunch"
python3 finance.py balance
python3 finance.py summary
python3 finance.py monthly
python3 finance.py savingsrate
python3 finance.py list
python3 finance.py export              # writes finance_export.csv
python3 finance.py budget food 5000
python3 finance.py checkbudget
python3 finance.py search coffee
python3 finance.py chart
python3 finance.py top
python3 finance.py biggestincome
python3 finance.py recurring expense 500 subscriptions "Netflix"
python3 finance.py applyrecurring
```

---

## Weather

### cli_tool.py
Live weather lookup from the terminal via wttr.in.
```bash
python3 cli_tool.py Mumbai
python3 cli_tool.py London Paris Tokyo
```

### weather.py
Basic weather fetch for a single city.

### weather_final.py
Weather fetch that reads the city from `CITY` in `.env`.
```bash
python3 weather_final.py
```

### weather_log.py
Logs weather for the configured city to `weather_log.txt`. Designed to run hourly via cron.

### weather_csv.py
Fetches weather and appends a row to `weather_data.csv`.

### weather_analysis.py
Reads `weather_data.csv` and prints basic statistics (min/max/avg temperature).

### weather_telegram.py
Sends the current weather to Telegram. Runs daily at 9am via cron.
```bash
python3 weather_telegram.py
```
Requires: `CITY`, `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`

---

## Bots & Alerts

### telegram_bot.py
Basic Telegram bot that responds to `/start` and `/weather`.
```bash
python3 telegram_bot.py
```
Requires: `TELEGRAM_TOKEN`

### birthday_countdown.py
Sends a Telegram countdown message to Harish's birthday. Fires twice on June 5th (12am & 1:30am via cron).
Requires: `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`

---

## Data & APIs

### scraper.py
Fetches trending coins from CoinGecko and prints name, symbol, price, and 24h change.
```bash
python3 scraper.py
```

### halal_restaurants.py
CLI tracker for halal restaurants stored in `restaurants.json`.
```bash
python3 halal_restaurants.py add
python3 halal_restaurants.py list
python3 halal_restaurants.py search "biryani"
```

### movies.py
Looks up movie info using the OMDB API.
```bash
python3 movies.py "Inception"
```
Requires: `OMDB_API_KEY`

### pokemon.py
Fetches Pokémon stats from the PokéAPI.
```bash
python3 pokemon.py pikachu
```

### api.py / auth_api.py / post_api.py
Examples of making GET, authenticated, and POST requests with `requests`.

---

## Learning Scripts

| Script | What it covers |
|--------|---------------|
| `classes.py` | OOP — classes, methods, inheritance |
| `csv_practice.py` | Reading and writing CSV files |
| `datatypes.py` | Python data types overview |
| `datetime_practice.py` | Formatting, arithmetic, countdowns |
| `dotenv_test.py` | Loading secrets from `.env` with python-dotenv |
| `errors.py` | Exception handling, timeouts, fallbacks |
| `fileio.py` | Reading and writing text files |
| `functions.py` | Function definitions and return values |
| `json_practice.py` | Reading, writing, and parsing JSON |
| `logic.py` | Conditionals and boolean logic |
| `regex_practice.py` | Pattern matching with `re` |
| `secure.py` | Reading secrets from environment variables |
| `threading_practice.py` | Basic threading with `threading.Thread` |

---

## Shell Scripts

### backup.sh
Backs up the `~/practice` folder to `~/backups/YYYY-MM-DD/`. Runs daily at 9am via cron.
```bash
bash backup.sh
```

### portfolio_alert.sh
Wrapper to run `portfolio.py alert` from cron.

---

## Cron Jobs

| Schedule | Script | Purpose |
|----------|--------|---------|
| 9am daily | `backup.sh` | Back up the repo |
| 9am daily | `weather_telegram.py` | Morning weather to Telegram |
| June 5 12am & 1:30am | `birthday_countdown.py` | Birthday countdown message |
