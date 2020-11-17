"""
The package contains steps to reproduce real game situations and the
result that we want to have after bot turn.

It will help us to be sure that new changes in logic don't change
the old fixed bugs with decisions.

Also, this package contains tools to generate documentation and unit tests
from the description of the situations.
"""

ACTION_DISCARD = 'discard'

SYSTEM_TESTING_CASES = [
    {
        'index': 1,
        'description': 'Bot discarded 2s by suji because of 2 additional ukeire in ryanshanten, instead of discarding the safe tile.',
        'reproducer_command': 'python reproducer.py --log 2020102200gm-0001-7994-1143916f --player 0 --wind 2 --honba 3 --tile=1s --n 2 --action=draw',
        'action': ACTION_DISCARD,
        'allowed_discards': ['3s', '5s']
    }
]
