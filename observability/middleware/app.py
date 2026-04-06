from flask import Flask, request, jsonify
import requests, os

app = Flask(__name__)

SNOW_URL = os.getenv("SNOW_URL")
USER = os.getenv("SNOW_USER")
PASS = os.getenv("SNOW_PASS")

HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

def find_ticket(service):
    url = f"{SNOW_URL}/api/now/table/incident"
    query = f"short_descriptionLIKE500 error - {service}^state!=7"
    res = requests.get(url, auth=(USER, PASS), headers=HEADERS, params={"sysparm_query": query})
    data = res.json()
    return data["result"][0]["sys_id"] if data["result"] else None

def create_ticket(service, msg):
    url = f"{SNOW_URL}/api/now/table/incident"
    payload = {"short_description": f"500 error - {service}", "description": msg, "urgency": "1"}
    requests.post(url, json=payload, auth=(USER, PASS), headers=HEADERS)

def update_ticket(sys_id, msg):
    url = f"{SNOW_URL}/api/now/table/incident/{sys_id}"
    payload = {"work_notes": msg}
    requests.patch(url, json=payload, auth=(USER, PASS), headers=HEADERS)

@app.route('/alert', methods=['POST'])
def alert():
    data = request.json
    service = data['alerts'][0]['labels'].get('service', 'unknown')
    message = data['alerts'][0]['annotations']['description']
    existing = find_ticket(service)
    if existing:
        update_ticket(existing, message)
        return {"status": "updated"}
    else:
        create_ticket(service, message)
        return {"status": "created"}

app.run(host='0.0.0.0', port=5000)
