from game.ai.configs.bot_ichihime import IchihimeConfig
from game.ai.configs.bot_kaavi import KaaviConfig
from game.ai.configs.bot_wanjirou import WanjirouConfig
from game.ai.configs.bot_xenia import XeniaConfig


class BattleConfig:
    CLIENTS_CONFIGS = [
        IchihimeConfig,
        KaaviConfig,
        WanjirouConfig,
        XeniaConfig,
    ]

    SEEDS = []
    # seeds that we used for performance tweaks testing
    # SEEDS = [0.42673535201335355, 0.09835276455730657, 0.27391557585866877]
