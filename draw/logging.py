from typing import Dict
from os import path, remove, makedirs
from pathlib import Path

from nonebot import get_driver

from .config import Config


global_config = get_driver().config
config = Config.parse_obj(global_config)
logs_path = config.log_file


def command_cut(msg: str):
    if msg[0] in {"(", ")", "（", "）"}:
        return ("outer", None)
    args = msg[4:].lstrip()
    ctype = ""
    _commands = (
        "log",
        "nn",
        "check",
        "close",
        "del",
    )
    for i in _commands:
        if i in args[:5]:
            ctype = i
            args = args.replace(i, "", 1)
    return (ctype, args.lstrip()) if ctype else ("text", msg)


class ChatLogger:
    def __init__(self, group_id, log_name) -> None:
        self.group_id = group_id
        self.log_name = log_name
        if not path.exists(path.join(logs_path, str(group_id))):
            makedirs(path.join(logs_path, str(group_id)))
        self.log_file = path.join(path.join(logs_path, str(group_id)), f"{log_name}.txt")
        self.characters: Dict[int, str] = {}

    def log_character(self, uid, name):
        self.characters[uid] = name
        return f"已为您创建角色：{name}"

    def log_start(self):
        if path.exists(self.log_file):
            ret = f"将继续记录：{self.log_name}"
        else:
            ret = f"已为您新建记录：{self.log_name}"
            # self.log = open(self.log_file, "a", encoding="utf-8")
        return ret

    def log_append(self, uid, text):
        context: str = f"{self.characters[uid]}:{text}\n"
        with open(self.log_file, "a", encoding="utf-8") as log:
            log.write(context)
        return None

    def log_close(self):
        # self.log.close()
        return f"已停止记录：{self.log_name}，请于 http://175.178.80.69/res/log.html?gid={self.group_id}&log={self.log_name} 查看"

    def check(self, gid, arg=None):
        if arg:
            if path.exists(path.join(path.join(logs_path, str(gid)), f"{arg}.txt")):
                return ("sg", f"请于 http://175.178.80.69/res/log.html?gid={gid}&log={arg} 查看记录")
            else:
                return ("sg", f"不存在名为{arg}的记录")
        else:
            group_dir = Path(logs_path) / str(gid)
            log_list = [f.stem for f in group_dir.iterdir() if f.suffix == ".txt"]
            ret = "本群记录有：\n" + "\n".join(log_list) + "\n"
            return ("ls", ret)

    def _legal_chat(msg):
        return False if msg[0] in ("(", ")", "（", "）") else True


def del_log(gid, log_name):
    try:
        remove(path.join(path.join(logs_path, str(gid)), f"{log_name}.txt"))
        return f"已移除记录{log_name}"
    except FileNotFoundError:
        return f"不存在名为{log_name}的记录"
