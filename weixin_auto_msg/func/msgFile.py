import re
import os

class MsgFile:


    def getOneMsg(self):
        result = None
        writeData = None
        basePath = os.path.split(os.path.realpath(__file__))[0]
        with open(basePath+"/onedaya", mode='r+', encoding='UTF-8') as file:
            data = file.readlines()
            for index,line in enumerate(data):
                val = re.search('(?<=G#).*',line)
                if val is None:
                    continue

                result = val.group(0)
                data[index] = data[index].replace("#FLAG#","")
                if (index+1) == len(data):
                    break

                data[index+1] = "#FLAG#" + data[index+1]
                writeData = data
                break

        if not writeData is None:
            with open(basePath+"/onedaya", mode='w', encoding='UTF-8') as file:
                file.writelines(writeData)
        return result
