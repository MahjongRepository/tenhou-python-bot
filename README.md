[![Build Status](https://travis-ci.org/MahjongRepository/tenhou-python-bot.svg?branch=master)](https://travis-ci.org/MahjongRepository/tenhou-python-bot)

For now only **Python 3.5+** is supported.

# What do we have here?

![Example of bot game](https://cloud.githubusercontent.com/assets/475367/25059936/31b33ac2-21c3-11e7-8cb2-de33d7ba96cb.gif)

## Mahjong hands calculation

We have a code which can calculate hand cost (han, fu, yaku and scores) based on the hand's tiles.

It supports features like:

- Disable\enable aka dora in the hand
- Disable\enable open tanyao yaku
- By now it supports double yakumans (Dai Suushii, Daburu Kokushi musou, Suu ankou tanki, 
Daburu Chuuren Poutou). Later I plan to have a disabling option in settings for it.

The code was validated on tenhou.net phoenix replays in total on **8'527'296 hands**, and 
results were the same in 100% cases.

So, we can say that our own hand calculator works the same way that tenhou.net hand calculation.

The example of usage you can find here: https://github.com/MahjongRepository/tenhou-python-bot/blob/master/project/validate_hand.py#L194

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

# For developers

## How to run it?

Run `pythone main.py` it will connect to the tenhou.net and will play a match. 
After the end of the match it will close connection to the server

## Configuration instructions

1. Put your own settings to the `project/settings_local.py` file. 
They will override settings from default `settings.py` file
2. Also you can override some default settings with command argument. 
Use `python main.py -h` to check all available commands

## Round reproducer

We built the way to reproduce already played round. 
This is really helpful when you want to reproduce table state and fix bot bad behaviour.

There are two options to do it.

### Reproduce from tenhou log link

First you need to do dry run of the reproducer with command:

```
python reproducer.py -o "http://tenhou.net/0/?log=2017041516gm-0089-0000-23b4752d&tw=3&ts=2" -d
```

It will print all available tags in the round. For example we want to stop before 
discard tile to other player ron, in given example we had to chose `<W59/>` tag as a stop tag.

Next command will be:

```
python reproducer.py -o "http://tenhou.net/0/?log=2017041516gm-0089-0000-23b4752d&tw=3&ts=2" -t "<W59/>"
```

And output:

```
Hand: 268m28p23456677s + 6p
Discard: 2m
```

After this you can debug bot decisions.

### Reproduce from our log

Sometimes we had to debug bot <-> server communication. For this purpose we built this reproducer.

Just use it with already played game:

```
python reproducer.py -l d6a5e_2017-04-13\ 09_54_01.log
```

It will send to the bot all commands that were send from tenhou in real game.

## Code checking

This command will check the code style: `flake8 --config=../.flake8`

## Contribution to the project

All PRs are welcomed anytime. Currently the project is in early stage and 
I'm working on the different parts of it in the same time, so before making any 
big changes it's better to check with me to avoid code duplication.
