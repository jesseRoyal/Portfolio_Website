import requests

url = "https://chatgpt-42.p.rapidapi.com/chat"

payload = {
    "messages": [
        {
            "role": "user",
            "content": "Hello, how are you? can you help me?"
        }
    ],
    "model": "gpt-4o-mini"
}
headers = {
    "x-rapidapi-key": "ba0b853dc8mshed2be5e2cf6966bp1aaf49jsn78c335d4e373",
    "x-rapidapi-host": "chatgpt-42.p.rapidapi.com",
    "Content-Type": "application/json"
}

print("Sending request to API:", url)
print("Payload:", payload)
print("Headers:", headers)

try:
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    print("Response status code:", response.status_code)
    print("Response JSON:", response.json())
except requests.exceptions.RequestException as e:
    print("Request failed:", e)
