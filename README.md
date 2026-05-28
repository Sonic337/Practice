```markdown
# Practice

A collection of scripts built while learning Python, Git, and terminal workflows.

## Scripts

### weather CLI
Check live weather from the terminal.
```
weather multi Mumbai Delhi Pune Dubai
weather weather London
```

### weather_log.py
Logs Pune's weather to `weather_log.txt` every hour via cron.

### weather_telegram.py
Sends Pune's weather to Telegram. Runs daily at 9am via cron.

### weather_final.py
Weather logger that reads city from `.env` file.

### hl_alert.py
Monitors a token on Hyperliquid and spams Telegram the moment it goes live.
```
python3 hl_alert.py
```

### birthday_countdown.py
Sends a Telegram message counting down to Harish's birthday. Fires twice on June 5th.

### backup.sh
Backs up the practice folder daily at 9am via cron.

### errors.py
Error handling examples — timeouts, HTTP errors, invalid config with auto-fallback.

### json_practice.py
Reading, writing, and parsing JSON files.

### datetime_practice.py
Datetime formatting, arithmetic, and countdowns.

### classes.py
Python OOP — classes, methods, inheritance.

### secure.py / dotenv_test.py
Environment variable and `.env` file examples — keeping secrets out of code.

## Setup

```
pip3 install requests python-dotenv
```

Create a `.env` file:
```
CITY=Pune
TELEGRAM_TOKEN=your-token
TELEGRAM_CHAT_ID=your-chat-id
```

## Cron Jobs

| Time | Script |
|------|--------|
| 9am daily | backup.sh |
| 9am daily | weather_telegram.py |
| June 5 12am & 1:30am | birthday_countdown.py |
```
