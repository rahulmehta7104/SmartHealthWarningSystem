
# Smart Public Health Warning System - Phase 2
# Setup and Installation Guide for Windows 11 with VS Code

## System Requirements
- Python 3.8 or higher
- VS Code (Visual Studio Code)
- Windows 11

## Installation Steps

### Step 1: Install Python
1. Download Python from https://python.org/downloads/
2. During installation, CHECK "Add Python to PATH"
3. Verify installation: Open Command Prompt and run `python --version`

### Step 2: Install VS Code
1. Download VS Code from https://code.visualstudio.com/
2. Install the Python extension in VS Code

### Step 3: Set up Project
1. Create a new folder for your project (e.g., C:\health-warning-system)
2. Open VS Code and open this folder (File -> Open Folder)
3. Copy all the project files into this folder

### Step 4: Set up Virtual Environment (Recommended)
Open VS Code Terminal (Terminal -> New Terminal) and run:
```bash
python -m venv health_env
health_env\Scripts\activate
```

### Step 5: Install Dependencies
In the VS Code terminal, run:
```bash
pip install -r requirements.txt
```

### Step 6: Run the Application
```bash
python app.py
```

### Step 7: Access the Application
- Open your web browser
- Go to http://localhost:5000 for the main dashboard
- Go to http://localhost:5000/query for SQL query interface

## Project Structure
```
health-warning-system/
├── app.py                 # Main Python application
├── requirements.txt       # Python dependencies
├── database_schema.sql    # Database schema (MySQL version)
├── sample_queries.sql     # Sample SQL queries for reference
├── templates/             # HTML templates
│   ├── dashboard.html     # Main dashboard
│   └── query.html         # SQL query interface
├── *.csv                  # Synthetic datasets
└── README.md             # This file
```

## How to Use

### 1. Dashboard
- Displays real-time health monitoring data
- Shows disease outbreaks, environmental risks, hospital capacity, and active alerts
- Data refreshes automatically

### 2. SQL Query Interface
- Execute custom SQL queries
- Sample queries provided for learning
- Download results as CSV
- Great for demonstrating DBMS concepts

### 3. Database Features Demonstrated
- Relational database design with proper normalization
- Foreign key relationships between tables
- Complex joins across multiple tables
- Aggregate queries and grouping
- Views for common analytical queries
- Indexes for performance optimization

## Phase 2 Scope
This implementation includes:
✅ Database design and creation
✅ Synthetic realistic datasets
✅ Data import functionality  
✅ Web-based dashboard
✅ SQL query interface
✅ Basic data analysis and visualization
✅ Foundation for ML integration

## Phase 3 Extensions (Future Work)
- Machine Learning models for outbreak prediction
- Real-time data ingestion from external APIs
- Advanced alert system with notifications
- Mobile application
- Geographic visualization (maps)
- Advanced analytics and reporting

## Troubleshooting

### Common Issues:
1. **Python not found**: Ensure Python is in your PATH
2. **Module not found**: Run `pip install -r requirements.txt`
3. **Port already in use**: Change port in app.py (line with app.run)
4. **Database errors**: Delete health_warning_system.db and restart

### Getting Help:
- Check VS Code terminal for error messages
- Ensure all CSV files are in the same directory as app.py
- Verify Python version is 3.8+

## Sample Queries to Try
1. Top cities by disease cases
2. Hospital capacity analysis
3. Environmental risk assessment
4. Disease patterns by age group
5. Correlation between pollution and respiratory diseases

Enjoy exploring the Smart Public Health Warning System!
