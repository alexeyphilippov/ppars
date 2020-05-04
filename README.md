# Proxy Manager

---

## Docker

### Установка

```bash
docker build -t ppar ./ppars/
```
### Запуск сервера
```bash
docker run -p 5000:5000 ppar
```

---

## Virtual environment

### Установка

```bash
pip install virtualenv
virtualenv env
source env/bin/activate
pip install -r requirements.txt
```

### Запуск сервера
```bash
FLASK_APP=app.py python app.py
```
---
## REST API

##### После этого можно заполнить базу POST зопросом на адрес 
```http://127.0.0.1:5000/proxy/fill```

---
##### Получить список имеющихся прокси GET запросом на адрес
```http://127.0.0.1:5000/proxy```
