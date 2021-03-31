# importing whole module 
from tkinter import * 
from tkinter.ttk import *
  
# importing strftime function to 
# retrieve system's time 
from time import *
  
# creating tkinter window 
root = Tk() 
root.title('Clock') 

# This function is used to  
# display time on the label 
def timex(): 
    string = int(time())
    lbl.config(text = string) 
    lbl.after(1000, timex) 
    
# Styling the label widget so that clock 
# will look more attractive 
lbl = Label(root, font = ('calibri', 40, 'bold'), 
            background = 'purple', 
            foreground = 'white') 

# Placing clock at the centre 
# of the tkinter window 
lbl.pack(anchor = 'center') 
timex() 
  
mainloop() 