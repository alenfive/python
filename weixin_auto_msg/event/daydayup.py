
import requests
import threading
import io
import base64
import xml.etree.ElementTree as Etree
import json
import shutil
import time
from datetime import datetime, timedelta


class TimerSendMsg(threading.Thread):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36"}
    session = None

    def __init__(self, session):
        threading.Thread.__init__(self)
        self.session = session

    def run(self):
        msgcore = MsgCore(self.session)
        while True:
            curTime = datetime.now()
            desTime = curTime.replace(hour=5, minute=20, second=0, microsecond=0)
            delta = curTime - desTime
            if abs(delta.total_seconds()) < 60*10:
                msgcore.sendmsg(Webwxinit.jsonData['User'], msgcore.finduserByNickname("郑小小"), "早起的虫子开始吃鸟了")
                time.sleep(60*10*2)
                continue

            time.sleep(60)

class SyncCheckThread(threading.Thread):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36"}
    session = None

    def __init__(self, session):
        threading.Thread.__init__(self)
        self.session = session

    def run(self):
        print("start sync check ...")
        #https: // webpush.wx2.qq.com / cgi - bin / mmwebwx - bin / synccheck?r = 1471491463975 & skey = % 40
        #crypt_fd882096_c470f01075e20985876407f1b2d0f441 & sid = IJOXOVSUgZtM1RRA & uin = 2947382904 & deviceid = e376640352862852 & synckey = 1
        #_650517214 % 7
        #C2_650517828 % 7
        #C3_650517782 % 7
        #C11_650517809 % 7
        #C13_650466158 % 7
        #C201_1471491461 % 7
        #C203_1471484329 % 7
        #C1000_1471480381 % 7
        #C1001_1471480412 % 7
        #C1004_1471314833 & _ = 1471491460322

        #self.sendmsg(Webwxinit.jsonData['User'],self.finduserByNickname("潘建兴"),"在做啥子")
        msgcore = MsgCore(self.session)
        while True:
            url = "https://webpush.wx2.qq.com/cgi-bin/mmwebwx-bin/synccheck?r=1471491463975&skey="+TicketInfo.skey+"&sid="+TicketInfo.wxsid+"&uin="+TicketInfo.wxuin+"&synckey="
            for item in Webwxinit.jsonData['SyncKey']['List']:
                url = url + ""+str(item['Key'])+"_"+str(item['Val'])+"|"
            print("GET " + url)
            r = self.session.get(url, headers=self.headers, allow_redirects=False,timeout=60)
            r.encoding = "utf-8"
            print(r.text)
            if r.text.find("retcode:\"0\"") == -1:
                break

            if r.text.find("selector:\"0\"") != -1:
                continue

            #https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxsync?sid=VznnR+RhwgnLTued&skey=@crypt_fd882096_f130cf0ca102faafe158aecd5b4b3fa8
            syncUrl = "https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxsync?sid="+TicketInfo.wxsid+"&skey="+TicketInfo.skey
            print("POST request", syncUrl)

            headers = {"Content-type": "application/json;charset=UTF-8"}
            headers.update(self.headers)
            params = {"BaseRequest": {"Uin": TicketInfo.wxuin, "Sid": TicketInfo.wxsid,"Skey":TicketInfo.skey},"SyncKey":Webwxinit.jsonData['SyncKey']}
            print(params)
            syncResult = self.session.post(syncUrl, headers=headers, data=json.JSONEncoder().encode(params),timeout=60)
            syncResult.encoding = "utf-8"
            print("result", syncResult.text)
            Webwxinit.jsonData['SyncKey'] = syncResult.json()['SyncKey']

            sendUserList = []
            for msg in syncResult.json()['AddMsgList']:
                if msg['FromUserName'] == Webwxinit.jsonData['User']['UserName']:
                    continue
                if msg['ToUserName'] != Webwxinit.jsonData['User']['UserName']:
                    continue
                # if msg['MsgType'] != 1:
                #     continue

                fromUser = msgcore.finduserByUsername(msg['FromUserName'])

                if fromUser is None:
                    continue

                print("receive from",fromUser['NickName']," Content:",msg['Content'])
                sendUserList.append(fromUser)
                self.appenduser(sendUserList,fromUser)


            for fu in sendUserList:
                msgcore.sendmsg(Webwxinit.jsonData['User'], fu, "我二爷又去加班了 别找他")

            time.sleep(5)

        print("已在其他地方登录。断开连接...")

    def appenduser(self,userList,user):
        for item in userList:
            if item['UserName'] == user['UserName']:
                return
        userList.append(user)


