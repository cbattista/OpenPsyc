import sys

sys.path.append('/home/cogdev/code/OpenPsyc/')

from mongoTools import ReadTable

try:
	number = sys.argv[1]
except:
	sys.stderr("You need to specify a participant ID")

fileName = "pre/070505_%s*.csv" % number
dbName = "CAT2"
tableName = "production_pre"

reader = ReadTable(fileName = fileName, dbName=dbName, tableName = tableName, clear=True)
