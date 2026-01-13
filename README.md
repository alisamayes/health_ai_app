# Mindful Mäuschen

A comprehensive desktop health tracking application built with Python and PyQt6. Track your calories, exercise, weight goals, and meal plans all in one place with AI-powered features for personalized health advice.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

## Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Requirements](#-requirements)
- [Development Status](#-development-status)
- [Contributing](#-contributing)
- [License](#-license)
- [Author](#-author)

## Features

### Core Functionality
- **Food Tracker**: Log daily meals and calorie intake with date-based tracking
- **Exercise Tracker**: Record workouts and calories burned
- **Weight Goals**: Set target weight and track progress over time with interactive graphs
- **Calorie Goals**: AI-powered daily calorie goal calculation based on personal metrics
- **Meal Planning**: Weekly meal plan editor with AI-generated suggestions
- **Progress Visualization**: Interactive matplotlib graphs showing calorie intake vs. burn over customizable timeframes
- **Pantry Management**: Track pantry items and generate AI-powered shopping lists
- **AI Chatbot**: Get personalized health and nutrition advice using OpenAI

### Additional Features
- **Desktop Notifications**: Weekly weight reminder notifications (Windows)
- **Auto-startup**: Optional Windows startup integration (WIP)
- **Dark Theme**: Modern, eye-friendly dark theme UI
- **Data Persistence**: SQLite database for reliable data storage
- **Calorie Suggestions**: Smart calorie suggestions from local database or USDA FoodData Central API

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd "Health App"
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Set Up Environment Variables

Create a `.env` file in the project root with your API keys:

```env
OPEN_API_KEY=your_openai_api_key_here
USDA_API_KEY=your_usda_api_key_here  # Optional, for calorie suggestions
```

> **Note**: You can get an OpenAI API key from [OpenAI's website](https://platform.openai.com/api-keys).  
> For USDA API key, visit [USDA FoodData Central](https://fdc.nal.usda.gov/api-guide.html).

### Step 4: Run the Application

```bash
python main.py
```

## Configuration

### Application Settings

The app includes a Settings page where you can configure:

- **Auto-startup**: Enable/disable Windows startup integration (WIP)
- **AI Features**: Toggle AI assistance for food tracking, exercise tracking, and meal planning in case you dont have access to an API key or want to use the features
- **Notifications**: Configure silent notifications for weight reminders
- **Database Import**: Import existing database files for data migration

### Database Location

The application creates a SQLite database file (`health_app.db`) in the project root directory. This file stores all your health data including:

- Food entries
- Exercise logs
- Weight goals and history
- Meal plans
- Pantry items
- Shopping lists

## Usage

### Getting Started

1. **Launch the app** using `python main.py`
2. **Set up your goals** in the Goals tab:
   - Enter your current weight
   - Set a target weight
   - Calculate your daily calorie goal using AI
3. **Start tracking**:
   - Log meals in the Food Tracker tab
   - Record exercises in the Exercise Tracker tab
   - Plan meals in the Meal Plans tab
4. **Monitor progress** in the Graphs tab to visualize your journey

### Keyboard Shortcuts

- **Delete Key**: Remove selected entries from Food Tracker or Exercise Tracker tables
- **Date Navigation**: Use `<` and `>` buttons to navigate between dates

### Tips

- Use the "Suggest" button in Food Tracker to get calorie estimates
- Click on data points in the Goals graph to view/edit/delete entries
- Generate shopping lists from your meal plans using AI
- Enable weekly weight reminders in Settings

## Project Structure

```
Health App/
├── assets/                 # Application icons and images
├── widgets/               # PyQt6 widget modules
│   ├── chat_bot.py        # AI chatbot interface
│   ├── day_widget.py      # Individual day meal plan widget
│   ├── exercise_tracker.py
│   ├── food_tracker.py
│   ├── goals.py
│   ├── graphs.py
│   ├── home_page.py
│   ├── meal_plan.py
│   ├── pantry.py
│   ├── planner_options_dialog.py
│   └── settings.py
├── build/                 # PyInstaller build artifacts
├── dist/                  # Distribution files
├── database.py            # Database utilities and initialization
├── main.py                # Application entry point
├── main_window.py         # Main window and tab management
├── utils.py               # Utility functions and AI decorators
├── config.py              # Configuration constants (colors, etc.)
├── requirements.txt       # Python dependencies
├── health_app.db          # SQLite database (created on first run)
└── README.md              # This file
```

## Requirements

### Core Dependencies

- **PyQt6** (>=6.0.0): GUI framework
- **matplotlib** (>=3.5.0): Data visualization
- **winotify** (>=1.1.0): Windows desktop notifications

### Optional Dependencies

- **python-dotenv**: For environment variable management (recommended)
- **openai**: For AI features (required for chatbot and meal planning)

Install all dependencies:

```bash
pip install -r requirements.txt
```

## Development Status

### ✅ Completed Features

- ✅ Calorie and food tracking
- ✅ Exercise tracking
- ✅ Weight goal tracking with interactive graphs
- ✅ Progress visualization (calories consumed vs. burned)
- ✅ AI chatbot for health advice
- ✅ Weekly weigh-in reminders
- ✅ Desktop notifications
- ✅ Meal planning with AI suggestions
- ✅ Pantry and shopping list management
- ✅ Modern dark theme UI
- ✅ Database import/export functionality

### 🚧 In Progress / Planned

- [ ] AI-suggested meal substitutes
- [ ] Calorie suggestions based on input factors
- [ ] Goal advice and recommendations
- [ ] Sleep diary tracking
- [ ] Health trends by day
- [ ] Mobile support
- [ ] Enhanced AI-driven improvements


## Author

**Alisa Mayes**

- Personal project for learning Python, PyQt6, and AI integration

## Acknowledgments

- **OpenAI** for GPT API access
- **USDA** for FoodData Central API
- **PyQt6** community for excellent documentation
- **Matplotlib** for powerful data visualization

---

**Note**: This application is designed for personal use. Always consult with healthcare professionals for medical advice.
