# WellNest 🌿

> **A holistic approach to health tracking.**
> Track your calories, monitor your weight, and visualize your progress with a modern, premium interface.


## ✨ Features

- **📊 Interactive Dashboard**: Get a quick summary of your daily intake and weight trends.
- **🍎 Food Logging**: Easily log meals with calorie counts.
- **⚖️ Weight Tracking**: Record your weight and view your history on beautiful, interactive charts.
- **🔐 Secure Authentication**: JWT-based secure login and registration system.
- **🌓 Light/Dark Mode**: Seamlessly switch between a clean light theme and a premium dark theme.
- **🎨 Modern UI**: Built with Tailwind CSS and Framer Motion for smooth animations and glassmorphism effects.

## 🛠 Tech Stack

### Frontend
- **Framework**: React 19 (Vite)
- **Styling**: Tailwind CSS v3
- **Animations**: Framer Motion
- **Charts**: Recharts
- **Icons**: Lucide React
- **Routing**: React Router DOM v7

### Backend
- **Framework**: FastAPI
- **Database**: SQLite (Development)
- **ORM**: SQLAlchemy
- **Authentication**: JWT (Python-jose)
- **Validation**: Pydantic v2

## 🚀 Getting Started

Follow these instructions to get the project running on your local machine.

### Prerequisites
- Node.js (v18+)
- Python (v3.10+)

### 1. Backend Setup

Navigate to the backend directory and set up the virtual environment.

```bash
cd wellnest-backend

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r req.txt

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8004
```
The backend API will be available at `http://localhost:8004`.
API Documentation (Swagger): `http://localhost:8004/docs`

### 2. Frontend Setup

Navigate to the frontend directory and install dependencies.

```bash
cd wellnest-frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```
The application will start at `http://localhost:5173` (or the next available port).

## 📂 Project Structure

```
WellNest/
├── wellnest-backend/     # FastAPI Backend
│   ├── app/
│   │   ├── api/          # API Routes (Auth, Health)
│   │   ├── core/         # Config & Security
│   │   ├── models.py     # Database Models
│   │   └── schemas.py    # Pydantic Schemas
│   └── ...
│
└── wellnest-frontend/    # React Frontend
    ├── src/
    │   ├── components/   # Reusable Components (Charts, Forms)
    │   ├── context/      # Auth & Theme Contexts
    │   ├── pages/        # Application Pages (Login, Dashboard)
    │   └── ...
    └── ...
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.
