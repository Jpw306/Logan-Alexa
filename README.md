# Logan's Alexa

## _A multipurpose Discord bot that brings together a community through music, user stats, and much more_

# Setup:

Make sure that you use Python 3.5.0 or greater
#### openjdk-13.0.2:
Install [openjdk-13.0.2] for your current OS and add the downloaded folder to the root of the bot's directory.

#### Lavalink:
Go to [Lavalink] github page and download the Lavalink.jar file. After it has downloaded run the following commands ton boot up a Lavalink server
```sh
cd ./bot/openjdk-13.0.2/bin/
java -jar Lavalink.jar
```

#### Discord[voice] and wavelink:
To install Discord.py and wavelink run the following command in the terminal.
```sh
pip install discord.py[voice] wavelink
```

#### application.yml:
In the new directory, go into bin folder and create a file called "application.yml". Copy and paste the following into the newly created file.

```sh
server: # REST and WS server
  port: 2333
  address: 127.0.0.1
lavalink:
  server:
    password: "youshallnotpass"
    sources:
      youtube: true
      bandcamp: true
      soundcloud: true
      twitch: true
      vimeo: true
      http: true
      local: false
    bufferDurationMs: 400
    youtubePlaylistLoadLimit: 6 # Number of pages at 100 each
    playerUpdateInterval: 5 # How frequently to send player updates to clients, in seconds
    youtubeSearchEnabled: true
    soundcloudSearchEnabled: true
    gc-warnings: true
    #ratelimit:
      #ipBlocks: ["1.0.0.0/8", "..."] # list of ip blocks
      #excludedIps: ["...", "..."] # ips which should be explicit excluded from usage by lavalink
      #strategy: "RotateOnBan" # RotateOnBan | LoadBalance | NanoSwitch | RotatingNanoSwitch
      #searchTriggersFail: true # Whether a search 429 should trigger marking the ip as failing
      #retryLimit: -1 # -1 = use default lavaplayer value | 0 = infinity | >0 = retry will happen this numbers times

metrics:
  prometheus:
    enabled: false
    endpoint: /metrics

sentry:
  dsn: ""
  environment: ""
#  tags:
#    some_key: some_value
#    another_key: another_value

logging:
  file:
    max-history: 30
    max-size: 1GB
  path: ./logs/

  level:
    root: INFO
    lavalink: INFO
```
#### Data folder:
Create a folder called "data" in the root of the bot's directory

#### Logan.db:
Run the following command in the terminal to go into the bot's data folder

```sh
cd ./bot/data/
```
Run the following SQL in the terminal to create a new database in the data folder
```sh
CREATE TABLE "discord" (
	"id"	TEXT NOT NULL,
	"uv"	INTEGER NOT NULL DEFAULT 0,
	"dv"	INTEGER NOT NULL DEFAULT 0,
	"msg"	INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY("id")
)
```

#### token.0:
Go to [Discord Developer Portal] and create a new application. On the side menu, click on Bot and then Add Bot. Then click on copy underneath the token and paste it into token.0

#### Data Folder:

After setup, your directory should look like this:

```sh
bot/
    cogs/
    data/
        Logan.db
        token.0
    openjdk-13.0.2/
        bin/
            application.yml
    launcher.py
```

## Usage:
Run launcher.py in the bot's directory and _voilà_

> Note: For the user stats to work as intended, feel free to change the emoji names in the bot.py file

[Lavalink]: https://ci.fredboat.com/viewLog.html?buildId=lastSuccessful&buildTypeId=Lavalink_Build&tab=artifacts&guest=1
[openjdk-13.0.2]: https://jdk.java.net/archive/
[Discord Developer Portal]: https://discord.com/developers/applications
