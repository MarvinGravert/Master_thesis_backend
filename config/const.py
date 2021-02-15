from decouple import config
from config.api_types import Example


TEST = config("TEST", cast=int, default=10)
DAY = config("DAY", cast=Example, default=Example.DAY_7)
