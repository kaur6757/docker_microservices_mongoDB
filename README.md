# 🏦 Microservices-Based Bank Letter Processing System

A distributed microservices application that processes customer data, validates records, and generates personalized bank letters using Docker and MongoDB.

---

## 🚀 Project Overview

This project demonstrates a **microservices architecture** where multiple independent services work together to process customer records and generate:

- 📄 Welcome Letters
- 💳 Offer Letters

The system validates input data, routes requests between services, and stores processing logs in MongoDB.

---

## 🧠 Architecture

Customer Data (JSON)
↓
Validation Service
↓

| |
Welcome Service Offer Service
| |
Generate Letters Generate Letters
↓
MongoDB (Logs Storage)


---

## ⚙️ Technologies Used

- 🐍 Python (Flask)
- 🐳 Docker & Docker Compose
- 🍃 MongoDB
- 🌐 REST APIs (HTTP communication)
- 📁 JSON Data Processing

---

## 🔧 Microservices

### 1️⃣ Validation Service
- Reads customer data from JSON
- Validates records
- Sends valid records to appropriate service
- Stores logs in MongoDB
- Saves invalid records to JSON

### 2️⃣ Welcome Service
- Generates welcome letters
- Uses text templates
- Saves output to files

### 3️⃣ Offer Service
- Generates offer letters
- Handles credit-related offers
- Saves output to files

---

## 🔁 Communication Method

Services communicate using **HTTP REST APIs between Docker containers**.

Example:

Validation → Welcome Service
POST http://welcome_service:5001/process


---

## 🗄️ Database (MongoDB)

MongoDB is used to store:

- Validation logs (valid/invalid records)
- Processed customer data

---

## ▶️ How to Run the Project

### Step 1: Clone the repo
```bash
git clone https://github.com/abkaur/microservices-bank-letter-system.git
cd microservices-bank-letter-system
Step 2: Run Docker
docker compose up --build
📂 Output
Generated Letters:
output_letters/
Invalid Records:
invalid_records_log.json
🧪 Sample Input

Customer data is read from:

customers.json
📊 MongoDB Verification

To verify database:

docker exec -it mongodb mongosh

Then run:

use bank_db
show collections
db.validation_logs.find().pretty()


🎯 Key Features

✔ Microservices architecture
✔ Containerized using Docker
✔ Inter-service communication
✔ Data validation pipeline
✔ MongoDB integration
✔ File-based output generation

🌟 Future Improvements

Add RabbitMQ for async communication
Deploy on AWS (ECS / EKS)
Add frontend dashboard
Add API Gateway
