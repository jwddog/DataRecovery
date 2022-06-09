import time

from Inode import Inode
from SuperBlock import SuperBlock
from Decoder import *
from Journal import *
from ReadJournal import *


class FileRecovery:


    def recoverFiles(self, diskName, transactions: list, deletedInodes: list, numToRecover, filePath):

        superBlock = SuperBlock(diskName)
        readJournal = ReadJournal(diskName)

        toRecover = deletedInodes[0:numToRecover]


        numRecovered = 0
        for deletedInode in toRecover:
            for transaction in transactions:
                
                journalBlockNum = transaction.journalBlockNum + 1

                breakFlag = False
                for dataBlock in transaction.dataBlocks:

                    if dataBlock[0] == deletedInode[0]:

                        iTableBlock = readJournal.readJournalBlock(journalBlockNum)
                        inode = Inode(diskName, deletedInode[1], superBlock, iTableBlock)

                        if inode.hasExtentTree:

                            numRecovered += 1

                            recoveredFile = open("%s/recoveredFile_%s" % (filePath, (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(deletedInode[2])) + f"_num_{numRecovered}")), "ab")

                            for entry in inode.entries:
                                disk = open(diskName, "rb")
                                disk.seek(superBlock.blockSize * entry.blockNum)

                                for i in range(0, entry.numBlocks):
                                    recoveredFile.write(disk.read(superBlock.blockSize))

                            breakFlag = True
                            break

                    journalBlockNum += 1

                if breakFlag:
                    break

        return numRecovered

    def getDeletedInodes(self, diskName, transactions: list):

        superBlock = SuperBlock(diskName)
        readJournal = ReadJournal(diskName)

        deletionTransactions: list[Transaction] = []

        for transaction in transactions:
            if transaction.transactionType == 0:
                deletionTransactions.append(transaction)

        deletedInodes: list = []

        for transaction in deletionTransactions:

            blockBuffer = 1
            for block in transaction.dataBlocks:

                if block[1] == "iTableBlock":
                    blockData = readJournal.readJournalBlock(transaction.journalBlockNum + blockBuffer)

                    for inode in self.readInodeTableBlock(blockData, block[0], superBlock):
                        if transaction.commitTime - inode[2] < 12:
                            deletedInodes.append(inode)

                blockBuffer += 1

        deletedInodes.sort(key=lambda inode: -inode[2])

        return deletedInodes


    def readInodeTableBlock(self, block: bytes, blockNum, superBlock: SuperBlock):

        deletedInodes: list = []

        numInodesInBlock = floor(superBlock.blockSize / superBlock.inodeSize)

        for inodeNum in range(0, numInodesInBlock):

            inode = Inode(False, inodeNum, superBlock, block)

            if inode.deletionTime > 0 and not inode.hasExtentTree:
                # each deleted inode is represented as a tuple(inode table block num, inode number within the table block starting at 0, inode deletion time)
                deletedInodes.append((blockNum, inodeNum, inode.deletionTime))

        return deletedInodes
        
