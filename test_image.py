import urllib.request
import urllib.parse
import base64

prompt = "white dress shirt, flat lay, white background"
encoded = urllib.parse.quote(prompt)
url = f"https://image.pollinations.ai/prompt/{encoded}?width=400&height=400&nologo=true"

print(f"Fetching: {url}")

try:
    with urllib.request.urlopen(url, timeout=15) as response:
        image_data = response.read()
        print(f"Success! Got {len(image_data)} bytes")
        b64 = base64.b64encode(image_data).decode()
        data_url = f"data:image/jpeg;base64,{b64}"
        print(f"Data URL starts with: {data_url[:60]}")
except Exception as e:
    print(f"FAILED: {e}")