
import requests
from PIL import Image,ImageTk
import threading
import io
import base64
import xml.etree.ElementTree as Etree
import json
import shutil
import time

#HTTPClient实例
class HttpClient:
    http = None

    def get_http(self):
        return self.http


class SyncCheckThread(threading.Thread):

    session = None

    def __init__(self,session):
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

        #while True:
         #url = "https://webpush.wx2.qq.com/cgi-bin/mmwebwx-bin/synccheck?r=1471491463975&skey=" + TicketInfo.skey + "&sid="+TicketInfo.wxsid+"&uin="+TicketInfo.wxuin




class CheckScanThread(threading.Thread):

    def __init__(self,qrcode,label,state):
        threading.Thread.__init__(self)
        self.qrcode = qrcode
        self.label = label
        self.state = state

    def run(self):
        print("scan...")
        while True:
            data = self.qrcode.checkScan()
            if data == 'window.code=408;':
                continue

            headStr = data.split("\'")[1].replace("data:img/jpg;base64,","")

            imgdata = base64.b64decode(headStr)
            file = open('/home/freedom/head.jpg', 'wb')
            file.write(imgdata)
            file.flush()
            file.close()

            img = Image.open('/home/freedom/head.jpg',mode="r")
            background_image = ImageTk.PhotoImage(img)

            self.label.config(image=background_image)
            self.label.image = background_image
            break

        self.state.config(text="扫描成功，请确认")
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

        self.state.config(text="已确认，正在验证ticket")
        dothing.checkTicket(ticket_url)

        self.state.config(text="认证成功,获取用户数据")

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
        path = "/home/freedom/qcode.jpg"
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


def start(label,state):


    session = requests.session()
    qrcode = QRCode(session)
    path = qrcode.getCodeImg()
    img = Image.open(path,mode="r")
    background_image = ImageTk.PhotoImage(img)

    label.config(image=background_image)
    label.image = background_image

    state.config(text="等待手机扫描中...")

    check = CheckScanThread(qrcode,label,state)
    check.setDaemon(label)
    check.start()
    print("start...")
    check.join()

    print("SyncCheckThread ..")
    SyncCheckThread(session).start()