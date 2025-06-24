# Example: How to request this GET endpoint using Python requests
import requests

url = "http://localhost:8001/files/zip/receipts/20250623T122000"
response = requests.get(url)

if response.status_code == 200:
    with open("data/downloaded_files_receipts.zip", "wb") as f:
        print(response)
        f.write(response.content)
    print("Downloaded zip file saved as downloaded_files.zip")
else:
    print(f"Failed to download: {response.status_code} - {response.text}")