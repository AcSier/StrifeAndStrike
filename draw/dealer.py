import re
from .config import Config
from nonebot import get_driver


global_config = get_driver().config
config = Config.parse_obj(global_config)
command_start = {"sns", "Sns", "SNS"}


def arg_cutter(arg: str) -> list:
    output = []
    arg = arg[3:]
    output += re.findall(r"([\u4e00-\u9fa5]+|[a-zA-Z]+|-?\d+)", arg)
    _commands = {
        "抽卡": "hpr",
        "card": "hpr",
        "propcard": "hpr",
        "卡": "hpr",
        "道具卡": "hpr",
        "技能": "hsk",
        "skill": "hsk",
        "抽技能": "hsk",
        "技能卡": "hsk",
        "抽场景": "sc",
        "场景": "sc",
        "场景卡": "sc",
        "scene": "sc",
        "重置": "re",
        "重置牌堆": "re",
        "牌堆重置": "re",
        "reload": "re",
        "刷新": "re",
        "明牌": "pr",
        "明牌抽卡": "pr",
        "明抽卡": "pr",
        "明牌技能": "sk",
        "明牌技能卡": "sk",
        "明牌抽技能": "sk",
        "明抽技能": "sk",
        "查看剩余卡牌": "rs",
        "查看剩余": "rs",
        "剩余卡牌": "rs",
        "剩余": "rs",
        "牌堆": "rs",
        "rest": "rs",
        "新建牌堆": "new",
        "创建牌堆": "new",
        "获取牌堆": "new",
        "移除牌堆": "de",
        "删除牌堆": "de",
        "查询解释": "ser",
        "查": "ser",
        "查询卡牌": "ser",
        "查询道具卡": "ser",
        "查询技能": "ser",
        "查询特质": "ser",
        "查询场景": "ser",
        "search": "ser",
        "选角色": "set",
        "新建角色": "set",
        "角色": "set",
        "newplayer": "set",
        "player": "set",
        "设置属性": "upd",
        "修改": "upd",
        "更新": "upd",
        "改": "upd",
        "update": "upd",
        "场记": "chk",
        "记": "chk",
        "show": "chk",
        "check": "chk",
        "查看属性": "chk",
        "属性": "chk",
        "删除角色": "del",
        "删除": "del",
        "delete": "del",
        "delplayer": "del",
        "drop": "del",
        "help": "hlp",
        "帮助": "hlp",
        "Help": "hlp"
        }
    for k, v in _commands.items():
        if k in output:
            output[output.index(k)] = v
    if re.match(r'[a-z]{2,3}', output[0]) is None:
        output.insert(0, "Err")
    return tuple(output)
