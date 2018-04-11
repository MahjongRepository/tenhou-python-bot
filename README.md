[![Build Status](https://travis-ci.org/MahjongRepository/tenhou-python-bot.svg?branch=master)](https://travis-ci.org/MahjongRepository/tenhou-python-bot)

For now only **Python 3.5+** is supported.

# What do we have here?

![Example of bot game](https://cloud.githubusercontent.com/assets/475367/25059936/31b33ac2-21c3-11e7-8cb2-de33d7ba96cb.gif)

## Mahjong hands calculation

You can find it here: https://github.com/MahjongRepository/mahjong

## Mahjong bot

For research purposes we built a simple bot to play riichi mahjong on tenhou.net server.

### 0.0.5 version

It can reach a tempai and call a riichi. It doesn't know about dora, yaku, defence and etc. 
Only about tempai and riichi so far.

This version had played 335 games (hanchans) and achieved only first dan (初段) on the tenhou.net so far
(and lost it later, and achieved it again...).

Rate was somewhere around R1350.

Stat:

|   | Result |
| --- | --- |
| Average position | 2.78 |
| Win rate | 20.73% |
| Feed rate | 19.40% |
| Riichi rate | 36.17% |
| Call rate | 0% |

So, even with the current simple logic it can play and win.

### 0.2.5 version

This version is much smarter than 0.0.x versions. It can open hand, go to defence and build hand effective (all supported features you can find in releases description).

This version had played 375 games (hanchans) and achieved second dan (二段).

Rate was somewhere around R1500.

Stat:

|   | Result |
| --- | --- |
| Average position | 2.65 |
| Win rate | 18.60% |
| Feed rate | 10.59% |
| Riichi rate | 15.64% |
| Call rate | 34.89% |

For the next version I have a plan to improve win rate, probably bot should push with good hands more often.

### 0.3.2 version

Version with various improvements.

This version had played 600 games (hanchans) and achieved fourth dan (四段).

Rate was somewhere around R1700.

Stat:

|   | Result |
| --- | --- |
| Average position | 2.53 |
| Win rate | 19.97% |
| Feed rate | 10.88% |
| Riichi rate | 15.80% |
| Call rate | 36.39% |

| Places |  |
| --- | --- |
| First | 22.41% |
| Second | 25.52% |
| Third| 28.28% |
| Fourth | 23.79% |
| Bankruptcy | 4.48% |


# For developers

## How to run it?

1. `pip install -r requirements.txt`
2. Run `python main.py` it will connect to the tenhou.net and will play a game

## Configuration instructions

1. Put your own settings to the `project/settings_local.py` file. 
They will override settings from default `settings.py` file
2. Also you can override some default settings with command argument. 
Use `python main.py -h` to check all available commands

## Implement your own AI

https://github.com/MahjongRepository/tenhou-python-bot/wiki/Implement-AI

## Round reproducer

https://github.com/MahjongRepository/tenhou-python-bot/wiki/Round-reproducer

## Contribution to the project

All PRs are welcomed anytime. Currently the project is in early stage and 
I'm working on the different parts of it in the same time, so before making any 
big changes it's better to check with me to avoid code duplication.
