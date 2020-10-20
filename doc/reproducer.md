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

Sometimes we had to debug `bot <-> server` communication. For this purpose we built this reproducer.

Just use it with already played game:

```
python reproducer.py -l d6a5e_2017-04-13\ 09_54_01.log
```

It will send to the bot all commands that were send from tenhou in real game.