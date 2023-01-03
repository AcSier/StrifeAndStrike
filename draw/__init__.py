from os import remove
from typing import Tuple, Dict
import time
from dataclasses import dataclass

from nonebot import get_driver, on_startswith, get_bot, on_message
from nonebot.rule import Rule
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER
from nonebot.typing import T_State
from nonebot.params import State, EventPlainText
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, GroupMessageEvent

from .draw_refactor import DrawCard, Player, update, delete
from .logging import ChatLogger, del_log, command_cut
from .dealer import arg_cutter
from .config import Config


__help__ = r"""以下是Strife&Strike的指令帮助
-本插件服务于桌游SnS
-可用指令有抽卡、抽技能、抽场景、重置牌堆、剩余卡牌、查询信息、新建角色、设置属性、删除角色、场记
-使用 sns help/帮助 <指令名称>查看细则"""
__exp__ = {
"hpr": r"""抽取一定数量道具卡
可用指令：抽卡、道具卡、card、propcard、hpr、pr(明牌)等
参数：<抽取张数> [是否明牌(b)]
用例：sns抽卡2b -> 明牌抽取两张道具卡""",
"hsk": r"""抽取一定数量技能卡
可用指令：技能、抽技能、技能卡、skill、hsk、sk(明牌)
参数：<抽取张数> [是否明牌(b)]
用例：sns技能2 -> 暗抽两张技能卡""",
"sc": r"""随机抽取一个场景
可用指令：抽场景、场景、scene、sc""",
"re": r"""重置群内牌堆
可用指令：重置牌堆、重置、刷新、reload、re""",
"rs": r"""查询群内牌堆剩余道具卡张数
可用指令：剩余卡牌、剩余、查看剩余、牌堆、rest、rs""",
"ser": r"""查询卡牌/场景/特质的信息
可用指令：查询解释、查、search、ser等
参数：<道具卡名称|技能名称|场景名称|特质名称|角色名称>
用例：sns 查 Data""",
"set": r"""用于新建场记角色（注意：该角色为通用角色，即不和群聊绑定，但会和玩家名绑定)
可用指令：新建角色、选角色、角色、player、newplayer
参数：<玩家名> <角色名> <hp> <atk> <def> <mov>
用例：snsset pl oc 1000 75 50 3""",
"upd": r"""用于场记时修改玩家属性
可用指令：设置属性、修改、更新、update、upd
参数：[设置模式(set)] <玩家名> <属性名> <增减值|更新值>
用例一：snsupd set pl hp 500 -> 设置玩家<pl>的hp到500
用例二：sns upd pl hp -50 -> 将玩家<pl>的hp减少50点""",
"del": r"""删除一个存在的场记角色
可用指令：删除角色、删除、delete、del、drop
参数：<玩家名>
用例：sns del pl -> 删除玩家<pl>""",
"chk": r"""用于查询游戏过程中玩家的数值
可用指令：场记、查看属性、属性、记、show、check、chk
参数：[玩家名]
用例一：sns场记 -> 查询所有玩家的属性
用例二：snsshow pl -> 查询玩家<pl>的属性"""
}


global_config = get_driver().config
config = Config.parse_obj(global_config)

@dataclass
class Options:
    decked: bool = False

decks: Dict[str, DrawCard] = {}
TempDeck = DrawCard()
decks["temp"] = TempDeck
players: Dict[str, Player] = {}

def _get_gid(event: MessageEvent):
        return (
            f"group_{event.group_id}"
            if isinstance(event, GroupMessageEvent)
            else "temp"
        )

def _deck_exist(event: MessageEvent) -> bool:
    cid = _get_gid(event)
    return bool(decks.get(cid, None))


deal = on_startswith({"sns", "SNS", "Sns"}, priority=10)


@deal.handle()
async def _(event: MessageEvent):
    _is_group_message = True if type(event) is GroupMessageEvent else False
    args = arg_cutter(str(event.get_message()))
    await _handle(_is_group_message, args, event)
    

