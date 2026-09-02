# SupportPilot

SupportPilot is an intelligent IT support ticketing system built with Flask and Python. It leverages machine learning to automatically classify incoming support tickets, predict their severity based on keywords, and calculate their priority based on business impact.

## Features

- **Submit Tickets:** A user-friendly web interface to submit IT support tickets.
- **AI Classification:** Uses a trained `scikit-learn` model to automatically categorize tickets into predefined categories (e.g., Network, Hardware, Software).
- **Severity Prediction:** Automatically assesses the severity of the issue (Critical, High, Medium, Low) using keyword analysis and category context.
- **Priority Calculation:** Calculates ticket priority (P1 to P4) based on the severity and the business impact of the user's department.
- **SQLite Database:** Stores all tickets and their AI-classified metadata in a local SQLite database (`tickets.db`).

## Prerequisites

- Python 3.7 or higher

## Installation

1. **Clone the repository or navigate to the project directory:**
   ```bash
   cd SupportPilot
   ```

2. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Train the Machine Learning Model:**
   Before running the application for the first time, you need to train the classifier model. This will generate the necessary `.pkl` files in the `models` directory.
   ```bash
   python train_model.py
   ```

2. **Start the Application:**
   Run the Flask development server.
   ```bash
   python app.py
   ```

3. **Access the Web Interface:**
   The application will automatically open in your default web browser at `http://127.0.0.1:5000`. If it doesn't, you can manually navigate to that URL.

## Project Structure

- `app.py`: The main Flask application handling routing, API endpoints, and database interactions.
- `classifier.py`: Contains the logic for AI classification, severity prediction, and priority calculation.
- `database.py`: Handles the SQLite database initialization.
- `train_model.py`: Script to train the `scikit-learn` model and save the vectorizer and classifier.
- `models/`: Directory where the trained `.pkl` models are stored.
- `templates/`: Contains the HTML templates for the web interface.
- `tickets.db`: The SQLite database file (created automatically upon running the app).
- `requirements.txt`: List of Python dependencies.

## Technologies Used

- **Flask:** Web framework for Python.
- **scikit-learn:** Machine learning library used for text classification.
- **joblib:** Used for saving and loading the trained models.
- **SQLite:** Lightweight relational database.
- **Pandas:** Data manipulation and analysis (used during model training).
