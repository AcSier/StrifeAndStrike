from pydantic import BaseSettings
from typing import List
from os import path


class Config(BaseSettings):
    command_start: List[str] = []
    log_file = path.abspath(path.join("C:/SharedData/logs/"))

    class Config:
        extra = "ignore"