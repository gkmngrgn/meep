from pathlib import Path
from typing import Final

from appdirs import user_config_dir

APP_NAME: Final = "meep"
CONFIG_DIR: Final = Path(user_config_dir(appname=APP_NAME))
DB_PATH: Final = CONFIG_DIR / f"{APP_NAME}.db"
