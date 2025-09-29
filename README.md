
# EKS AI Dashboard

## Executive Summary

The **EKS AI Dashboard** is a unified platform for real-time monitoring and intelligent diagnostics of Kubernetes workloads running on AWS EKS. It combines infrastructure-as-code provisioning (Terraform) with a Python Flask web application, enabling DevOps teams to automate cluster deployment, monitor pod health, receive AI-powered troubleshooting, and get automated alerts for critical issues. This solution accelerates incident response, reduces manual troubleshooting, and empowers teams with AI-driven insights, making Kubernetes operations more resilient and efficient.


<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/934d82d6-5cf7-4622-9fa1-8bfd0967a298" />


---

## Features

- **Automated EKS Cluster Deployment:**  
  Terraform scripts provision secure, production-ready EKS clusters, including networking, IAM roles, and a sample Nginx workload.

- **Real-Time Pod Monitoring:**  
  The dashboard displays live pod status, restart counts, and error diagnostics across all namespaces.

- **AI-Powered Troubleshooting:**  
  Uses Azure OpenAI (GPT-4o) to analyze pod logs and manifests, providing actionable recommendations for resolving errors and exceptions.

- **Automated Email Alerts:**  
  Critical issues trigger email notifications to designated recipients, ensuring rapid response and minimizing downtime.

- **Secure & Extensible Architecture:**  
  Sensitive credentials are managed via environment variables, with recommendations to use secret managers for production. The modular design allows easy extension to other cloud providers or AI models.

---

## Repository Structure

```
eks-ai-dashboard/
├── eks.py
├── requirements.txt
├── start.sh
├── stop.sh
├── dashboard.html
├── flask.log
├── venv/                # (add to .gitignore)
├── .env                 # (add to .gitignore)
├── terraform_eks_provision/
│   ├── main.tf
│   ├── variables.tf
│   ├── terraform.tfstate
│   ├── terraform.tfstate.backup
├── README.md
├── .gitignore
```

---

## Getting Started

### Prerequisites

- Python 3.8+
- Terraform
- AWS CLI
- kubectl

### Setup Instructions

#### 1. **Clone the Repository**

```bash
git clone https://github.com/<your-username>/eks-ai-dashboard.git
cd eks-ai-dashboard
```

#### 2. **Configure Environment Variables**

Create a `.env` file in the root directory with the following content (replace placeholders with your actual values):

```ini
AZURE_API_KEY="your-azure-api-key"
AZURE_API_BASE="https://your-resource.openai.azure.com"
AZURE_API_VERSION="2024-08-01-preview"
AZURE_DEPLOYMENT_MODEL="gpt-4o"

EMAIL_SENDER="your-email@gmail.com"
EMAIL_PASSWORD="your-email-password"
EMAIL_RECEIVER="recipient1@mail.com,recipient2@mail.com"
```

> **Note:** Never commit your `.env` file to GitHub.

#### 3. **Install Python Dependencies**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 4. **Provision EKS Cluster with Terraform**

```bash
cd terraform_eks_provision
terraform init
terraform apply
```

- Review and confirm the changes when prompted.
- This will create the EKS cluster, networking, IAM roles, and deploy a sample Nginx workload.

#### 5. **Start the Flask App**

```bash
./start.sh
```

- The app will run in the background on port 5001.
- Logs are written to `flask.log`.

#### 6. **Access the Dashboard**

Open your browser and go to:

```
http://<server-ip>:5001/eks_dashboard/
```

---

## Usage

- **Dashboard:**  
  - Select a namespace to view pod status.
  - See restart counts, error diagnostics, and AI feedback for each pod.
  - AI diagnostics are generated using Azure OpenAI and displayed for pods with errors or exceptions.

- **Email Alerts:**  
  - When a new issue is detected, an email is sent to the configured recipients.
  - Alerts are throttled to avoid spamming.

- **Terraform:**  
  - Easily customize cluster parameters in `variables.tf`.
  - Extend `main.tf` to add more resources or workloads.

---

## Security Notes

- **Do NOT commit `.env`, `venv/`, or Terraform state files (`terraform.tfstate*`) to GitHub.**
- Use a `.gitignore` file with:
  ```
  venv/
  .env
  flask.log
  terraform_eks_provision/terraform.tfstate*
  ```
- For production, use a secrets manager (e.g., HashiCorp Vault, AWS Secrets Manager) instead of plaintext `.env` files.
- Rotate credentials regularly and follow cloud provider security best practices.

---

## Extending the Solution

- **Add more AI models:**  
  Swap out the Azure OpenAI integration for other providers or models as needed.

- **Integrate with other notification channels:**  
  Extend email alerts to Slack, Teams, or SMS.

- **Customize Terraform modules:**  
  Add more resources, workloads, or security controls.

---

Certainly! Here’s a **Benefits & Differentiators** section in README format, ready to copy-paste into your repository:

---

## Benefits & Differentiators

### Why is this Solution Required?

- **Proactive Incident Response:**  
  Unlike traditional Kubernetes monitoring tools that require manual log inspection and troubleshooting, this solution uses AI to automatically analyze logs and manifests, providing instant, actionable recommendations. This reduces downtime and accelerates root cause analysis.

- **Unified Monitoring & Automation:**  
  Combines real-time pod status, error detection, and automated alerting in a single dashboard. No need to juggle multiple tools or dashboards.

- **End-to-End Automation:**  
  From infrastructure provisioning (Terraform) to AI-powered diagnostics and notification, the entire workflow is automated—saving time and reducing human error.

- **Scalable & Extensible:**  
  Easily adapts to new clusters, workloads, or cloud providers. Modular design allows integration with other AI models, notification channels (Slack, Teams), or secret managers.

- **Security Best Practices:**  
  Credentials are managed via environment variables, with recommendations for using Vault/AWS Secrets Manager in production. This is more secure than hardcoding secrets or using plaintext files.

---

### How is this Different from Other Solutions?

- **AI-Powered Troubleshooting:**  
  Most dashboards only show metrics and logs. This solution leverages Azure OpenAI (GPT-4o) to interpret logs and suggest fixes, going beyond simple visualization.

- **Automated Email Alerts:**  
  Issues trigger intelligent, throttled notifications to the right people—no need for manual monitoring or custom scripts.

- **Infrastructure as Code:**  
  Terraform scripts ensure repeatable, version-controlled cluster provisioning, unlike manual setup or click-based cloud consoles.

- **Customizable & Open Source:**  
  You can extend the dashboard, AI logic, or infrastructure modules to fit your organization’s needs. No vendor lock-in.

- **Integrated Workflow:**  
  Everything from cluster setup to monitoring, diagnostics, and alerting is managed in one solution—streamlining DevOps operations.

---

**In summary:**  
The EKS AI Dashboard empowers teams to move from reactive to proactive operations, leveraging AI for smarter troubleshooting, and automating the entire lifecycle from infrastructure to incident response. This is a leap beyond traditional monitoring tools, making Kubernetes management faster, smarter, and more secure.


