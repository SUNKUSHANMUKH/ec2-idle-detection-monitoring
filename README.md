# EC2 Monitoring Script

## Overview
This Python script monitors an AWS EC2 instance and provides:
- Average CPU utilization (last 1 hour)
- Network In and Out (last 1 hour)
- EC2 service cost (last X days)
- Status evaluation (underutilized or normal)

It uses Python 3, boto3, and CloudWatch metrics. Configuration is via a `.env` file.

## Prerequisites
- AWS IAM Role or Credentials with minimal EC2, CloudWatch, and Cost Explorer permissions.
- Python 3 installed
- Internet access from EC2
- Security Group: SSH inbound, HTTPS outbound

## Setup Instructions
1. SSH into EC2 instance.
2. Install Python and dependencies:
```
sudo apt update
sudo apt install -y python3 python3-venv python3-pip unzip curl
```
3. Create virtual environment:
```
python3 -m venv myenv
source myenv/bin/activate
```
4. Install dependencies:
```
pip install --upgrade pip
pip install -r requirements.txt
```
5. Configure `.env` with your instance details.

## Running the Script
```
source myenv/bin/activate
python3 ec2_usage_check.py
```

## Optional Testing
- Generate CPU load:
```
sudo apt install stress -y
stress --cpu 2 --timeout 120s
```
- Generate network load:
```
curl -O https://speed.hetzner.de/100MB.bin
```

## Notes
- `.env` separates configuration from code
- Metrics are read directly from CloudWatch
- EC2 cost is service-level, not per-instance
