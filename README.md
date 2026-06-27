# 🚨 Kubernetes CrashLoopBackOff Troubleshooting Lab

A hands-on Kubernetes lab designed to simulate and troubleshoot a **CrashLoopBackOff** scenario caused by an application failing to connect to its PostgreSQL database during startup.

This project demonstrates how to investigate pod failures using common Kubernetes debugging commands and understand the CrashLoopBackOff lifecycle.

---

## 📌 Objectives

- Deploy a PostgreSQL database
- Deploy a Python Flask application
- Connect the application to PostgreSQL
- Intentionally break the application
- Observe Kubernetes restarting the container
- Investigate the failure using Kubernetes troubleshooting techniques
- Restore the application

---

## 🏗️ Architecture

```
                +----------------+
                |   Client       |
                +--------+-------+
                         |
                         |
                 Kubernetes Service
                         |
                         ▼
                +----------------+
                | Payment API    |
                | Flask + Python |
                +--------+-------+
                         |
                    PostgreSQL
                         |
                         ▼
                +----------------+
                | paymentdb      |
                +----------------+
```

---

## 📁 Project Structure

```
11-crashloop/
│
├── app/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── k8s/
│   ├── namespace.yaml
│   ├── postgres.yaml
│   ├── postgres-service.yaml
│   ├── payment-deployment.yaml
│   └── payment-service.yaml
│
└── README.md
```

---

## 🛠️ Technologies Used

- Kubernetes (Kind)
- Docker
- Python 3
- Flask
- PostgreSQL 16
- kubectl

---

# Deployment

## 1. Create Kind Cluster

```bash
kind create cluster --name incident-lab
```

---

## 2. Create Namespace

```bash
kubectl apply -f k8s/namespace.yaml
```

---

## 3. Deploy PostgreSQL

```bash
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/postgres-service.yaml
```

Verify

```bash
kubectl get pods -n crashloop-lab
```

---

## 4. Build Application

```bash
docker build -t payment-service:v1 ./app
```

Load into Kind

```bash
kind load docker-image payment-service:v1 --name incident-lab
```

---

## 5. Deploy Payment Service

```bash
kubectl apply -f k8s/payment-deployment.yaml
kubectl apply -f k8s/payment-service.yaml
```

---

## Verify

```bash
kubectl get pods -n crashloop-lab
```

Expected

```
postgres        Running
payment         Running
```

---

# Verify PostgreSQL

Connect

```bash
kubectl exec -it \
$(kubectl get pod -n crashloop-lab -l app=postgres -o jsonpath='{.items[0].metadata.name}') \
-n crashloop-lab -- \
psql -U admin -d paymentdb
```

Check version

```sql
SELECT version();
```

---

# Simulating CrashLoopBackOff

Scale PostgreSQL down

```bash
kubectl scale deployment postgres \
--replicas=0 \
-n crashloop-lab
```

Delete the payment pod

```bash
kubectl delete pod \
-l app=payment \
-n crashloop-lab
```

Kubernetes recreates the pod.

Since PostgreSQL is unavailable, the application exits during startup.

Result

```
CrashLoopBackOff
```

---

# Investigation

## Check Pods

```bash
kubectl get pods -n crashloop-lab
```

---

## Describe Pod

```bash
kubectl describe pod <payment-pod> \
-n crashloop-lab
```

---

## View Logs

```bash
kubectl logs <payment-pod> \
-n crashloop-lab
```

Expected

```
Database connection failed
Connection refused
```

---

## Watch Restart Count

```bash
kubectl get pods -n crashloop-lab -w
```

Observe

```
RESTARTS
1
2
3
4
...
```

---

# Root Cause

The Flask application attempts to establish a PostgreSQL connection during startup.

When PostgreSQL is unavailable, the application exits with a non-zero status.

Kubernetes interprets this as a container failure and continuously restarts the pod.

Eventually, Kubernetes backs off between restart attempts and the pod enters the **CrashLoopBackOff** state.

---

# Recovery

Restore PostgreSQL

```bash
kubectl scale deployment postgres \
--replicas=1 \
-n crashloop-lab
```

Delete the failed application pod

```bash
kubectl delete pod \
-l app=payment \
-n crashloop-lab
```

Verify

```bash
kubectl get pods -n crashloop-lab
```

Expected

```
postgres     Running
payment      Running
```

---

# Troubleshooting Commands

List pods

```bash
kubectl get pods -n crashloop-lab
```

Describe pod

```bash
kubectl describe pod <pod-name> -n crashloop-lab
```

View logs

```bash
kubectl logs <pod-name> -n crashloop-lab
```

Watch pods

```bash
kubectl get pods -w
```

Restart deployment

```bash
kubectl rollout restart deployment payment -n crashloop-lab
```

---

# Learning Outcomes

After completing this lab, you should be able to:

- Understand how CrashLoopBackOff occurs
- Debug Kubernetes application failures
- Interpret pod events
- Inspect container logs
- Analyze restart counts
- Identify root causes
- Restore failed workloads
- Apply systematic Kubernetes troubleshooting techniques

---

## 📚 References

- Kubernetes Documentation
- Docker Documentation
- PostgreSQL Documentation
- Flask Documentation

---

## 👨‍💻 Author

**Kowshik Thiruppathi**

Computer Science Engineering (Cyber Security)

Built as part of a Kubernetes troubleshooting and incident response practice series.
