import httpx

r = httpx.get('http://127.0.0.1:8001/health')
print(r.status_code, r.text)
