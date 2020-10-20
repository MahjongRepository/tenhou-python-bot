# Game reproducer

We built the way to reproduce already played round. 

This is really helpful when you want to reproduce table state and fix bot incorrect behaviour.

There are two options to do it.

## Getting game meta information

It will be easier to find the round number to reproduce if you check the game meta-information first:

Command:
```bash
python reproducer.py --log 2020102008gm-0001-7994-9438a8f4 --meta
```

Output:
```json
{
  "players": [
    {
      "seat": 0,
      "name": "Wanjirou",
      "rank": "新人"
    },
    {
      "seat": 1,
      "name": "Kaavi",
      "rank": "新人"
    },
    {
      "seat": 2,
      "name": "Xenia",
      "rank": "新人"
    },
    {
      "seat": 3,
      "name": "Ichihime",
      "rank": "新人"
    }
  ],
  "game_rounds": [
    {
      "wind": 0,
      "honba": 0,
      "round_start_scores": [
        250,
        250,
        250,
        250
      ]
    },
    {
      "wind": 1,
      "honba": 1,
      "round_start_scores": [
        235,
        235,
        265,
        265
      ]
    },
    {
      "wind": 1,
      "honba": 2,
      "round_start_scores": [
        221,
        277,
        251,
        251
      ]
    },
    {
      "wind": 1,
      "honba": 3,
      "round_start_scores": [
        221,
        298,
        230,
        251
      ]
    },
    {
      "wind": 2,
      "honba": 0,
      "round_start_scores": [
        320,
        255,
        197,
        228
      ]
    },
    {
      "wind": 3,
      "honba": 0,
      "round_start_scores": [
        290,
        215,
        137,
        358
      ]
    }
  ]
}
```

From this information player seat and wind number could be useful for the next command run.

## Running the reproducing for the game

To reproduce game situation you need to know:
- log id
- player seat number or player nickname
- wind number (1-4 for east, 5-8 for south, 9-12 for west)
- honba number
- tile where to stop the game
- action

There are two supported actions for the reproducer:
- `draw`. Sought tile will be added to the hand, then method `discard_tile()` will be called and after that reproducer will stop.
- `enemy_discard`. After enemy discard method `try_to_call_meld()` will be called (if possible) and after that reproducer will stop.

## Examples of usage

```bash
python reproducer.py --log 2020102008gm-0001-7994-9438a8f4 --player Wanjirou --wind 3 --honba 0 --tile 7p --action enemy_discard
```

```bash
python reproducer.py --log 2020102009gm-0001-7994-5e2f46c0 --player Kaavi --wind 3 --honba 1 --tile 5m --action draw
```

