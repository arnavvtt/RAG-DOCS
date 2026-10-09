import requests

BASE = "http://127.0.0.1:8000"

# Health check
r = requests.get(f"{BASE}/health")
print("Health:", r.status_code, r.json())

# Ask
r = requests.post(f"{BASE}/ask", json={"question": "What is RAG?", "top_k": 4})
print("\nAsk:", r.status_code)
data = r.json()
print(f"Answer: {data['answer'][:200]}...")
print(f"Sources: {[s['filename'] for s in data['sources']]}")