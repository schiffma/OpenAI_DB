# -*- coding: utf-8 -*-
"""
Created on Mon Jul 31 11:11:25 2023

@author: schiffma
"""

from dotenv import load_dotenv
import duckdb
import openai
import os
import re
import time
import sys
from tabulate import tabulate

load_dotenv()
openai.api_key = os.environ.get('OPENAI_API_KEY')


class ChatBotOpenAI():

    def __init__(self):
        self.context_file = { "general" : "data/general_context.txt",
                              "gpp" : "data/gpp_context.txt", 
                              "gwr" : "data/gwr_ch_bfs_context.txt"  }
        self.context_db = { "gpp" : "data/gpp_duck.db", 
                            "gwr" : "data/gwr_ch_bfs_duck.db"  }
       
        self.messages = [
            {"role": "system", "content": self.__read_txt_file(self.context_file["general"])},
        ]
        self.db_file = None
        
        self.openai_model = "gpt-4"
        self.openai_temperature = 0.2

        self.select_pattern = '(SELECT|WITH)(.|\n)+?([;]|[`]{3})' # find (multi-line) SQL non-greedy !!!
  
    def __read_txt_file(self, file_name):
        with open(file_name, mode="r", encoding="utf-8") as file:
            text_str = file.read()
        return text_str    
  
    def __eval_sql(self, sql, answer):
        eval_sql_res = False
        run_time = ""
        time_start = time.time()
        conn = duckdb.connect(self.db_file, read_only=True) # just queries
        try:
            df = conn.sql(sql).df()
            result = sql + "\n" + tabulate(df, headers='keys', tablefmt='psql') + "\n"
            eval_sql_res = True
        except Exception as e:
            result = f"{answer}\nSQL-Error {e} for:\n"
        time_end=time.time()
        conn.close() 
        run_time = f"\n> Total Runtime of {sys._getframe().f_code.co_name} {round(time_end-time_start,2)} second(s)"         
        return result, run_time, eval_sql_res
    
    def __handle_sql(self, reply):
        time_start = time.time()
        eval_sql_res = False
        run_time = ""
        run_time_sql = ""
        sql = ""
        matches = re.finditer(self.select_pattern, reply)
        for match in matches: # get last sql, usually the best one
            sql = match.group()
        if len(sql) > 0:    
            # print(f"SQL found in answer: {sql}")
            sql = sql.replace('`','')
            reply, run_time_sql, eval_sql_res = self.__eval_sql(sql, reply)
        else:
            reply  = f"{reply}\nSQL not found in reply:\n"
        time_end=time.time() 
        run_time = f"\n> Total Runtime of {sys._getframe().f_code.co_name} {round(time_end-time_start,2)} second(s)"  
        # print(run_time_sql + run_time)
        return reply, run_time_sql + run_time, eval_sql_res 
    
    

    def set_context_str(self, context):
        context_text = self.__read_txt_file(self.context_file[context])
        self.messages = [
            {"role": "system", "content": context_text},
        ]
        self.db_file = None
        
    def set_context_db(self, context):
        context_text = self.__read_txt_file(self.context_file[context])
        self.messages = [
            {"role": "system", "content": context_text},
        ]
        self.db_file = self.context_db[context]        

    def chat(self, input):
        if self.db_file == None:
            reply, run_time, status = self.chat_openai(input)
        else:
            reply, run_time, status = self.chat_db(input)
        return reply, run_time, status
            

    def chat_openai(self, input):
        time_start = time.time()
        reply = None
        run_time = None
        status = -1
        try:
            
            self.messages.append({"role": "user", "content": input})
            # https://platform.openai.com/docs/api-reference/completions/create
            chat = openai.ChatCompletion.create(
                model=self.openai_model,
                messages=self.messages,
                temperature=self.openai_temperature,
                max_tokens=2048,
                #stream = True,
                n = 1,
                #frequency_penalty=0,
                #presence_penalty=0
            )
            reply = chat.choices[0].message.content
            self.messages.append({"role": "assistant", "content": reply})
                 
            status = 0
        except Exception as e:
           reply = f"OpenAI-Error {e}"
        time_end=time.time() 
        run_time = f"\n> Total Runtime of {sys._getframe().f_code.co_name} {round(time_end-time_start,2)} second(s)"    
        return reply, run_time, status

    def chat_db(self, input):
        time_start = time.time()
        reply, run_time_openai, status = self.chat_openai(input)
        if status == 0:
            reply, run_time_sql, status = self.__handle_sql(reply)
        time_end=time.time() 
        run_time = f"\n> Total Runtime of {sys._getframe().f_code.co_name} {round(time_end-time_start,2)} second(s)" 
        return reply, run_time_openai + run_time_sql + run_time + "\n", status
                
        
        
        
     