import toml
import vk_api

CONFIG_PATH = 'resources/config.toml'
VK_LOGIN = 'vk_login'
VK_PASSWORD = 'vk_password'


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Config(metaclass=Singleton):
    def __init__(self):
        self.CONFIG = toml.load(CONFIG_PATH)

    def get(self):
        return self.CONFIG


class VkApi(metaclass=Singleton):
    VK_API = toml.load(CONFIG_PATH)

    def __init__(self):
        config = Config().get()

        vk_session = vk_api.VkApi(config[VK_LOGIN], config[VK_PASSWORD])
        vk_session.auth()

        self.VK_API = vk_session.get_api()

    def get(self):
        return self.VK_API


def get_config():
    return Config().get()


def get_vk_api():
    return VkApi().get()
