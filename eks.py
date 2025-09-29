
import subprocess, os, smtplib, json, time, hashlib
from flask import Flask, request
from email.mime.text import MIMEText
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()
app = Flask(__name__)
sent_alerts = {}
feedback_cache = {}

DEFAULT_NAMESPACE = os.getenv("KUBERNETES_NAMESPACE", "default")
ALERT_TTL_SECONDS = 3600

client = AzureOpenAI(
    api_key=os.getenv("AZURE_API_KEY"),
    api_version=os.getenv("AZURE_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_API_BASE")
)

def get_namespaces():
    result = subprocess.run(["kubectl", "get", "namespaces", "-o", "json"], capture_output=True, text=True)
    items = json.loads(result.stdout)["items"]
    return [ns["metadata"]["name"] for ns in items]

def get_pods(namespace):
    try:
        result = subprocess.run(["kubectl", "get", "pods", "-n", namespace, "-o", "json"], capture_output=True, text=True, check=True)
        return json.loads(result.stdout)["items"]
    except subprocess.CalledProcessError:
        return []

def get_logs(pod_name, namespace):
    result = subprocess.run(["kubectl", "logs", pod_name, "-n", namespace], capture_output=True)
    return result.stdout.decode("utf-8", errors="replace")

def get_manifest(pod_name, namespace):
    result = subprocess.run(["kubectl", "get", "pod", pod_name, "-n", namespace, "-o", "yaml"], capture_output=True)
    return result.stdout.decode("utf-8", errors="replace")

def extract_relevant_logs(logs):
    lines = logs.splitlines()
    filtered = [line for line in lines if "error" in line.lower() or "exception" in line.lower()]
    return "\n".join(filtered[-100:])

def hash_logs(logs):
    return hashlib.md5(logs.encode()).hexdigest()

def analyze_logs(logs, manifest=None):
    trimmed_logs = extract_relevant_logs(logs)
    if not trimmed_logs.strip():
        return "No critical errors or exceptions found in logs."

    context = f"Analyze these logs and suggest fixes:\n{trimmed_logs}"
    if manifest:
        context += f"\n\nHere is the full pod manifest:\n{manifest}"

    response = client.chat.completions.create(
        model=os.getenv("AZURE_DEPLOYMENT_MODEL"),
        messages=[
            {"role": "system", "content": "You're a Kubernetes troubleshooting assistant."},
            {"role": "user", "content": context}
        ]
    )
    return response.choices[0].message.content

def analyze_container_issue(reason, message, manifest=None):
    context = f"Pod is failing with reason: {reason}\nMessage: {message}"
    if manifest:
        context += f"\n\nPod manifest:\n{manifest}"

    response = client.chat.completions.create(
        model=os.getenv("AZURE_DEPLOYMENT_MODEL"),
        messages=[
            {"role": "system", "content": "You're a Kubernetes troubleshooting assistant."},
            {"role": "user", "content": context}
        ]
    )
    return response.choices[0].message.content

def send_email(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = os.getenv("EMAIL_SENDER")
    msg['To'] = os.getenv("EMAIL_RECEIVER")

    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 465))

    with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
        server.login(os.getenv("EMAIL_SENDER"), os.getenv("EMAIL_PASSWORD"))
        server.send_message(msg)

def should_send_alert(key):
    last_sent = sent_alerts.get(key)
    if not last_sent:
        return True
    return (time.time() - last_sent) > ALERT_TTL_SECONDS

@app.route("/eks_dashboard/")
def index():
    return open("dashboard.html").read()

@app.route("/eks_dashboard/namespaces")
def list_namespaces():
    return json.dumps(get_namespaces())

@app.route("/eks_dashboard/data")
def dashboard_data():
    namespace = request.args.get("namespace") or DEFAULT_NAMESPACE
    pods = get_pods(namespace)
    pod_rows = ""
    diagnostics = ""

    for pod in pods:
        name = pod["metadata"]["name"]
        status = pod["status"]["phase"]
        container_statuses = pod["status"].get("containerStatuses", [])
        restarts = sum(int(c.get("restartCount", 0)) for c in container_statuses)
        manifest = get_manifest(name, namespace)

        reason = ""
        message = ""
        for c in container_statuses:
            waiting = c.get("state", {}).get("waiting")
            if waiting:
                reason = waiting.get("reason", "")
                message = waiting.get("message", "")
                break

        if status not in ["Running", "Succeeded", "Failed"] or reason:
            row_color = "#fff3cd"
            status_icon = "⏳"
            issue_key = f"{name}:{reason}:{message}"

            if should_send_alert(issue_key):
                ai_feedback = analyze_container_issue(reason, message, manifest)
                send_email(f"Issue in pod {name}", ai_feedback)
                sent_alerts[issue_key] = time.time()
            else:
                ai_feedback = f"Issue previously reported. Last alert sent: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(sent_alerts[issue_key]))}"

            diagnostics += f"""
            <div style="margin-bottom:20px;">
                <strong>{name}</strong><br>
                <em>Container Issue:</em> {reason}<br>
                <em>Message:</em> {message}<br>
                <em>Last alert sent:</em> {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(sent_alerts[issue_key]))}<br>
                <pre style="background:#f8f8f8; padding:10px; border:1px solid #ccc;">{ai_feedback}</pre>
            </div>
            """
        else:
            logs = get_logs(name, namespace)
            has_error = "error" in logs.lower() or "exception" in logs.lower()
            row_color = "#f8d7da" if has_error else "#d4edda"
            status_icon = "❌" if has_error else "✅"

            if has_error:
                trimmed_logs = extract_relevant_logs(logs)
                error_hash = hash_logs(trimmed_logs)
                if should_send_alert(error_hash):
                    ai_feedback = analyze_logs(logs, manifest)
                    send_email(f"Issue in pod {name}", ai_feedback)
                    sent_alerts[error_hash] = time.time()
                else:
                    ai_feedback = f"Issue previously reported. Last alert sent: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(sent_alerts[error_hash]))}"

                diagnostics += f"""
                <div style="margin-bottom:20px;">
                    <strong>{name}</strong><br>
                    <em>Last alert sent:</em> {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(sent_alerts[error_hash]))}<br>
                    <pre style="background:#f8f8f8; padding:10px; border:1px solid #ccc;">{trimmed_logs}</pre>
                </div>
                """
            else:
                ai_feedback = "No critical issues found."

        pod_rows += f"""
        <tr style="background-color:{row_color};">
            <td>{name}</td>
            <td>{status_icon} {status}</td>
            <td>{restarts}</td>
            <td>{ai_feedback}</td>
        </tr>
        """

    return f"""
    <div id="pod-status">
        <table border="1" cellpadding="6" cellspacing="0" style="width:100%; border-collapse:collapse;">
            <tr style="background-color:#e2e3e5;">
                <th>Pod Name</th><th>Status</th><th>Restarts</th><th>AI Feedback</th>
            </tr>
            {pod_rows}
        </table>
    </div>

    <hr>

    <div id="ai-diagnostics">
        <h2>AI Error Diagnostics</h2>
        {diagnostics if diagnostics else "<p>No errors detected in any pods.</p>"}
    </div>
    """

@app.route("/health")
def health():
    try:
        namespaces = get_namespaces()
        pod_count = sum(len(get_pods(ns)) for ns in namespaces)
        return json.dumps({"status": "OK", "namespaces": len(namespaces), "pods": pod_count}), 200
    except Exception as e:
        return json.dumps({"status": "ERROR", "details": str(e)}), 500

if __name__ == "__main__":
    sent_alerts.clear()
    app.run(debug=True, host="0.0.0.0", port=5001)
