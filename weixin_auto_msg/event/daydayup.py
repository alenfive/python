
import http.client
from PIL import Image,ImageTk
import threading
import io
import base64
import xml.etree.ElementTree as Etree
import json

#HTTPClient实例
class HttpClient:
    http = None

    def get_http(self):
        return self.http


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
            arr = str(data).split("\'")
            if arr[1] == 'window.code=408;':
                continue

            print(arr)
            headStr = arr[1].replace("data:img/jpg;base64,","")
            print(headStr)

            imgdata = base64.b64decode(headStr)
            file = open('/home/freedom/head.jpg', 'wb')
            file.write(imgdata)

            img = Image.open(r'/home/freedom/head.jpg')
            background_image = ImageTk.PhotoImage(img)

            self.label.config(image=background_image)
            self.label.image = background_image
            break

        self.state.config(text="扫描成功，请确认")
        print("confim...")
        dothing = Dothing()
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

class ConnPool:
    wx2_conn = None
    wx_conn = None
    wx2_qq_conn = None

    @staticmethod
    def clear(self):
        ConnPool.wx2_qq_conn = None
        ConnPool.wx_conn = None
        ConnPool.wx2_conn = None

class Dothing:
    __wx2_qq_url = "https://wx2.qq.com"
    wx2_qq_conn = None

    def __init__(self):
        if ConnPool.wx2_qq_conn == None:
            ConnPool.wx2_qq_conn = http.client.HTTPSConnection('wx2.qq.com', 443)
        self.wx2_qq_conn = ConnPool.wx2_qq_conn

    def checkTicket(self,ticket_url):
        uri = ticket_url.replace(self.__wx2_qq_url,"")
        print("check ticket...", self.__wx2_qq_url + uri)
        self.wx2_qq_conn.request("GET",uri)
        r1 = self.wx2_qq_conn.getresponse()
        data = str(r1.read(),'utf-8')

        print("result:",data)
        print("head:",r1.getheaders())

        if data.find("pass_ticket") == -1:
            self.checkTicket(ticket_url)
            return

        notify_data_tree = Etree.fromstring(data)
        TicketInfo.skey = notify_data_tree.find("skey").text
        TicketInfo.isgrayscale = notify_data_tree.find("isgrayscale").text
        TicketInfo.wxsid = notify_data_tree.find("wxsid").text
        TicketInfo.wxuin = notify_data_tree.find("wxuin").text
        TicketInfo.pass_ticket = notify_data_tree.find("pass_ticket").text

    def webwxinit(self):
        uri = "/cgi-bin/mmwebwx-bin/webwxinit?r=2101655714&lang=zh_CN&pass_ticket="+TicketInfo.pass_ticket
        print("POST request", self.__wx2_qq_url + uri)

        headers = {"Content-type": "application/json;charset=UTF-8"}
        params = {"BaseRequest":{"Uin":TicketInfo.wxuin,"Sid":TicketInfo.wxsid}}
        print(params)
        self.wx2_qq_conn.request("POST", uri, json.JSONEncoder().encode(params),headers)
        r1 = self.wx2_qq_conn.getresponse()
        data = str(r1.read(), 'utf-8')
        print(data)

    def getConcat(self):
        #https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxgetcontact?r=1471228115491&seq=0&skey=@crypt_fd882096_e8bd8df96281b5dabd75bce72d14e9cd
        uri ="/cgi-bin/mmwebwx-bin/webwxgetcontact?r=1471228115491&seq=0&skey="+TicketInfo.skey
        print("GET request", self.__wx2_qq_url + uri)
        self.wx2_qq_conn.request("GET", uri)
        r1 = self.wx2_qq_conn.getresponse()
        data = str(r1.read(), 'utf-8')
        print(r1.getheaders)
        print(data)

#验证码
class QRCode:

    uuid = None
    __wx2_url = "https://login.wx2.qq.com"
    __wx_url = "https://login.wx.qq.com"
    wx2_conn = None
    wx_conn = None

    def __init__(self):
        if ConnPool.wx2_conn == None:
            ConnPool.wx2_conn = http.client.HTTPSConnection('login.wx2.qq.com', 443)
        if ConnPool.wx_conn == None:
            ConnPool.wx_conn = http.client.HTTPSConnection('login.wx.qq.com', 443)

        self.wx2_conn = ConnPool.wx2_conn
        self.wx_conn =  ConnPool.wx_conn

    def getUuid(self):
        if self.uuid == None:
            uri = "/jslogin?appid=wx782c26e4c19acffb&redirect_uri=https%3A%2F%2Fwx2.qq.com%2Fcgi-bin%2Fmmwebwx-bin%2Fwebwxnewloginpage&fun=new&lang=zh_CN&_=1470879353086"
            print("GET request :",self.__wx2_url + uri)
            self.wx2_conn.request("GET",uri)
            r1 = self.wx2_conn.getresponse()
            data = r1.read()
            print(str(data))
            self.uuid = str(data).split("\"")[1]
        return self.uuid

    def getCodeImg(self):
        uuid = self.getUuid()
        uri = "/qrcode/"+uuid
        print("GET request :", self.__wx2_url + uri)
        self.wx2_conn.request("GET",uri)
        r1 = self.wx2_conn.getresponse()
        data = r1.read()
        return data

    def checkScan(self):
        uri = "/cgi-bin/mmwebwx-bin/login?loginicon=true&uuid=" + self.getUuid() +"&tip=0&r=-2110777326&_=1470989564469"
        print("GET request :", self.__wx2_url + uri)
        self.wx2_conn.request("GET", uri)
        r1 = self.wx2_conn.getresponse()
        data = r1.read()
        print(data)
        return data

    def checkConfim(self):
        uri = "/cgi-bin/mmwebwx-bin/login?loginicon=true&uuid=" + self.getUuid() + "&tip=0&r=-2110777326&_=1470989564469"
        print("GET request :", self.__wx_url + uri)
        self.wx_conn.request("GET", uri)
        r1 = self.wx_conn.getresponse()
        data = str(r1.read(),"utf-8")
        print(data)
        return data



def main():
    QRCode().getCodeImg()


def start(label,state):
    ConnPool.wx2_qq_conn = None
    ConnPool.wx_conn = None
    ConnPool.wx2_conn = None

    qrcode = QRCode()
    f = open("/home/freedom/qcode.jpg", "wb")
    f.write(qrcode.getCodeImg())
    f.flush()
    f.close()
    img = Image.open(r"/home/freedom/qcode.jpg")
    background_image = ImageTk.PhotoImage(img)

    label.config(image=background_image)
    label.image = background_image

    state.config(text="等待手机扫描中...")



    check = CheckScanThread(qrcode,label,state)
    check.setDaemon(label)
    check.start()
    print("start...")