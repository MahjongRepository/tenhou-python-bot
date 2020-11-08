import importlib


class SettingsSingleton:
    """
    Let's load a settings in the memory one time when the app starts
    Than override some settings with command arguments
    After this we not should change the object
    """

    instance = None

    def __init__(self):
        if not SettingsSingleton.instance:
            SettingsSingleton.instance = Settings()

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def __setattr__(self, key, value):
        return setattr(self.instance, key, value)


class Settings:
    def __init__(self):
        mod = importlib.import_module("settings.base")

        for setting in dir(mod):
            setting_value = getattr(mod, setting)
            setattr(self, setting, setting_value)


settings = SettingsSingleton()
