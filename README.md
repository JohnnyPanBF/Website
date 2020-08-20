# Kangaroo

## 檔案說明
```
server/           伺服器的檔案
   __init__.py    負責 Server, CherryPy
   mode.py        負責 Database, SQLAlchemy
   view.py        負責 Html, CherryPy

requirement.txt   需要安裝的 Libarary
main.             呼叫的程式
```

### 安裝
1. 開啟 Python Virtual Enviroment<br>
`$ python -m venv env`

2. 啟動 Python Virtual Enviroment<br>
`$ source env/bin/activate`

3. 安裝 Libraray<br>
`$ pip install -r requirement.txt`

### 啟動
`$ python main.py`