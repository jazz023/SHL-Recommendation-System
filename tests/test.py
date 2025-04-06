import requests
print(requests.post("http://localhost:8000/recommend", 
                   json={"query": "Looking to hire mid-level professionals who are proficient in Python, SQL and Java Script. Need an\
assessment package that can test all skills with max duration of 60 minutes."}).json())