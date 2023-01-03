import random
from sqlite3 import IntegrityError
from typing import List
from ast import literal_eval

from .explain import PropInfo, SkillInfo, TraitInfo, SceneInfo, AliasInfo, StatusInfo, Ambiguation


class DrawCard(object):
    def __init__(self, times=0):
        self.propcards: List[str] = []
        for card in PropInfo.select():
            self.propcards += [card.name] * card.quantity
        self.skills: List[str] = [skill.name for skill in SkillInfo.select()]
        self.scenes: List[str] = [scene.name for scene in SceneInfo.select()]
        self.times: int = times
        

    def redeck(self):
        self.__init__()
        return "牌堆已更新~"

    def draw_prop(self, times):
        out = []
        for i in range(times):
            if len(self.propcards) == 0:
                out.append("这是最后一张了哦")
                break
            else:                
                c = random.choice(self.propcards)
                self.propcards.remove(c)
                out.append(c + "\n")
        msg = str()
        for c in out:
            msg += c
        return msg

    def draw_skill(self, times):
        out = []
        for i in range(times):
            if len(self.skills) == 0:
                out.append("这是最后一张了哦")
                break
            else:
                c = random.choice(self.skills)
                self.skills.remove(c)
                out.append(c + "\n")
        msg = str()
        for c in out:
            msg += c
        return msg
    
    def draw_scene(self):
        return random.choice(self.scenes)

    def get_len(self):
        return "剩余道具卡%d张"%len(self.propcards)

    def get_explanation(self, arg):
        ali_point = AliasInfo.get_or_none(alias=arg)
        def get(cid):
            if cid // 1000 == 101:
                obj = PropInfo.get_by_id(cid)
                return "道具：{n}\n描述：{info}\n数量：{num}张".format(n=obj.name, info=obj.info, num=obj.quantity)
            elif cid // 1000 == 102:
                obj = SkillInfo.get_by_id(cid)
                return "技能：{n}\n描述：{info}\n冷却：{t}轮".format(n=obj.name, info=obj.info, t=obj.cd)
            elif cid // 1000 == 103:
                obj = TraitInfo.get_by_id(cid)
                return "特质：{n}\n角色：{o}\n描述：{info}".format(n=obj.name, o=obj.owner, info=obj.info)
            elif cid // 1000 == 104:
                obj = SceneInfo.get_by_id(cid)
                return "场景：{n}\n效果：{info}\n描述：{des}".format(n=obj.name, info=obj.info, des=obj.description)
            elif cid // 1000 == 105:
                obj = StatusInfo.get_by_id(cid)
                return "状态名称：{n}（{typ}状态效果）\n可叠加：{st}\n描述：{info}".format(n=obj.name, typ=obj.type, st=obj.stackability, info=obj.info)
        if ali_point is None:
            return "还没有找到解释哦~"
        else:
            cid = ali_point.to_id
            if cid // 1000 == 200:
                obj = Ambiguation.get_by_id(cid)
                msg = f"以下是名词“{arg}”的多个词条：\n"
                for c2id in obj.to_id.split():
                    msg += get(int(c2id)) + "\n————————\n"
                return msg
            else:
                return get(cid)

    def get_id(self, name):
        cid = AliasInfo.get_or_none(alias=name).to_id
        return f"该词条的id为：{cid}" if cid else "未找到id"


class Player:
    def __init__(self, player: str, oc: str, hp: int=0, attack: int=0, defense: int=0, mov: int=0):
        self.player = player
        self.oc = oc
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.mov = mov

    def change(self, attr:str, val:int, set: bool=False):
        if set:
            if attr == "hp":
                self.hp = val
            elif attr == "atk":
                self.attack = val
            elif attr == "def":
                self.defense = val
            elif attr == "mov":
                self.mov = val
        else:
            if attr == "hp":
                self.hp += val
            elif attr == "atk":
                self.attack += val
            elif attr == "def":
                self.defense += val
            elif attr == "mov":
                self.mov += val
            
    def check(self, arg=""):
        if arg == "":
            return f"{self.player}——{self.oc}\nhp:{self.hp}\tatk:{self.attack}\tdef:{self.defense}\tmov:{self.mov}"
        else:
            if arg == "hp":
                return self.hp
            elif arg == "atk":
                return self.attack
            elif arg == "def":
                return self.defense
            elif arg == "mov":
                return self.mov


def _return(n):
        if n == "Ambiguation":
            return Ambiguation
        elif n == "PropInfo":
            return PropInfo
        elif n == "SkillInfo":
            return SkillInfo
        elif n == "TraitInfo":
            return TraitInfo
        elif n == "SceneInfo":
            return SceneInfo
        elif n == "AliasInfo":
            return AliasInfo
        elif n == "StatusInfo":
            return StatusInfo


def update(cmd:str):
    cmd = cmd.split()
    try:
        try:
            _return(cmd[0]).insert(literal_eval(cmd[1])).execute()
        except IntegrityError:
            _return(cmd[0]).update(literal_eval(cmd[1])).execute()
        finally:
            return "执行成功"
    except Exception as E:
        return "执行失败\n[Error]:%s"%repr(E)


def delete(cmd:str):
    cmd = cmd.split()
    try:
        atTable = _return(cmd[0])
        if atTable == AliasInfo:
            atTable.delete().where(atTable.alias==cmd[1]).execute()
        else:
            atTable.delete_by_id(int(cmd[1]))
        return "执行成功"
    except Exception as E:
        return "执行失败\n[Error]:%s"%repr(E)
