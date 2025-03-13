
# 🚀 Emoji Odyssey - Multiplayer & Single Player Web Game (React + Flask + Supabase)

## 📌 Project Overview
**Emoji Odyssey** is a fully completed **multiplayer and single-player web game** where players guess words based on emoji clues. It features **real-time gameplay, score tracking, leaderboards, and chat functionality**. Built using **React** for the frontend, **Flask** for the backend, and **Supabase** for database, authentication, and real-time capabilities.

---

### 🎮 Key Features
- 🔐 **User Authentication** (Signup & Login) via Supabase  
- 🎯 **Single Player Mode** with progressive levels and scoring  
- ⚔️ **Multiplayer Mode** with room creation, joining, and real-time scoring  
- 💬 **Real-Time Chat** within multiplayer rooms  
- 🏆 **Leaderboard System** to track top scores for both modes  
- ⚡ **Real-Time Updates** for scores and gameplay events  
- 🧹 **Automatic Room Cleanup** after game completion  
- 🛠️ **Efficient Storage Management**  

---

## 🛠️ Tech Stack
| Component       | Tech Used                        |
|-----------------|---------------------------------|
| **Frontend**    | React, Tailwind CSS              |
| **Backend**     | Flask, Python                    |
| **Database**    | Supabase PostgreSQL              |
| **Authentication** | Supabase Auth (JWT-based)      |
| **Real-Time**   | Supabase Realtime                |
---

## 📥 Installation & Setup

### 1️⃣ **Clone the Repository**
```bash
git clone https://github.com/Tharanitharan-M/Emoji-Odyssey-Web.git
cd emoji-odyssey
```

### 2️⃣ **Frontend Setup**
```bash
cd frontend
npm install
npm run dev
```

### 3️⃣ **Backend Setup**
```bash
cd ../backend
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate       # Windows
pip install -r requirements.txt
python app.py
```

### 4️⃣ **Set Up Environment Variables** (`.env`)
Create `.env` files in both `frontend` and `backend` directories.

**Backend `.env`**
```env
SUPABASE_URL=https://your-supabase-url.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_JWT_SECRET=your-supabase-jwt-secret
```

**Frontend `.env`**
```env
NEXT_PUBLIC_SUPABASE_URL=https://your-supabase-url.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
```

---

## 📌 Gameplay Flow

### 🎯 **Single Player Mode**
1. **Select Genre** → Choose from Movies, Phrases, etc.  
2. **Solve Levels** → Progress through levels by solving emoji puzzles.  
3. **Level Unlocking** → Unlock the next level after solving the previous one.  
4. **Scoring** → Scores are calculated per genre and displayed on the leaderboard.

---

### ⚔️ **Multiplayer Mode**
1. **Create or Join Room** → Hosts create a room with a specific number of rounds or players join using a room code.  
2. **Start Game** → Host starts the game, and a random emoji puzzle is presented.  
3. **Real-Time Gameplay** → Players submit answers, with faster responses earning more points.  
4. **Chat Functionality** → Players can communicate in real-time during the game.  
5. **Leaderboard** → Scores are updated in real-time, and the top players are ranked.

---

## 📌 API Overview

### 🎯 **Single Player APIs**
- `POST /singleplayer/get_genres` → Fetch available genres.  
- `GET /singleplayer/get_levels/<user_id>/<genre>` → Get levels for a user in a genre.  
- `POST /singleplayer/submit_answer` → Submit an answer for a level.  
- `GET /singleplayer/get_score/<user_id>/<genre>` → Fetch scores for a user in a specific genre.

---

### ⚔️ **Multiplayer APIs**
- `POST /multiplayer/create_room` → Create a new multiplayer room.  
- `POST /multiplayer/join_room` → Join an existing room using a room code.  
- `POST /multiplayer/start_game` → Start the game and fetch the first question.  
- `POST /multiplayer/submit_answer` → Submit an answer for a question.  
- `GET /multiplayer/get_scores/<room_id>` → Get player scores for a room.  
- `GET /multiplayer/get_players/<room_id>` → Get players in a room.

---

### 🏆 **Leaderboard APIs**
- `GET /leaderboard/singleplayer` → Fetch top players for single player mode.  
- `GET /leaderboard/multiplayer` → Fetch top players for multiplayer mode.

---

## ✅ Key Highlights of the Project
- 🔄 **Real-Time Gameplay** with dynamic score updates.  
- 🧩 **Randomized Emoji Puzzles** for fresh gameplay every round.  
- ⚔️ **Multiplayer & Single Player Modes** with integrated scoring.  
- 🏆 **Leaderboard Tracking** for both modes.  
- ⚡ **Real-Time Chat** to enhance multiplayer engagement.  
- 🧹 **Automatic Room Cleanup** to optimize storage.

---

## 🔄 Future Enhancements (Optional)
- 🎨 **Custom Player Avatars & Profiles**.  
- 🏆 **Seasonal Leaderboards** with resets.  
- 📈 **Analytics Dashboard** for tracking player stats.  
- 🌐 **Global Chat System** for inter-room conversations.

---

## 📜 License
This project is licensed under the **MIT License**.  
Feel free to contribute and enhance the gameplay! 🚀

---

## 💬 Need Help?
For questions, feel free to **open an issue** or reach out on [GitHub](https://github.com/Tharanitharan-M/Emoji-Odyssey-Web). 🚀
