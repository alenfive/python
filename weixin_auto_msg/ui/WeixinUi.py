from tkinter import *
from time import *
import datetime

from weixin_auto_msg.event import daydayup


top = Tk(className="微信auto")
labelframe = LabelFrame(top, text="", width=500, height=300)
labelframe.pack_propagate(0)
labelframe.pack()

imgLabel = Label(labelframe,bg="gray",text="二维码",width=50,height=50)
startBtn = Button(labelframe, text="开始", width=15, command=lambda: daydayup.start(imgLabel))
startBtn.pack_propagate(0)
startBtn.pack()
imgLabel.pack()

top.mainloop()















