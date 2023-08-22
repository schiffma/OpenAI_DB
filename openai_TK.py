# -*- coding: utf-8 -*-
"""
Created on Sun Jul 30 17:51:28 2023

@author: schiffma
"""

openai_tk = """
________                              _____   .___      ___________ ____  __. 
\_____  \  ______    ____    ____    /  _  \  |   |     \__    ___/|    |/ _| 
 /   |   \ \____ \ _/ __ \  /    \  /  /_\  \ |   | ______|    |   |      <   
/    |    \|  |_> >\  ___/ |   |  \/    |    \|   |/_____/|    |   |    |  \  
\_______  /|   __/  \___  >|___|  /\____|__  /|___|       |____|   |____|__ \ 
        \/ |__|         \/      \/         \/                              \/ 
                                                                              
schiffma 2023

"""

import tkinter as tk
import time
import os
from chatbot_openai import ChatBotOpenAI

window_size="800x600"


class ChatInterface(tk.Frame):

    def __init__(self, master=None):
        

        tk.Frame.__init__(self, master)
        self.master = master
        
        self.base_prompt = "OpenAI-TK"
        self.bot_prompt = self.base_prompt
        
        self.user = os.getlogin()
        
        self.history = []
        self.history_index = -1


        colors =  { "Default": {'bg': "#FFFFFF", "bg2": "#EEEEEE", "fg" : "#000000" },
                  "Dark": {'bg': "#212121", "bg2": "#2a2b2d", "fg" : "#FFFFFF" },
                  "Grey": {'bg':  "#4f4f4f", "bg2": "#444444", "fg" : "#ffffff" },
                  "Torque": {'bg': "#669999", "bg2":  "#003333", "fg" : "#FFFFFF" },
                  "Darkblue": {'bg': "#1c2e44", "bg2":  "#263b54", "fg" : "#FFFFFF" },
                  "Hacker": {'bg': "#0F0F0F", "bg2":  "#0F0F0F", "fg" : "#33FF33"},
                  "Hacker2": {'bg': "#0F0F0F", "bg2":  "#0F0F0F", "fg" : "#FF8C00"}}

        # sets default bg for top level windows
        
        
        self.tl_bg = colors["Hacker"]["bg"]
        self.tl_bg2 = colors["Hacker"]["bg2"]
        self.tl_fg = colors["Hacker"]["fg"]
        self.font = "fixedsys"        

        menu = tk.Menu(self.master)
        self.master.config(menu=menu, bd=5)
    # Menu bar

    # File
        file = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=file)
       # file.add_command(label="Save Chat Log", command=self.save_chat)
        file.add_command(label="Clear Chat", command=self.clear_chat)
      #  file.add_separator()
        file.add_command(label="Exit",command=self.chatexit)
        
    # Options
        contexts = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Contexts", menu=contexts)
        contexts.add_command(label="General",command=self.general)
        contexts.add_command(label="SQL/Global Power Plants",command=self.gpp)
        contexts.add_command(label="SQL/GWR CH",command=self.gwr_ch_bfs)

       
        help_option = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Help", menu=help_option)
        #help_option.add_command(label="Features", command=self.features_msg)
        help_option.add_command(label="About PyBot", command=self.msg)
        help_option.add_command(label="Developers", command=self.about)
        
 
     
        self.text_frame = tk.Frame(self.master, bd=6)
        self.text_frame.pack(expand=True, fill=tk.BOTH)

        # scrollbar for text box
        self.text_box_scrollbar = tk.Scrollbar(self.text_frame, bd=0)
        self.text_box_scrollbar.pack(fill=tk.Y, side=tk.RIGHT)

        # contains messages
        self.text_box = tk.Text(self.text_frame, yscrollcommand=self.text_box_scrollbar.set, state=tk.DISABLED,
                             bd=1, padx=6, pady=6, spacing3=8, wrap=tk.WORD, bg=None, font="Verdana 10", relief=tk.GROOVE,
                             width=10, height=1)
        self.text_box.pack(expand=True, fill=tk.BOTH)
        self.text_box_scrollbar.config(command=self.text_box.yview)
        
        

        # frame containing user entry field
        self.entry_frame = tk.Frame(self.master, bd=1)
        self.entry_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # entry field
        self.entry_field = tk.Entry(self.entry_frame, bd=1, justify=tk.LEFT)
        self.entry_field.pack(fill=tk.X, padx=6, pady=6, ipady=3)
        # self.users_message = self.entry_field.get()

        # frame containing send button and emoji button
        self.send_button_frame = tk.Frame(self.master, bd=0)
        self.send_button_frame.pack(fill=tk.BOTH)

        # send button
        self.send_button = tk.Button(self.send_button_frame, text="Send", width=5, relief=tk.GROOVE, bg='white',
                                  bd=1, command=lambda: self.send_message_insert(None), activebackground="#FFFFFF",
                                  activeforeground="#000000")
        self.send_button.pack(side=tk.LEFT, ipady=8)
        self.master.bind("<Return>", self.send_message_insert)
        self.master.bind("<Up>",self.cycleHistory)
        
        self.last_sent_label(date="No messages sent.")

         # Options
        options = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Options", menu=options)         
        # font
        font =tk.Menu(options, tearoff=0)
        options.add_cascade(label="Font", menu=font)
        font.add_command(label="Default",command=lambda: self.font_change_generic("Verdana 10"))
        font.add_command(label="Times",command=lambda: self.font_change_generic("Times"))
        font.add_command(label="System",command=lambda: self.font_change_generic("System"))
        font.add_command(label="Helvetica",command=lambda: self.font_change_generic("helvetica 10"))
        font.add_command(label="Fixedsys",command= lambda: self.font_change_generic("fixedsys")) 
           
     
         # color theme
        color_theme = tk.Menu(options, tearoff=0)
        options.add_cascade(label="Color Theme", menu=color_theme)
        color_theme.add_command(label="Default",command=lambda: self.color_theme_generic(colors["Default"])) 
        color_theme.add_command(label="Dark",command=lambda: self.color_theme_generic(colors["Dark"])) 
        color_theme.add_command(label="Grey",command=lambda: self.color_theme_generic(colors["Grey"])) 
        color_theme.add_command(label="Blue",command=lambda: self.color_theme_generic(colors["Darkblue"]))        
        color_theme.add_command(label="Torque",command=lambda: self.color_theme_generic(colors["Torque"]))
        color_theme.add_command(label="Hacker",command=lambda: self.color_theme_generic(colors["Hacker"]))
        color_theme.add_command(label="Hacker2",command=lambda: self.color_theme_generic(colors["Hacker2"]))
            
        self.font_change_generic("fixedsys")
        self.color_theme_generic(colors["Hacker"]) 
    
        self.__append_to_text_box(openai_tk)
        self.openaibot = ChatBotOpenAI()
        

        
    def __append_to_text_box(self, text):
        self.text_box.configure(state=tk.NORMAL)
        self.text_box.insert(tk.END, text)
        self.text_box.configure(state=tk.DISABLED)
        self.text_box.see(tk.END)
                
    def last_sent_label(self, date):
        try:
            self.sent_label.destroy()
        except AttributeError:
            pass

        self.sent_label = tk.Label(self.entry_frame, font="Verdana 7", text=date, bg=self.tl_bg2, fg=self.tl_fg)
        self.sent_label.pack(side=tk.LEFT, fill=tk.X, padx=3)

    def clear_chat(self):
        self.text_box.config(state=tk.NORMAL)
        self.last_sent_label(date="No messages sent.")
        self.text_box.delete(1.0, tk.END)
        self.text_box.delete(1.0, tk.END)
        self.text_box.config(state=tk.DISABLED)

    def chatexit(self):
        self.master.destroy()
        
    def general(self):
        self.bot_prompt = self.base_prompt
        context = "general"
        self.openaibot.set_context_db(context)
        self.__append_to_text_box(f"SQL-Context: {context} loaded.\n\n")
        
        
    def gpp(self):
        self.bot_prompt = self.base_prompt + "[gpp]"
        context = "gpp"
        self.openaibot.set_context_db(context)
        self.__append_to_text_box(f"SQL-Context: {context} loaded.\n\n")
        

    def gwr_ch_bfs(self):
        self.bot_prompt = self.base_prompt + "[gwr]"
        context = "gwr"
        self.openaibot.set_context_db(context)
        self.__append_to_text_box(f"SQL-Context: {context} loaded.\n\n")
        

    def msg(self):
        tk.messagebox.showinfo(f"{self.base_prompt}",f"{self.base_prompt} is a Python/Tk chatbot powered by the OpenAI API.")

    def about(self):
        tk.messagebox.showinfo(f"{self.base_prompt}","schiffma")
    
    def send_message_insert(self, message):
        user_input = self.entry_field.get()
        if len(user_input) == 0: return 
        self.history.append(user_input)
        self.history_index = -1        
        input_ = f"{self.user} : {user_input}\n"
        self.__append_to_text_box(input_)                 
        reply, run_time,_ = self.openaibot.chat(user_input)
        pr=f"{self.bot_prompt} : " + reply + "\n" + run_time + "\n"
        self.__append_to_text_box(pr)
        self.last_sent_label(str(time.strftime( "Last message sent: " + '%B %d, %Y' + ' at ' + '%I:%M %p')))
        self.entry_field.delete(0,tk.END)
        time.sleep(0)


    def cycleHistory(self,event):
        if len(self.history):
            try:
                comm = self.history[self.history_index]
                self.history_index -= 1
            except IndexError:
                self.history_index = -1
                comm = self.history[self.history_index]
            self.entry_field.delete(0,tk.END)
            self.entry_field.insert(0,comm)   


    def font_change_generic(self, font):
        self.text_box.config(font=font)
        self.entry_field.config(font=font)
        self.font = font


    def color_theme_generic(self, colors):
        self.master.config(bg=colors["bg2"])
        self.text_frame.config(bg=colors["bg2"])
        self.entry_frame.config(bg=colors["bg2"])
        self.text_box.config(bg=colors["bg"], fg=colors["fg"])
        self.entry_field.config(bg=colors["bg"], fg=colors["fg"], insertbackground=colors["fg"])
        self.send_button_frame.config(bg=colors["bg2"])
        self.send_button.config(bg=colors["bg"], fg=colors["fg"], activebackground=colors["bg"], activeforeground=colors["fg"])
        self.sent_label.config(bg=colors["bg2"], fg=colors["fg"])
        self.tl_bg = colors["bg"]
        self.tl_bg2 = colors["bg2"]
        self.tl_fg = colors["fg"]
  

if __name__ == "__main__":
    root=tk.Tk()
    _ = ChatInterface(root)
    root.geometry(window_size)
    root.title("TK")
    # root.iconbitmap('i.ico')
    root.mainloop()