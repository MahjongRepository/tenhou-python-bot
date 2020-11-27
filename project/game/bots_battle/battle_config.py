from game.ai.configs.bot5 import MikiConfig
from game.ai.configs.bot6 import ChioriConfig
from game.ai.configs.bot7 import KanaConfig
from game.ai.configs.bot8 import MaiConfig
from game.ai.configs.bot9 import YuiConfig
from game.ai.configs.bot10 import NadeshikoConfig
from game.ai.configs.bot11 import RiuConfig
from game.ai.configs.bot12 import KeikumusumeConfig
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
        MikiConfig,
        ChioriConfig,
        KanaConfig,
        MaiConfig,
        YuiConfig,
        NadeshikoConfig,
        RiuConfig,
        KeikumusumeConfig,
    ]
