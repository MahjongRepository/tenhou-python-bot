[![Build Status](https://travis-ci.org/MahjongRepository/tenhou-python-bot.svg?branch=master)](https://travis-ci.org/MahjongRepository/tenhou-python-bot)

For now only **Python 3.5** is supported.

# What do we have here?

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

## Simple mahjong bot

For research purposes we built a simple bot to play riichi mahjong on tenhou.net server.

### 0.0.5 version

It can reach a tempai and call a riichi. It doesn't know about dora, yaku, defence and etc. 
Only about tempai and riichi so far.

This version had played 335 games (hanchans) and achieved only first dan on the tenhou.net so far
(and lost it later, and achieved it again...).

Rate was somewhere around R1350.

|   | Result |
| --- | --- |
| Average position | 2.78 |
| Win rate | 20.73% |
| Feed rate | 19.40% |
| Riichi rate| 36.17% |

So, even with the current simple logic it can play and win.

## Local runner for mahjong bots

It allows to run four copies of bots to play with each other and it collects 
different statistics for each copy of the bot.

It doesn't support 100% of mahjong rules, but we are working on it.

The main purpose of it to be able to run three old bots to play against a new copy of the bot. 
It will allow to determine was a new version improved or not.

To be able to run it you need to copy an old ai version to the `mahjong/ai/old_version.py` 
and run `bots_battle.py`.

# For developers

## How to run it?

1. Install [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
2. Install [Vagrant](https://www.vagrantup.com/downloads.html)
3. Run `vagrant up`. It will take a while, also it will ask your system root password to setup NFS
4. Run `vagrant ssh`
5. Run `python main.py` it will connect to the tenhou.net and will play a match. 
After the end of the match it will close connection to the server

## Configuration instructions

1. Put your own settings to the `project/settings_local.py` file. 
They will override settings from default `settings.py` file
2. Also you can override some default settings with command argument. 
Use `python main.py -h` to check all available commands

## Code checking

This command will check the code style: `flake8 --config=../.flake8`

## Contribution to the project

All PRs are welcomed anytime. Currently the project is in early stage and 
I'm working on the different parts of it in the same time, so before making any 
big changes it's better to check with me to avoid code duplication.