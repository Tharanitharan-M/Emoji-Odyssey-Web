# 🚀 Emoji Odyssey - Web Game (Flask + Supabase)

## 📌 Project Overview
Emoji Odyssey is a **web-based game** where players guess words based on emoji clues. This project is built using **Flask (Backend), Supabase (Database & Auth), and React (Frontend - coming soon!)**. It features:
- 🔐 **User Authentication (Signup & Login)** via Supabase
- 🏆 **Leaderboard with Ranking & Pagination**
- 🎯 **Score Submission API (Cumulative Scoring)**
- ⏳ **Token-based Authentication (JWT)**

## 🛠️ Tech Stack
- **Backend:** Flask, Supabase, Python
- **Database:** Supabase PostgreSQL
- **Authentication:** Supabase Auth (JWT-based)
- **Frontend:** React (Planned)
- **Hosting:** Vercel (Frontend), Render/Supabase Edge (Backend)

---

## 📥 Installation & Setup

### 1️⃣ **Clone the Repository**
```bash
git clone https://github.com/Tharanitharan-M/Emoji-Odyssey-Web.git
cd emoji-odyssey
```

### 2️⃣ **Create & Activate Virtual Environment**
```bash
python -m venv venv  # Create virtual environment
source venv/bin/activate  # Activate on Mac/Linux
venv\Scripts\activate  # Activate on Windows
```

### 3️⃣ **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 4️⃣ **Set Up Environment Variables** (`.env`)
Create a `.env` file in the project root and add:
```plaintext
SUPABASE_URL=https://your-supabase-url.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_JWT_SECRET=your-supabase-jwt-secret
```

### 5️⃣ **Run Flask Server**
```bash
python app.py
```

---

## 📌 API Documentation

### 🔹 **1. User Authentication**
#### 🔹 Signup - `POST /signup`
**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```
**Response:**
```json
{
  "message": "User created successfully!"
}
```

#### 🔹 Login - `POST /login`
**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```
**Response:**
```json
{
  "token": "your-jwt-token"
}
```

---

### 🏆 **2. Leaderboard APIs**

#### 🔹 Submit Score - `POST /submit_score`
🔐 **Requires Token** (Include `Authorization: Bearer <token>` header)

**Request Body:**
```json
{
  "score": 50
}
```
**Response:**
```json
{
  "message": "Score updated successfully!",
  "total_score": 150
}
```

#### 🔹 Get Leaderboard - `GET /leaderboard?page=1&per_page=10`
**Response:**
```json
{
  "leaderboard": [
    {
      "rank": 1,
      "user_id": "5bbf0ca5-d80d-44ed-890e-1c02d69379be",
      "total_score": 200,
      "latest_timestamp": 1712136784
    }
  ],
  "page": 1,
  "per_page": 10,
  "total_entries": 15,
  "total_pages": 2
}
```

---

## 🔄 Future Improvements
- 🎨 **Frontend React UI** for better user experience
- 🎮 **Multiplayer Mode** (Real-time rooms & competition)
- 🎭 **Emoji Customization** for player avatars
- 📊 **Admin Dashboard** for managing users & scores

## 📜 License
This project is **open-source** under the MIT License.

## 💬 Need Help?
For questions, feel free to **open an issue** or reach out on [GitHub](https://github.com/yourusername/emoji-odyssey). 🚀
