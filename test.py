import requests
import urllib.parse

# Define the API URL
url = "https://cloud.google.com/products/calculator/your-endpoint"  # Replace with the actual endpoint URL

# Headers (replace/add any headers required by the API)
headers = {
    "Content-Type": "application/json",
    "hl": "en"
}

# Decode the `f.req` parameter from URL-encoded to its original form
f_req_encoded = "%5B%5B%5B%22jUj4td%22%2C%22%5Bnull%2Cnull%2Cnull%2C%5C%22CiQ0YjNhYTU3NS0yYTdmLTQwZjQtYTg4NC03MmJjZDkzZWM5MDYQAQ%3D%3D%5C%22..."
f_req_decoded = urllib.parse.unquote(f_req_encoded)

# Define the payload
payload = {
    "rpcids": "jUj4td",
    "source-path": "/products/calculator",
    "f.sid": "-7798812777053225354",
    "bl": "boq_cloud-ux-webapp-cgc-ui_20250120.05_p0",
    "hl": "en",
    "soc-app": 1,
    "soc-platform": 1,
    "soc-device": 1,
    "_reqid": 642869,
    "rt": "c",
    "f.req": f_req_decoded,  # Insert the decoded `f.req` value
}

# Send the POST request
response = requests.post(url, headers=headers, json=payload)

# Print the response
print("Status Code:", response.status_code)
print("Response Text:", response.text)
