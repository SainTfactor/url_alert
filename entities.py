from peewee import *
import datetime


db = SqliteDatabase('entity.db')

class BaseModel(Model):
    class Meta:
        database = db

class Task(BaseModel):
    name = CharField()
    search_term = CharField()
    urls = CharField()
    target_email = CharField()
    last_triggered = DateTimeField(null=True)

# Create Tables
#db.connect()
#db.create_tables([Task])

def create_task(name, search_term, urls, target_email):
    task = Task(
        name = name, 
        search_term = search_term, 
        urls = urls, 
        target_email = target_email
      )
    task.save()

def remove_task(name):
    return Task.delete().where(Task.name == name).execute()
    
def get_task(name):
    return Task.get(Task.name == name)
    