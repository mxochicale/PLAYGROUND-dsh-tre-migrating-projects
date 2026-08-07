#!/usr/bin/env python
# coding: utf-8

# # Testing 5 Popular Python Packages
# 
# This notebook picks the **5 most widely-used, general-purpose packages** from the installed
# environment (excluding Jupyter/conda internals like `traitlets`, `jupyter_core`, etc., which
# are infrastructure rather than libraries you'd import in your own code) and runs a few basic
# sanity checks against each one:
# 
# 1. **requests** – HTTP client
# 2. **pydantic** – data validation
# 3. **SQLAlchemy** – SQL toolkit / ORM
# 4. **beautifulsoup4 (bs4)** – HTML parsing
# 5. **PyYAML (yaml)** – YAML serialization
# 
# Each section imports the package, prints its version, and exercises a couple of its core
# functions so you can confirm the environment is working end-to-end.

# ## Setup — import everything and print versions

# In[1]:


import requests
import pydantic
import sqlalchemy
import bs4
import yaml

print(f"requests      : {requests.__version__}")
print(f"pydantic      : {pydantic.VERSION}")
print(f"SQLAlchemy    : {sqlalchemy.__version__}")
print(f"beautifulsoup4: {bs4.__version__}")
print(f"PyYAML        : {yaml.__version__}")


# ## 1. `requests` — HTTP client library
# 
# To keep this test self-contained (no external internet dependency required), we spin up a
# tiny local HTTP server in a background thread and issue a real GET request against it with
# `requests`.

# In[2]:


import threading
import http.server
import socketserver
import json as _json
import time

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(_json.dumps({"message": "Hello from local server", "path": self.path}).encode())

    def log_message(self, format, *args):
        pass  # silence default request logging

PORT = 8765
httpd = socketserver.TCPServer(("localhost", PORT), Handler)
server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
server_thread.start()
time.sleep(0.5)  # give the server a moment to start

response = requests.get(f"http://localhost:{PORT}/test")
print("Status code   :", response.status_code)
print("JSON response :", response.json())
print("Content-Type  :", response.headers["Content-Type"])

httpd.shutdown()


# ## 2. `pydantic` — data validation
# 
# We define a simple model, validate correct data, then intentionally pass invalid data to
# confirm that `ValidationError` is raised as expected.

# In[3]:


from pydantic import BaseModel, Field, ValidationError

class User(BaseModel):
    name: str
    age: int = Field(gt=0, lt=120)
    email: str

# Valid data
user = User(name="Alice", age=30, email="alice@example.com")
print("Valid user  :", user)
print("As dict     :", user.model_dump())

# Invalid data (age out of range) -- should raise
try:
    User(name="Bob", age=-5, email="bob@example.com")
except ValidationError as e:
    print("\nValidation correctly rejected bad input:")
    print(e)


# ## 3. `SQLAlchemy` — SQL toolkit / ORM
# 
# We create an in-memory SQLite database, define an ORM model, insert a couple of rows, and
# query them back out.

# In[4]:


from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine("sqlite:///:memory:", echo=False)
Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Integer)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

session.add_all([
    Product(name="Widget", price=10),
    Product(name="Gadget", price=25),
])
session.commit()

products = session.query(Product).order_by(Product.price).all()
for p in products:
    print(f"id={p.id}  name={p.name!r}  price=${p.price}")

session.close()


# ## 4. `beautifulsoup4` — HTML parsing
# 
# We parse a small HTML snippet and pull out elements using both the tag API and CSS
# selectors.

# In[5]:


from bs4 import BeautifulSoup

html_doc = """
<html>
<head><title>Sample Page</title></head>
<body>
<h1>Welcome</h1>
<ul id="items">
<li class="item">Apple</li>
<li class="item">Banana</li>
<li class="item">Cherry</li>
</ul>
</body>
</html>
"""

soup = BeautifulSoup(html_doc, "html.parser")

print("Title       :", soup.title.string)
print("H1 text     :", soup.h1.text)

items = soup.find_all("li", class_="item")
print("Items found :", [item.get_text() for item in items])

print("CSS selector count:", len(soup.select("#items .item")))


# ## 5. `PyYAML` — YAML serialization
# 
# We dump a Python dictionary to a YAML string, print it, then load it back and confirm it
# round-trips correctly.

# In[6]:


import yaml

data = {
    "name": "Test Config",
    "version": 1.0,
    "features": ["fast", "reliable", "simple"],
    "settings": {"debug": False, "max_connections": 100},
}

yaml_str = yaml.dump(data, default_flow_style=False, sort_keys=False)
print("YAML output:\n")
print(yaml_str)

loaded = yaml.safe_load(yaml_str)
print("Round-trip matches original:", loaded == data)


# ## Summary
# 
# If every cell above ran without errors, then `requests`, `pydantic`, `SQLAlchemy`,
# `beautifulsoup4`, and `PyYAML` are all correctly installed and functioning in this
# environment.

# In[ ]:




