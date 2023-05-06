# kp-telegram-bot

## Usage
```
usage: main.py [-h] -t TOKEN [-a ALIASES] [-d DB_URI]

options:
  -h, --help            show this help message and exit
  -t TOKEN, --token TOKEN
                        Telegram Bot token
  -a ALIASES, --aliases ALIASES
                        Path to YAML file with user aliases
  -d DB_URI, --db-uri DB_URI
                        Database URI
```

## Run

### Docker compose (with Mongo)
```
export BOT_TOKEN=<BOT_TOKEN>
docker-compose up -d
```

### Docker
```
docker build -t kp-telegram-bot .
docker run -d -e BOT_TOKEN=<BOT_TOKEN> kp-telegram-bot
```

### Local
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python main.py -t <BOT_TOKEN>
```
