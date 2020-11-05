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