async def _handle(state: bool, args: Tuple, event: MessageEvent) -> Tuple[bool, str]:
    # await bot.send_private_msg(user_id=event.user_id, message=".")
    gid = _get_gid(event=event)
    self_id = event.self_id
    bot = get_bot(str(self_id))
    assert isinstance(bot, Bot)
    async def send(msg):
        tuple(msg)
        if msg[0] is False:
            await bot.send_private_msg(user_id=event.user_id, message=msg[1])
        elif msg[0] is True and type(event) is GroupMessageEvent:
            await bot.send_group_msg(group_id=event.group_id, message=msg[1])
    

    def _help(state, args):
        if len(args) == 1:
            return state, __help__
        else:
            try:
                return state, __exp__[args[1]]
            except KeyError:
                return state, "未找到该词条~"


    try:
        deck = decks[gid]
    except KeyError:
        deck = decks["temp"]


    def _new(event):
        if _deck_exist(event=event):
            return state, "牌堆已存在"
        else:
            gid = _get_gid(event=event)
            deck = DrawCard()
            decks[gid] = deck
            return state, "已创建牌堆"

    def _del(event):
        if not _deck_exist(event=event):
            return state, "牌堆不存在"
        else:
            decks.pop(_get_gid(event=event))
            return state, "已清除牌堆"

    def _card(args, bright=False):
        for arg in args:
            try:
                times = int(arg)
            except ValueError:
                pass
        if "b" in args: bright = True
        msg = deck.draw_prop(times=times)
        return bright, msg

    def _skill(args, bright=False):
        for arg in args:
            try:
                times = int(arg)
            except ValueError:
                continue
        if "b" in args: bright = True
        msg = deck.draw_skill(times=times)
        return bright, msg

    def _scene(state):
        msg = deck.draw_scene()
        return state, msg

    def _reload():
        msg = deck.redeck()
        return True, msg

    def _rest(state):
        msg = deck.get_len()
        return state, msg

    def _search(state, args):
        msg = deck.get_explanation(arg=args[1])
        return state, msg

    def _new_player(args):
        if len(args) != 7:
            return True, f"缺少{7-len(args)}个属性哦~"
        else:
            try:
                player_name = args[1]
                player = Player(player_name, args[2], int(args[3]), int(args[4]), int(args[5]), int(args[6]))
                players[player_name] = player
                return True, f"成功创建~\n{player.check()}"
            except ValueError:
                return True, "参数不对哦~"

    def _check(state, args):
        if len(args) == 1:
            attrs = ""
            if len(players) == 0:
                return state, "目前还没有战斗哦~"
            for pln, pl in players.items():
                attrs += pl.check() + "\n"
            return state, attrs
        else:
            try:
                player = players[args[1]]
                return state, f"{player.check()}"
            except:
                return state, "查无此人~"

    def _update(state, args):
        if not "set" in args:
            player = players[args[1]]
            attr = args[2]
            pre_ = player.check(attr)
            player.change(args[2], int(args[3]))
        else:
            player = players[args[2]]
            attr = args[3]
            pre_ = player.check(attr)
            player.change(args[3], args[4], set=True)
        aft_ = player.check(attr)
        return True, f"属性已更新~\n{attr}:{pre_} -> {aft_}"

    def _del_player(args):
        player = players[args[1]]
        oc = player.oc
        players.pop(args[1])
        return True, f"已删除角色 {args[1]}——{oc}"

    def _id(state, args):
        msg = deck.get_id(args[1])
        return state, msg

    cmd = args[0]
    if cmd != "Err":
        if state is False and cmd not in ["sc", "ser", "chk"]:
                await send(tuple([False, "该指令不支持私聊哦"]))
        elif not _deck_exist(event=event):
            gid = _get_gid(event=event)
            deck = DrawCard()
            decks[gid] = deck
            deck = decks[gid]
            msg = tuple([True, "初始化中~"])
            await send(msg)
        if cmd == "hpr":
            msg = _card(args)
        elif cmd == "hsk":
            msg = _skill(args)
        elif cmd == "sc":
            msg = _scene(state)
        elif cmd == "re":
            msg = _reload()
        elif cmd == "ser":
            msg = _search(state, args)
        elif cmd == "upd":
            msg = _update(state, args)
        elif cmd == "chk":
            msg = _check(state, args)
        elif cmd == "del":
            msg = _del_player(args)
        elif cmd == "pr":
            msg = _card(args, bright=True)
        elif cmd == "sk":
            msg = _skill(args, bright=True)
        elif cmd == "rs":
            msg = _rest(state)
        elif cmd == "set":
            msg = _new_player(args)
        elif cmd == "hlp":
            msg = _help(state, args)
        elif cmd == "new":
            msg = _new(event)
        elif cmd == "de":
            msg = _del(event)
        elif cmd == "id":
            msg == _id(state, args)
        await send(msg)


