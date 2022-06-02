
from ReadJournal import *
from ExtentNode import *
from fileRecovery import *


fileRecovery = FileRecovery()

diskName = input("File path of disk: ")
readJournal = ReadJournal(diskName)


transactions = readJournal.readFileSystemJournal()
deletedInodes = fileRecovery.getDeletedInodes(diskName, transactions)

numDeleted = len(deletedInodes)


userChoice = input("%d deleted files found. Enter Y to recover all, and an integer N (1 to %d) to recover the N most recently deleted files: " % (numDeleted, numDeleted))

numToRecover = 0
if userChoice.upper() == "Y":
    numToRecover = numDeleted

elif int(userChoice) <= numDeleted and int(userChoice) > 0:
    numToRecover = int(userChoice)

filePath = input("please provide a file path for recovered files: ")

numRecovered = fileRecovery.recoverFiles(diskName, transactions, deletedInodes, numToRecover, filePath)

print("%d files were successfully recovered" % numRecovered)