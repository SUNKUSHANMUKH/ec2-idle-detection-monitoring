import boto3
from datetime import datetime, timedelta, timezone

# ----------------------------
# Configuration
# ----------------------------
INSTANCE_ID = "i-xxxxxxxxxxxxxxxxx"   # <-- replace with your Instance ID
START_DAYS = 7                        # last X days for EC2 cost calculation
CPU_THRESHOLD = 10                    # %
NETWORK_THRESHOLD = 10                # MB
REGION = "ap-south-1"                 # replace as needed
# ----------------------------

cloudwatch = boto3.client("cloudwatch", region_name=REGION)
ce = boto3.client("ce")


# ----------------------------------------------------
# Get Average CPU Utilization
# ----------------------------------------------------
def get_cpu_usage(instance_id):
    end = datetime.now(timezone.utc)
    start = end - timedelta(hours=1)  # last 1 hour

    response = cloudwatch.get_metric_statistics(
        Namespace="AWS/EC2",
        MetricName="CPUUtilization",
        Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
        StartTime=start,
        EndTime=end,
        Period=300,
        Statistics=["Average"]
    )

    data = response.get("Datapoints", [])
    if not data:
        return 0

    return round(data[-1]["Average"], 2)


# ----------------------------------------------------
# Get Network IN & OUT usage
# ----------------------------------------------------
def get_network_usage(instance_id):
    end = datetime.now(timezone.utc)
    start = end - timedelta(hours=1)

    def fetch_metric(metric):
        resp = cloudwatch.get_metric_statistics(
            Namespace="AWS/EC2",
            MetricName=metric,
            Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
            StartTime=start,
            EndTime=end,
            Period=300,
            Statistics=["Sum"]
        )
        points = resp.get("Datapoints", [])
        if not points:
            return 0
        return round(points[-1]["Sum"] / (1024 * 1024), 2)  # Convert bytes → MB

    net_in = fetch_metric("NetworkIn")
    net_out = fetch_metric("NetworkOut")

    return net_in, net_out


# ----------------------------------------------------
# Get Total EC2 Cost for last X days
# ----------------------------------------------------
def get_cost(start_days):
    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=start_days)

    response = ce.get_cost_and_usage(
        TimePeriod={
            "Start": str(start),
            "End": str(end)
        },
        Granularity="DAILY",
        Metrics=["UnblendedCost"],
        Filter={
            "Dimensions": {
                "Key": "SERVICE",
                "Values": ["Amazon Elastic Compute Cloud - Compute"]
            }
        }
    )

    total_cost = 0.0
    for day in response["ResultsByTime"]:
        total_cost += float(day["Total"]["UnblendedCost"]["Amount"])

    return round(total_cost, 4)


# ----------------------------------------------------
# Main Execution
# ----------------------------------------------------
if __name__ == "__main__":
    print("\n--- EC2 Usage Report ---")

    cpu = get_cpu_usage(INSTANCE_ID)
    net_in, net_out = get_network_usage(INSTANCE_ID)
    cost = get_cost(START_DAYS)

    print(f"Instance ID: {INSTANCE_ID}")
    print(f"CPU Usage (avg last 1 hr): {cpu}%")
    print(f"Network In (MB): {net_in}")
    print(f"Network Out (MB): {net_out}")
    print(f"EC2 Cost (last {START_DAYS} days): ${cost}")

    # Evaluation
    if cpu < CPU_THRESHOLD and net_in < NETWORK_THRESHOLD and net_out < NETWORK_THRESHOLD:
        print("\nStatus: Instance appears **underutilized**. Consider downsizing or stopping.")
    else:
        print("\nStatus: Instance utilization is normal.")
