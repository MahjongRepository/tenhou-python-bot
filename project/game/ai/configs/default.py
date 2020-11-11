from game.ai.placement import PlacementHandler


class BotDefaultConfig:
    # all features that we are testing should starts with FEATURE_ prefix
    # with that it will be easier to track these flags usage over the code
    FEATURE_DEFENCE_ENABLED = True

    placement_handler_class = PlacementHandler

    # TODO move all separate configs as subclasses here
