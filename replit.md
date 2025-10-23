# EcoMind: A Smart Digital Carbon Tracker

## Overview

EcoMind is an AI-powered web application that helps users track, predict, and reduce their digital carbon footprint. The application monitors carbon emissions from digital activities including emails, video calls, streaming, cloud storage, and device usage. It uses machine learning to predict future emissions, provides personalized eco-friendly recommendations, and gamifies the experience through levels and badges to encourage sustainable digital behavior.

The application is built with Streamlit for the frontend, Python for backend logic, scikit-learn for ML predictions, and PostgreSQL for data persistence. It features interactive data visualizations using Plotly, comprehensive PDF reporting capabilities, and a gamification system to drive user engagement.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
The application uses **Streamlit** as the web framework, providing an interactive single-page application with tabs for different features (Dashboard, Predictions, Recommendations, Profile). The UI emphasizes data visualization through Plotly charts and interactive components. Session state management handles user authentication, calculator instances, and database connections throughout the user session.

### Backend Architecture
The application follows a **modular utility-based architecture** with separate Python modules for distinct concerns:

- **Carbon Calculator** (`utils/carbon_calculator.py`): Core calculation engine that converts digital activities into CO2 emissions using predefined emission factors
- **ML Predictor** (`utils/ml_model.py`): Random Forest regression model for predicting future carbon emissions based on historical user behavior
- **Recommendation Engine** (`utils/recommender.py`): Rule-based system that provides personalized eco-tips based on user activity patterns
- **Gamification System** (`utils/gamification.py`): Manages user progression through levels (Bronze to Diamond), badge awards, and scoring mechanisms
- **PDF Generator** (`utils/pdf_generator.py`): Creates comprehensive reports using ReportLab with charts and statistics
- **Database Manager** (`utils/database.py`): Handles all PostgreSQL operations with connection pooling and schema management

### Data Storage Solutions
The application uses **PostgreSQL** as the primary database with the following schema design:

- **users table**: Stores user accounts with username, email, level, score, and join date
- **activity_logs table**: Records daily digital activities and calculated CO2 emissions per user
- **badges table**: Tracks earned achievements and timestamps
- **predictions table**: Stores ML-generated predictions for future reference

The database manager implements connection string validation, automatic schema creation, and error handling for connection failures. All database operations use parameterized queries to prevent SQL injection.

### Authentication & Authorization
The application implements a **session-based authentication** system stored in Streamlit's session state. User credentials and authentication status are managed through `st.session_state.authenticated`, `st.session_state.current_user`, and `st.session_state.user_id`. The database stores user accounts, but the implementation allows for integration with external authentication providers like Supabase.

### Machine Learning Pipeline
The **CarbonPredictor** module uses a Random Forest regression model trained on synthetic data representing various user behavior patterns. The model:

- Accepts features: emails sent, video call hours, streaming hours, cloud storage GB, device usage hours
- Outputs: Predicted CO2 emissions in grams
- Uses StandardScaler for feature normalization
- Implements automatic retraining when historical data is insufficient
- Generates synthetic training data for cold-start scenarios

Alternative considered: Linear regression was evaluated but Random Forest was chosen for better handling of non-linear relationships between digital activities and emissions.

### Gamification Design
The system implements a **points-based progression** system with five levels (Bronze, Silver, Gold, Platinum, Diamond) and activity-based badges. Users earn points by:

- Reducing emissions below threshold values
- Maintaining consistent tracking streaks
- Achieving specific milestones

This approach encourages continued engagement and positive behavior change through tangible rewards and visible progress indicators.

## External Dependencies

### Third-Party Libraries
- **Streamlit**: Web application framework for the user interface
- **Plotly**: Interactive charting and data visualization library
- **Pandas & NumPy**: Data manipulation and numerical computations
- **scikit-learn**: Machine learning model training and prediction
- **ReportLab**: PDF generation for downloadable reports
- **psycopg2**: PostgreSQL database adapter for Python

### Database Service
- **PostgreSQL**: Relational database accessed via `DATABASE_URL` environment variable
- Connection string must be configured in environment variables
- Application validates connection on startup and provides clear error messages if unavailable

### Data Sources
- **Sample Data Generator** (`data/sample_data.py`): Creates synthetic user activity data for testing and model training
- Emission factors are hardcoded constants based on research averages for digital activities

### Future Integration Points
The architecture supports potential integration with:
- External authentication providers (Supabase mentioned in requirements)
- Voice assistant capabilities using `speech_recognition` and `pyttsx3`
- Cloud deployment on Streamlit Cloud
- Real-time activity tracking through browser extensions or API integrations