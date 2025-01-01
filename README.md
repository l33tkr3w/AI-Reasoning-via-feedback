AI Reasoning System - README
Overview
The AI Reasoning System is a Flask-based web application designed to facilitate reasoning and problem-solving using AI models. This project integrates with the AI Reasoning via Feedback repository, providing an interactive interface for inputting questions and streaming AI-driven reasoning steps and conclusions.

Features
Real-Time Reasoning Progress: Stream AI reasoning steps directly to the client in real time.
Dynamic Model Selection: Automatically fetch and display available models from the AI backend.
Step-by-Step Analysis: Generate structured reasoning steps with detailed conclusions.
Interactive Web Interface: Responsive UI styled with Bootstrap for modern usability.
Asynchronous Processing: Multithreaded backend for smooth and efficient analysis.
Technologies Used
Backend: Flask, Python
Frontend: HTML, Bootstrap 5
API Communication: Requests library for connecting to the AI backend
Concurrency: Python threading and queue for asynchronous task management
Setup Instructions
1. Prerequisites
Python 3.8 or newer
AI Reasoning backend from AI-Reasoning-via-feedback
pip package manager
AI backend server running locally on localhost:11434
2. Installation
Clone the repository:
bash
Copy code
git clone https://github.com/l33tkr3w/AI-Reasoning-via-feedback.git
cd AI-Reasoning-via-feedback
Install Python dependencies:
bash
Copy code
pip install flask requests
Start the AI backend server (refer to the AI Reasoning via Feedback documentation).
Running the Application
1. Start the Flask App
Run the Flask application with:

bash
Copy code
python app.py
The app will start at http://localhost:5000.

2. Access the Web Interface
Open a browser and go to http://localhost:5000.

