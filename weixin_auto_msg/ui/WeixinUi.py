from tkinter import *
from time import *
import datetime
from PIL import Image,ImageTk


from weixin_auto_msg.event import daydayup



top = Tk(className="微信auto")
labelframe = LabelFrame(top, text="", width=500, height=550)
labelframe.pack_propagate(0)
labelframe.pack()

state = Label(labelframe,text="状态栏",bg="gray",fg="white",height=2,width=100)

imgLabel = Label(labelframe,bitmap = 'question',text="",width=430,height=430,compound=LEFT)
startBtn = Button(labelframe, text="刷新", width=15, command=lambda: daydayup.start(imgLabel,state))
startBtn.pack_propagate(0)
startBtn.pack()
imgLabel.pack()


state.pack()
daydayup.start(imgLabel,state)
top.mainloop()















