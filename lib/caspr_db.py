# Database relations library for the CASPR project.
import peewee
from peewee import *

#---- Base SQL connections ----
db = MySQLDatabase('CASPR_database', user='root', password='boj75302816')

class BaseModel(Model):
	class Meta:
		database = db


#---- Table definitions ----
class Person(BaseModel):
	PersonID = PrimaryKeyField()
	ID_NUM = BlobField()
	ImagePath = CharField()
	Banned = BooleanField()
	CreatedAt = DateTimeField()
	FirstName = CharField()
	LastName = CharField()
	class Meta:
		db_table='Person'

class Log(BaseModel):
	LogID = PrimaryKeyField()
	PersonID = ForeignKeyField(Person,
		db_column='PersonID',
		to_field='PersonID')
	LoggedAt = DateTimeField()
	class Meta:
		db_table='Log'


#---- Person table methods ----
def getPersonById(ID):
	try:
		return Person.get(Person.PersonID == ID)
	except Exception as e:
		print str(e)
		return None

def getPersonByID_NUM(ID_NUM):
	try:
		return Person.get(Person.ID_NUM == ID_NUM)
	except Exception as e:
		print str(e)
		return None

def postPerson(ID_NUM, ImagePath, Banned, FirstName, LastName):
	try:
		person = Person(
			ID_NUM=ID_NUM,
			ImagePath=ImagePath,
			Banned=Banned,
			FirstName=FirstName,
			LastName=LastName)
		person.save()
		print "CDB: New person record created successfully."
	except Exception as e:
		print str(e)

#---- Log table methods ----
def getLogsByPersonID(ID):
	try:
		query = Log.select().where(Log.PersonID == ID)
		return list(query)
	except Exception as e:
		print str(e)
		return None

def postLog(personID):
	try:
		log = Log(PersonID=personID)
		log.save()
		print "CDB: New log record created successfully."
	except Exception as e:
		print str(e)