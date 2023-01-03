from os import makedirs, path
import peewee as pw
from ._RHelper import RHelper

root = RHelper()
makedirs(root.database, exist_ok=True)
db = pw.SqliteDatabase(root.database / ("sns_data.db"))


class PropInfo(pw.Model):
    id = pw.IntegerField(primary_key=True)
    name = pw.CharField()
    info = pw.CharField()
    quantity = pw.IntegerField()

    class Meta:
        database = db
        


class SkillInfo(pw.Model):
    id = pw.IntegerField(primary_key=True)
    name = pw.CharField()
    info = pw.CharField()
    cd = pw.IntegerField()

    class Meta:
        database = db


class SceneInfo(pw.Model):
    id = pw.IntegerField(primary_key=True)
    name = pw.CharField()
    info = pw.CharField()
    description = pw.CharField()

    class Meta:
        database = db


class TraitInfo(pw.Model):
    id = pw.IntegerField(primary_key=True)
    name = pw.CharField()
    owner = pw.CharField()
    info = pw.CharField()

    class Meta:
        database = db

    
class StatusInfo(pw.Model):
    id = pw.IntegerField(primary_key=True)
    name = pw.CharField()
    info = pw.CharField()
    stackability = pw.CharField()
    type = pw.CharField()

    class Meta:
        database = db


class AliasInfo(pw.Model):
    alias = pw.CharField()
    to_id = pw.IntegerField()

    class Meta:
        database = db


class Ambiguation(pw.Model):
    id = pw.IntegerField(primary_key=True)
    to_id = pw.CharField()

    class Meta:
        database = db


if not path.exists(root.database / ("sns_data.db")):
    db.connect()
    db.create_tables([PropInfo])
    db.create_tables([SkillInfo])
    db.create_tables([SceneInfo])
    db.create_tables([TraitInfo])
    db.create_tables([AliasInfo])
    db.create_tables([StatusInfo])
    db.create_tables([Ambiguation])
    db.close()
else:
    db.connect()
    if "propinfo" not in db.get_tables():
        db.create_tables([PropInfo])
    if "skillinfo" not in db.get_tables():
        db.create_tables([SkillInfo])
    if "sceneinfo" not in db.get_tables():
        db.create_tables([SceneInfo])
    if "traitinfo" not in db.get_tables():
        db.create_tables([TraitInfo])
    if "aliasinfo" not in db.get_tables():
        db.create_tables([AliasInfo])
    if "statusinfo" not in db.get_tables():
        db.create_tables([StatusInfo])
    if "ambiguatiom" not in db.get_tables():
        db.create_tables([Ambiguation])
    db.close()