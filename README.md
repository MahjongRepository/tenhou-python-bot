[![Build Status](https://travis-ci.org/MahjongRepository/tenhou-python-bot.svg?branch=master)](https://travis-ci.org/MahjongRepository/tenhou-python-bot)

# What is it?

This is simple bot for the popular riichi mahjong server tenhou.net.

For now only **Python 3** is supported.

# How to run it?

1. Install [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
2. Install [Vagrant](https://www.vagrantup.com/downloads.html)
3. Run `vagrant up`. It will take a while, also it will ask your system root password to setup NFS
4. Run `vagrant ssh`
5. Run `python main.py` it will connect to the tenhou.net and will play a match. After the end of match it will close connection to the server
