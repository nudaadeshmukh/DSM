# Supply Chain Optimization & Inventory Management System

## 📌 Project Overview

This project is a web-based system designed to optimize inventory management and transportation decisions in a retail supply chain.

It integrates:

- **Economic Order Quantity (EOQ)**
- **Reorder Point (ROP)**
- **Shortest Path Optimization (Dijkstra Algorithm)**

**Goal**: Minimize total cost while ensuring continuous product availability across suppliers, warehouses and retailers.

---

## 🎯 Objectives

- Minimize total inventory and transportation cost
- Compute optimal order quantity using EOQ
- Prevent stockouts using Reorder Point (ROP)
- Determine least-cost transportation path using graph algorithms
- Provide a user-friendly interface for data input and results visualization

---

## 🧠 Mathematical Model

### 🔹 EOQ (Economic Order Quantity)

```
Q* = √(2DS/H)
```

### 🔹 Reorder Point (ROP)

```
ROP = d × L
```

### 🔹 Total Cost Function

```
TC = (D/Q)S + (Q/2)H + Transportation Cost
```

### 🔹 Graph Model

- **Nodes**: Suppliers, Warehouses, Retailers
- **Edges**: Transportation routes
- **Weight**: Cost of transportation

---

## 🏗️ System Architecture

```
Frontend (HTML/CSS/JS)
         ↓
Backend (Flask API)
         ↓
Optimization Engine (EOQ + ROP + Dijkstra)
         ↓
Database (SQLite)
```

---

## 💻 Tech Stack

### 🔹 Frontend

- HTML
- CSS
- JavaScript

### 🔹 Backend

- Python (Flask)

### 🔹 Database

- SQLite

### 🔹 Algorithms

- EOQ Model
- Reorder Point Calculation
- Dijkstra's Algorithm

---

## 📂 Project Structure

```
supply-chain-optimizer/
│
├── backend/
│   ├── app.py
│   ├── services/
│   ├── routes/
│   ├── models/
│   └── database/
│
├── frontend/
│   ├── pages/
│   ├── css/
│   └── js/
│
└── README.md
```

---

## ⚙️ Features

- User authentication (Login/Register)
- Input supply chain data (demand, cost, routes)
- Automatic EOQ & ROP calculation
- Shortest path computation for transportation
- Total cost analysis
- Results visualization

---

## 🚀 How to Run the Project

### 1️⃣ Clone the repository

```bash
git clone <your-repo-url>
```

### 2️⃣ Setup Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

### 3️⃣ Connect existing MySQL database

Create `backend/.env` from `backend/.env.example` and update:

```env
DB_BACKEND=mysql
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=your_db_name
INIT_DB_ON_STARTUP=false
```

Notes:

- `INIT_DB_ON_STARTUP=false` is recommended when your schema already exists.
- If you want the app to bootstrap tables for a fresh DB, set `INIT_DB_ON_STARTUP=true`.

### 4️⃣ Open Frontend

Open `frontend/pages/login.html` in browser  
**OR**  
Use Live Server (recommended)

---

## 🧪 Postman Testing (after DB population)

Base URL: `http://127.0.0.1:5000`

1. Register user  
   `POST /api/auth/register`

   ```json
   {
     "username": "testuser",
     "email": "test@example.com",
     "password": "secret123",
     "confirm_password": "secret123"
   }
   ```

2. Login (use Postman cookie jar/session)  
   `POST /api/auth/login`

   ```json
   {
     "email_or_username": "testuser",
     "password": "secret123"
   }
   ```

3. Populate master data
   - `POST /api/supply-chain/suppliers`
   - `POST /api/supply-chain/warehouses`
   - `POST /api/supply-chain/retailers`
   - `POST /api/supply-chain/products`
   - `POST /api/supply-chain/inventory`
   - `POST /api/supply-chain/routes` with:

   ```json
   {
     "source_id": 1,
     "destination_id": 1,
     "source_type": "S",
     "destination_type": "W",
     "cost": 120
   }
   ```

4. Run optimization  
   `POST /api/optimize`

   ```json
   {
     "demand": 1000,
     "ordering_cost": 50,
     "holding_cost": 2,
     "lead_time": 5,
     "start_node": "S1",
     "end_node": "R1"
   }
   ```

5. Verify stored results
   - `GET /api/results/`
   - `GET /api/results/latest`

---

## 📊 Example Input/Output

**Example Input:**

```json
{
  "demand": 1000,
  "ordering_cost": 50,
  "holding_cost": 2,
  "lead_time": 5
}
```

**Example Output:**

```json
{
  "eoq": 224,
  "rop": 50,
  "shortest_path": ["Supplier", "Warehouse", "Retailer"],
  "total_cost": 5000
}
```

---

## 👥 Team Responsibilities

- **Riya Kumbhoje** – Frontend Developer  
  UI & user interaction
- **Gargi Joshi** – Backend Developer  
  API & server logic
- **Nudaa Deshmukh** – Optimization Engineer  
  EOQ, ROP, Graph algorithms
- **Koyal Kembhavi** – Database Engineer  
  Schema & data management