class MsgCore:
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36"}
    session = None

    def __init__(self, session):
        self.session = session

    def sendmsg(self, fromusername,tousername, msg):
        if fromusername is None or tousername is None:
            return

        print("send msg ",tousername['NickName']," content",msg)
        sendUrl = "https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxsendmsg?lang=zh_CN&pass_ticket="+TicketInfo.pass_ticket
        print("POST request", sendUrl)
        headers = {"Content-type": "application/json;charset=UTF-8"}
        headers.update(self.headers)
        params = {"BaseRequest": {"Uin": TicketInfo.wxuin, "Sid": TicketInfo.wxsid, "Skey": TicketInfo.skey},
                  "Msg": {"Content":msg,"FromUserName":fromusername['UserName'],"ToUserName":tousername['UserName'],"Type":1},
                  "Scene":0}
        print(params)
        sendResult = self.session.post(sendUrl, headers=headers, data=json.dumps(params,ensure_ascii=False).encode("utf-8"),timeout=60)
        sendResult.encoding = "utf-8"
        print("result", sendResult.text)

    def finduserByUsername(self,username):
        if Webwxinit.jsonData['User']['UserName'] == username:
            return Webwxinit.jsonData['User']

        for item in Concat.jsonData['MemberList']:
            if item['UserName'] == username:
                return item
        return None

    def finduserByNickname(self,nickName):

        if Webwxinit.jsonData['User']['UserName'] == nickName or Webwxinit.jsonData['User']['RemarkName'] == nickName:
            return Webwxinit.jsonData['User']

        for item in Concat.jsonData['MemberList']:
            if item['NickName'] == nickName or item['RemarkName'] == nickName:
                return item
        return None

class CheckScanThread(threading.Thread):

    def __init__(self, qrcode):
        threading.Thread.__init__(self)
        self.qrcode = qrcode

    def run(self):
        print("scan...")
        while True:
            data = self.qrcode.checkScan()
            if data == 'window.code=408;':
                continue
            break

        print("confim...")
        dothing = Dothing(self.qrcode.session)
        ticket_url = None
        while True:
            data = self.qrcode.checkConfim()
            if data == 'window.code=408;':
                continue

            arr = str(data).split("\"")
            print(arr)
            ticket_url = arr[1]
            break

        print("已确认，正在验证ticket")
        dothing.checkTicket(ticket_url)
        print("认证成功,获取用户数据")
        dothing.webwxinit()
        dothing.getConcat()

class TicketInfo:
    skey = None
    wxsid = None
    pass_ticket = None
    wxuin = None
    isgrayscale = None

class Webwxinit:
    jsonData = None

class Concat:
    jsonData = None