superdeal = on_startswith("snsu", priority=8, permission=SUPERUSER)

@superdeal.handle()
async def _(event:MessageEvent):
    cmd = str(event.get_message())[5:]
    msg = update(cmd)
    await superdeal.finish(message=msg)


superdel = on_startswith("snsd", priority=8, permission=SUPERUSER)

@superdel.handle()
async def _(event:MessageEvent):
    cmd = str(event.get_message())[5:]
    msg = delete(cmd)
    await superdeal.finish(message=msg)


# --Logger--
logger = on_startswith({"trpg", "Trpg", "TRPG"}, priority=8)
log_group = set()
log_object: Dict[int, ChatLogger] = {}
group_nick: Dict[int, Dict[int, str]] = {}


log_object[000000000] = ChatLogger(000000000, "default")


def is_logging(event: GroupMessageEvent) -> bool:
    return True if int(event.group_id) in log_group else False

def get_input(arg: str = EventPlainText()) -> bool:
    if len(arg) > 0:
        if arg[0] not in {"(", ")", "（", "）"}:
            return True
    return False

word_matcher = on_message(Rule(is_logging) & get_input, block=True, priority=12)

@logger.handle()
async def _(event: GroupMessageEvent, arg: str = EventPlainText()):
    await _log_handle(event, arg)

@word_matcher.handle()
async def _(event: GroupMessageEvent, arg: str = EventPlainText()):
    await _log_handle(event, arg)

async def _log_handle(event: GroupMessageEvent, args):
    gid = int(event.group_id)
    uid = int(event.user_id)
    self_id = event.self_id
    bot = get_bot(str(self_id))
    assert isinstance(bot, Bot)
    async def send(msg):
        if msg:
            await bot.send_group_msg(group_id=gid, message=msg)
        else:
            pass

    logs: ChatLogger = log_object.get(gid, log_object[000000000])

    def _new(gid, arg, logs: ChatLogger=logs):
        if gid in log_group:
            return "群聊中有正在进行的记录哦"
        else:
            log_group.add(gid)
            if not logs or logs.log_name == "default":
                if not arg:
                    arg = time.strftime("%Y%m%d_%H%M%S", time.localtime())
                logs = ChatLogger(gid, arg)
                log_object[gid] = logs
                logs: ChatLogger = log_object.get(gid)
            if arg != logs.log_name:
                logs = ChatLogger(gid, arg)
                log_object[gid] = logs
                logs: ChatLogger = log_object.get(gid)
            return logs.log_start()

    def _append(uid, arg, logs: ChatLogger=logs):
        if is_logging(event):
            name = group_nick[gid].get(uid)
            if not name:
                return "您还未创建角色哦"
            logs.log_append(uid, arg)
        return None
        
    def _close(logs=logs):
        if not gid in log_group:
            return "群聊中没有正在进行的记录哦"
        else:
            log_group.remove(gid)
            return logs.log_close()

    def _check(arg=None, logs=logs):
        if not logs:
            return "本群暂无记录"
        msg = logs.check(gid, arg)
        return msg[1] + f"最近的一次记录：http://175.178.80.69/res/log.html?gid={gid}&log={logs.log_name}" if msg[0] == "ls" else msg[1]

    def _remove(gid, arg, logs=logs):
        return del_log(gid, arg)

    def _nn(uid, arg=None, logs=logs):
        if not group_nick.get(gid):
            group_nick[gid] = {}
        group_nick[gid][uid] = arg
        return logs.log_character(uid, arg)

    arg = command_cut(args)
    if arg[0] != "outer":
        if arg[0] == "log":
            msg = _new(gid, arg[1])
        elif arg[0] == "close":
            msg = _close()
        elif arg[0] == "nn":
            msg = _nn(uid, arg[1])
        elif arg[0] == "text":
            msg = _append(uid, arg[1])
        elif arg[0] == "check":
            msg = _check(arg[1])
        elif arg[0] == "del":
            msg = _remove(gid, arg[1])
        await send(msg)