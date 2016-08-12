
import http.client
from tkinter import PhotoImage

#HTTPClient实例
class HttpClient:
    http = None

    def get_http(self):
        return self.http


#验证码

class QRCode:

    uuid = ''
    __uuid_url = "https://login.wx2.qq.com"

    def getUuid(self):
        conn = http.client.HTTPSConnection('login.wx2.qq.com', 443)
        conn.request("GET","/jslogin?appid=wx782c26e4c19acffb&redirect_uri=https%3A%2F%2Fwx2.qq.com%2Fcgi-bin%2Fmmwebwx-bin%2Fwebwxnewloginpage&fun=new&lang=zh_CN&_=1470879353086")
        r1 = conn.getresponse()
        data = r1.read()
        print(str(data))
        self.uuid = str(data).split("\"")[1]
        conn.close()
        return self.uuid

    def getCodeImg(self):
        uuid = self.getUuid()
        #https: // login.weixin.qq.com / qrcode / Ab5nFLgydg ==
        conn = http.client.HTTPSConnection('login.wx2.qq.com', 443)
        conn.request("GET","/qrcode/"+uuid)
        r1 = conn.getresponse()
        data = r1.read()
        conn.close()
        return data

def main():
    QRCode().getCodeImg()


def start(label):

    #f = open("/xx.gif", "wb")
    #f.write(QRCode().getCodeImg())
    #f.flush()
    #f.close()
    img = PhotoImage(file="C:/Users/Administrator/Desktop/gg.gif")
    label.config(image=img)
    print("start...")