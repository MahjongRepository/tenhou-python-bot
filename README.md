![Mahjong bot](https://github.com/MahjongRepository/tenhou-python-bot/workflows/Mahjong%20bot/badge.svg)

Bot was tested with Python 3.5. With Python 2 it is not working.

# What do we have here?

![Example of bot game](https://cloud.githubusercontent.com/assets/475367/25059936/31b33ac2-21c3-11e7-8cb2-de33d7ba96cb.gif)

## Mahjong hands calculation

You can find it here: https://github.com/MahjongRepository/mahjong

## Mahjong bot

For research purposes we built a simple bot to play riichi mahjong on tenhou.net server.

Here you can read about bot strength: https://github.com/MahjongRepository/tenhou-python-bot/wiki/Bot-versions

# For developers

## How to run it?

1. `pip install -r requirements/dev.txt`
2. Run `cd project && python main.py` it will connect to the tenhou.net and will play a game

## Configuration instructions

1. Put your own settings to the `project/settings_local.py` file. 
They will override settings from default `settings.py` file.
2. Also, you can override some default settings with command arguments. 
Use `python main.py -h` to check all available commands.

## Round reproducer

It can be useful to debug bot crash or strange discards: https://github.com/MahjongRepository/tenhou-python-bot/wiki/Round-reproducer

## Contribution to the project

All PRs are welcomed anytime. Currently the project is in early stage and 
I'm working on the different parts of it in the same time, so before making any 
big changes it's better to check with me to avoid code duplication.