class Dothing:
    wx2_qq_conn = None
    session = None
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36"}

    def __init__(self,session):
        self.session = session

    def checkTicket(self,ticket_url):
        print("GET", ticket_url)
        r = self.session.get(ticket_url, headers=self.headers, allow_redirects = False)
        print("result",r.text)

        if r.text.find("pass_ticket") == -1:
            time.sleep(5)
            self.checkTicket(ticket_url)
            return

        notify_data_tree = Etree.fromstring(r.text)
        TicketInfo.skey = notify_data_tree.find("skey").text
        TicketInfo.isgrayscale = notify_data_tree.find("isgrayscale").text
        TicketInfo.pass_ticket = notify_data_tree.find("pass_ticket").text
        TicketInfo.wxsid = notify_data_tree.find("wxsid").text
        TicketInfo.wxuin = notify_data_tree.find("wxuin").text



    def webwxinit(self):
        url = "https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxinit?r=1860846903&pass_ticket="+TicketInfo.pass_ticket
        print("POST request",url)

        headers = {"Content-type": "application/json;charset=UTF-8"}
        headers.update(self.headers)
        params = {"BaseRequest":{"Uin":TicketInfo.wxuin,"Sid":TicketInfo.wxsid}}
        print(params)
        r = self.session.post(url, headers=headers,data = json.JSONEncoder().encode(params))
        r.encoding = "utf-8"
        Webwxinit.jsonData = r.json()
        print("result",r.text)


    def getConcat(self):
        url ="https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxgetcontact?r=1471228115491&seq=0&skey="+TicketInfo.skey+"&pass_ticket="+TicketInfo.pass_ticket
        print("GET", url)
        r = self.session.get(url, headers=self.headers)
        r.encoding = "utf-8"
        Concat.jsonData = r.json()
        #print(r.json()['MemberList'][0]['NickName'])
        print(r.text)

    # def webwxbatchgetcontact(self):
    #     url = "https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxbatchgetcontact?type=ex&r=1471693769173"
    #     print("POST request", url)
    #
    #     headers = {"Content-type": "application/json;charset=UTF-8"}
    #     headers.update(self.headers)
    #     params = {"BaseRequest": {"Uin": TicketInfo.wxuin, "Sid": TicketInfo.wxsid}}
    #     print(params)
    #     r = self.session.post(url, headers=headers, data=json.JSONEncoder().encode(params))
    #     r.encoding = "utf-8"
    #     Webwxinit.jsonData = r.json()
    #     print("result", r.text)

#验证码
class QRCode:

    uuid = None
    headers = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36"}
    session = None

    def __init__(self,session):
        self.session = session

    def getUuid(self):
        if self.uuid == None:
            url = "https://login.wx2.qq.com/jslogin?appid=wx782c26e4c19acffb&redirect_uri=https%3A%2F%2Fwx2.qq.com%2Fcgi-bin%2Fmmwebwx-bin%2Fwebwxnewloginpage&fun=new&lang=zh_CN&_=1470879353086"
            print("GET request :",url)
            r = self.session.get(url,headers = self.headers)
            print(r.text)
            self.uuid = r.text.split("\"")[1]
        return self.uuid

    def getCodeImg(self):
        uuid = self.getUuid()
        url = "https://login.wx2.qq.com/qrcode/"+uuid
        print("GET request :", url)
        r = self.session.get(url,headers = self.headers,stream = True)
        path = "/qcode.jpg"
        with open(path,'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw,f)

        return path

    def checkScan(self):
        url = "https://login.wx2.qq.com/cgi-bin/mmwebwx-bin/login?loginicon=true&uuid=" + self.getUuid() +"&tip=0&r=-2110777326&_=1470989564469"
        print("GET request :", url)
        r = self.session.get(url, headers=self.headers)
        print(r.text)
        return r.text

    def checkConfim(self):
        url = "https://login.wx.qq.com/cgi-bin/mmwebwx-bin/login?loginicon=true&uuid=" + self.getUuid() + "&tip=0&r=-2110777326&_=1470989564469"
        print("GET request :", url)
        r = self.session.get(url, headers=self.headers)
        print(r.text)
        return r.text


def start():
    session = requests.session()
    qrcode = QRCode(session)
    path = qrcode.getCodeImg()

    check = CheckScanThread(qrcode)
    check.start()
    print("start...")
    check.join()
    print("SyncCheckThread ..")

    TimerSendMsg(session).start()

    while True:
        try:
            sct = SyncCheckThread(session)
            sct.start()
            sct.join()
        except Exception as e:
            print(e)






if __name__ == '__main__':
    start()
    #SyncCheckThread(requests.session()).run()