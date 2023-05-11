# TGBot

# 1. The bot abble to be in role as writer. It generate text in one context from short-story to whole book.
It generate book by the saving answer from AI in db and resend it to AI again in context: continue the story in same way. 
Controller of bot is reacting to this command '/write' to start generate book.
But user have to give some context at start. Such as a kind of story, style of writing, etc.
Also user could include a number symbols in request. By the buil-in parser bot shall take a first found number as number of symbols in book.
If user doesn't write a number in request bot will generate book in default setting length.
It's possible to set default symbol's length in config module:
SYMBOLS_LENGTH_IN_BOOK = 20000  # default size of story/book in symbols
Bot is using cycle of iteration with request for rewrite text. 
It's possible to set your desired iteration quantity in config module:
TEXT_REWRITE_ITERATION = 3  # default quantity of rewrite text by AI
At the end all entries for specific chat_id in db will be flush automatically.  
To get better perfomance bot doesn't save book file in local storage, it keep it in buffer and render the docx file from RAM.
Books rendering works asynchronous, so it doesn't block any feature. But keep in mind that if you send request /write while bot already write a book it won't be work as expected. 
That's explain as db scheme consist of two relations. The first relation for save chats by id and the second to storing AI model's responses to specific user_id. 
Sending request to write another book while bot haven't done previous just will mix it all in one rambling text.   

# WARNING
For 05.11.23 the AI model doesn't set optimal for render book. That's a reason why sometimes bot produce incoherent text.

![image](https://github.com/leonidsliusar/TGBot/assets/128726342/f3a26c8b-3b5f-4868-ba98-17a1384bcb88)

![image](https://github.com/leonidsliusar/TGBot/assets/128726342/8d266ea4-5b3d-42b3-a8c7-c920069080d0)

# 2. The bot abble to be in role as chat assistant. That's pretty classic exploitation of chatGPT.
Althought the AI model you can choose by API haven't memory, the app got a short-term memory in RAM. 
It's implemented like a hash-map (Python's built-in dict) with chat_id as key and messages as elements of queue (Python's built-in deque).
Before append new message in hashmap it checks for length of queue doesn't over settings length.
It's possible to set your desired capacity in config module:
MAX_CAPACITY_MEM_CACHE = 50  # set 1 < capacity < MAX (measured in number of messages) to save context in memory(RAM)

![image](https://github.com/leonidsliusar/TGBot/assets/128726342/297b25ee-c9cc-4b4f-9c92-829528389aee)

# 3. One more feature it's the sql quiz.
The parser login and make a request to special url, parses the response and send to user the question.
User can use /sql_answer and bot will send correct answer.
 
![image](https://github.com/leonidsliusar/TGBot/assets/128726342/d1ee539d-b08c-4db0-8e39-eccd6efe5da1)

![image](https://github.com/leonidsliusar/TGBot/assets/128726342/a8614cfd-1747-4a7b-bb63-9e780f6e93e5)

![image](https://github.com/leonidsliusar/TGBot/assets/128726342/526e4ed8-6919-4d97-9c0b-f873a83df0be)

# Environment configuration

API_TELEGRAM    |set API key for telegram (https://t.me/botfather)

API_GPT         |set API key for openai (https://platform.openai.com/overview)

ORGANIZATION    |set organization code for openai (https://platform.openai.com/overview)

USERNAME_SQL    |set username to sql questions recource (https://www.sql-ex.com/?Lang=1)

PASSWORD        |set password to sql questions recource (https://www.sql-ex.com/?Lang=1)

DB              |set DBMS ('postgres'|'mysql'|etc)

DB_LOGIN        |set username of DB ('postgres')

DB_PASS         |set password of DB ('password')

DB_HOST         |set database's IP  ('127.0.0.1')

DB_NAME         |set name of db ('db_name')
