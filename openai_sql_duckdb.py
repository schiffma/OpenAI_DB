# -*- coding: utf-8 -*-
"""
Created on Mon May 22 01:05:46 2023

@author: schiffma
"""

import openai
import os
import re
import duckdb
import sys
from tabulate import tabulate
import time
from dotenv import load_dotenv


load_dotenv()
openai.api_key = os.environ.get('OPENAI_API_KEY')

#db = chinook.db"
context = "gwr_ch_bfs"
db = context + "_duck.db"
db_file = "data/" + db
context_file = "data/" + context + "_context.txt"
select_pattern = '(SELECT|WITH)(.|\n)+?([;]|[`]{3})' # find SQL non-greedy !!!

# openai_model = "gpt-3.5-turbo"
openai_model = "gpt-4"
openai_temperature = 0.1


def read_txt_file(file_name):
    with open(file_name, mode="r", encoding="utf-8") as file:
        text_str = file.read()
    return text_str

def open_db():
    conn = duckdb.connect(db_file, read_only=True) # just queries
    return conn

def eval_sql(conn, sql, answer):
    eval_sql_res = False
    time_start = time.time()
    try:
        df = conn.sql(sql).df()
        result = tabulate(df, headers='keys', tablefmt='psql') + "\n" + sql
        eval_sql_res = True
    except Exception as e:
        result = f"SQL-Error {e} for:\n{answer}"
        eval_sql_res = False
    time_end=time.time() 
    print('\n>> Total Runtime of %s: %.2f second.' 
          %(sys._getframe().f_code.co_name,
          time_end-time_start))        
    return result, eval_sql_res

def open_ai_sql(messages):
    time_start = time.time() 
    time_start_openai = time.time()
    chat = openai.ChatCompletion.create(
        model=openai_model,
        temperature = openai_temperature,
        n = 1,
        max_tokens=2048,
        messages=messages
        
    )
    time_end_openai=time.time()
    print("prompt_tokens: ", chat.usage["prompt_tokens"])
    total_tokens = int(chat.usage["total_tokens"])
    print("total_tokens: ", total_tokens)
    print('>> Runtime of OpenAI: %.2f second.' 
          %(time_end_openai-time_start_openai))
    reply = chat.choices[0].message.content            
    eval_sql_res = False

    #answer_1line = " ".join(reply.splitlines())            
    sql = ""
    matches = re.finditer(select_pattern, reply)
    for match in matches: # get last sql
        sql = match.group()
    if len(sql) > 0:    
        # print(f"SQL found in answer: {sql}")
        sql = sql.replace('`','')
        reply, eval_sql_res = eval_sql(conn, sql, reply)
    else:
        reply  = f"SQL not found in reply:\n{reply}"
    nl = "\n" if eval_sql_res else ""
    print(f"\nChatGPT[{db}]: {nl}{reply}")
    time_end=time.time() 
    print('\n> Total Runtime of %s: %.2f second.' 
          %(sys._getframe().f_code.co_name,
          time_end-time_start))        

def sql_answer(conn, context_text):
    messages = []
    messages.append({"role": "system", "content": context_text})
    while True:        
        query = input("\nQuestion: ")
        #query = prompt("\nQuestion: ")
        if query == "exit":
            break    
        if query:           
            # query = context_text + query
            messages.append({"role": "user", "content": query})                        
            try:  
                open_ai_sql(messages)       
            except Exception as e:
              print(f"OpenAI-Error {e}")


if __name__ == "__main__":
    context_text = read_txt_file(context_file)
    conn = open_db() 
    sql_answer(conn, context_text)
    conn.close()