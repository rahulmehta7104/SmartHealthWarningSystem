import sqlite3
import pandas as pd
import os
from datetime import datetime, date, timedelta
from flask import Flask, render_template, jsonify, request
import json

class HealthWarningSystem:
    def __init__(self, db_path="health_warning_system.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize SQLite database with schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create tables (SQLite version of the schema)
        schema_queries = [
            """
            CREATE TABLE IF NOT EXISTS cities (
                city_id INTEGER PRIMARY KEY AUTOINCREMENT,
                city_name VARCHAR(100) NOT NULL,
                state VARCHAR(100) NOT NULL,
                region VARCHAR(50) NOT NULL,
                population BIGINT NOT NULL,
                pincode VARCHAR(10) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS hospitals (
                hospital_id INTEGER PRIMARY KEY AUTOINCREMENT,
                hospital_name VARCHAR(200) NOT NULL,
                city_id INTEGER NOT NULL,
                hospital_type VARCHAR(100) NOT NULL,
                bed_capacity INTEGER NOT NULL,
                contact_number VARCHAR(15),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (city_id) REFERENCES cities(city_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS diseases (
                disease_id INTEGER PRIMARY KEY AUTOINCREMENT,
                disease_name VARCHAR(100) NOT NULL,
                disease_type VARCHAR(50) NOT NULL,
                severity_level VARCHAR(10) NOT NULL,
                is_communicable BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS symptoms (
                symptom_id INTEGER PRIMARY KEY AUTOINCREMENT,
                symptom_name VARCHAR(100) NOT NULL,
                symptom_category VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS disease_symptoms (
                mapping_id INTEGER PRIMARY KEY AUTOINCREMENT,
                disease_id INTEGER NOT NULL,
                symptom_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (disease_id) REFERENCES diseases(disease_id),
                FOREIGN KEY (symptom_id) REFERENCES symptoms(symptom_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS patient_reports (
                report_id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_name VARCHAR(100) NOT NULL,
                age INTEGER NOT NULL,
                gender VARCHAR(10) NOT NULL,
                contact_number VARCHAR(15),
                city_id INTEGER NOT NULL,
                hospital_id INTEGER NOT NULL,
                disease_id INTEGER NOT NULL,
                report_date DATE NOT NULL,
                outcome VARCHAR(20) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (city_id) REFERENCES cities(city_id),
                FOREIGN KEY (hospital_id) REFERENCES hospitals(hospital_id),
                FOREIGN KEY (disease_id) REFERENCES diseases(disease_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS environmental_data (
                env_id INTEGER PRIMARY KEY AUTOINCREMENT,
                city_id INTEGER NOT NULL,
                monitoring_date DATE NOT NULL,
                air_quality_index INTEGER NOT NULL,
                water_quality_index INTEGER NOT NULL,
                temperature DECIMAL(4,1) NOT NULL,
                humidity INTEGER NOT NULL,
                pm2_5 DECIMAL(5,1) NOT NULL,
                pm10 DECIMAL(5,1) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (city_id) REFERENCES cities(city_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS alerts (
                alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
                city_id INTEGER NOT NULL,
                alert_type VARCHAR(100) NOT NULL,
                severity_level VARCHAR(20) NOT NULL,
                alert_message TEXT NOT NULL,
                alert_date DATE NOT NULL,
                status VARCHAR(20) DEFAULT 'Active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (city_id) REFERENCES cities(city_id)
            )
            """
        ]

        for query in schema_queries:
            cursor.execute(query)

        # Create indexes
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_patient_reports_date ON patient_reports(report_date)",
            "CREATE INDEX IF NOT EXISTS idx_patient_reports_city ON patient_reports(city_id)",
            "CREATE INDEX IF NOT EXISTS idx_environmental_data_date ON environmental_data(monitoring_date)",
            "CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status)"
        ]

        for query in index_queries:
            cursor.execute(query)

        conn.commit()
        conn.close()
        print("Database initialized successfully!")

    def import_csv_data(self, csv_folder="."):
        """Import data from CSV files into database"""
        conn = sqlite3.connect(self.db_path)

        csv_files = [
            ('cities.csv', 'cities'),
            ('hospitals.csv', 'hospitals'),
            ('diseases.csv', 'diseases'),
            ('symptoms.csv', 'symptoms'),
            ('disease_symptoms.csv', 'disease_symptoms'),
            ('patient_reports.csv', 'patient_reports'),
            ('environmental_data.csv', 'environmental_data'),
            ('alerts.csv', 'alerts')
        ]

        for csv_file, table_name in csv_files:
            csv_path = os.path.join(csv_folder, csv_file)
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                df.to_sql(table_name, conn, if_exists='replace', index=False)
                print(f"Imported {len(df)} records into {table_name}")
            else:
                print(f"Warning: {csv_file} not found!")

        conn.close()
        print("Data import completed!")

    def execute_query(self, query, params=None):
        """Execute SQL query and return results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        results = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        conn.close()

        return results, columns

    def get_disease_outbreak_summary(self, days=90):  # CHANGED: Increased from 30 to 90 days
        """Get disease outbreak summary for last N days - FIXED VERSION"""

        # ADDED: Debug query to check data first
        debug_query = """
        SELECT 
            COUNT(*) as total_reports,
            MIN(report_date) as earliest_date,
            MAX(report_date) as latest_date
        FROM patient_reports
        """
        debug_results, _ = self.execute_query(debug_query)
        print(f"Debug - Total reports: {debug_results[0][0]}, Date range: {debug_results[0][1]} to {debug_results[0][2]}")

        # FIXED: More flexible query with lower threshold
        query = """
        SELECT 
            c.city_name,
            d.disease_name,
            COUNT(pr.report_id) as case_count,
            MIN(pr.report_date) as first_case,
            MAX(pr.report_date) as latest_case
        FROM patient_reports pr
        JOIN cities c ON pr.city_id = c.city_id
        JOIN diseases d ON pr.disease_id = d.disease_id
        WHERE pr.report_date >= date('now', '-{} days')
        GROUP BY c.city_id, d.disease_id
        HAVING case_count >= 3
        ORDER BY case_count DESC
        LIMIT 20
        """.format(days)

        results, columns = self.execute_query(query)

        # ADDED: Fallback query if no results
        if not results:
            print("No outbreak data found with strict criteria, using fallback query...")
            fallback_query = """
            SELECT 
                c.city_name,
                d.disease_name,
                COUNT(pr.report_id) as case_count,
                MIN(pr.report_date) as first_case,
                MAX(pr.report_date) as latest_case
            FROM patient_reports pr
            JOIN cities c ON pr.city_id = c.city_id
            JOIN diseases d ON pr.disease_id = d.disease_id
            GROUP BY c.city_id, d.disease_id
            HAVING case_count >= 1
            ORDER BY case_count DESC
            LIMIT 15
            """
            results, columns = self.execute_query(fallback_query)

        return results, columns

    def get_environmental_risk_cities(self):
        """Get cities with high environmental risk - FIXED VERSION"""

        # ADDED: Debug environmental data
        debug_query = "SELECT COUNT(*), MIN(monitoring_date), MAX(monitoring_date) FROM environmental_data"
        debug_results, _ = self.execute_query(debug_query)
        print(f"Debug - Environmental records: {debug_results[0][0]}, Date range: {debug_results[0][1]} to {debug_results[0][2]}")

        query = """
        SELECT 
            c.city_name,
            AVG(ed.air_quality_index) as avg_aqi,
            AVG(ed.water_quality_index) as avg_water_quality,
            COUNT(CASE WHEN ed.air_quality_index > 200 THEN 1 END) as high_pollution_days
        FROM environmental_data ed
        JOIN cities c ON ed.city_id = c.city_id
        WHERE ed.monitoring_date >= date('now', '-90 days')
        GROUP BY c.city_id
        HAVING avg_aqi > 100 OR avg_water_quality < 80
        ORDER BY avg_aqi DESC
        LIMIT 15
        """

        results, columns = self.execute_query(query)

        # ADDED: Fallback for environmental data
        if not results:
            fallback_query = """
            SELECT 
                c.city_name,
                AVG(ed.air_quality_index) as avg_aqi,
                AVG(ed.water_quality_index) as avg_water_quality,
                COUNT(*) as total_readings
            FROM environmental_data ed
            JOIN cities c ON ed.city_id = c.city_id
            GROUP BY c.city_id
            ORDER BY avg_aqi DESC
            LIMIT 10
            """
            results, columns = self.execute_query(fallback_query)

        return results, columns

    def get_hospital_capacity_status(self):
        """Get hospital capacity utilization - FIXED VERSION"""
        query = """
        SELECT 
            h.hospital_name,
            c.city_name,
            h.bed_capacity,
            COUNT(pr.report_id) as total_patients,
            COUNT(CASE WHEN pr.outcome = 'Under Treatment' THEN 1 END) as current_patients,
            ROUND((COUNT(pr.report_id) * 100.0 / h.bed_capacity), 2) as utilization_rate
        FROM hospitals h
        JOIN cities c ON h.city_id = c.city_id
        LEFT JOIN patient_reports pr ON h.hospital_id = pr.hospital_id 
        GROUP BY h.hospital_id
        ORDER BY utilization_rate DESC
        LIMIT 20
        """

        results, columns = self.execute_query(query)
        return results, columns

    def get_active_alerts(self):
        """Get active alerts - FIXED VERSION"""
        query = """
        SELECT 
            c.city_name,
            a.alert_type,
            a.severity_level,
            a.alert_message,
            a.alert_date,
            a.status
        FROM alerts a
        JOIN cities c ON a.city_id = c.city_id
        WHERE a.status = 'Active' OR a.alert_date >= date('now', '-30 days')
        ORDER BY 
            CASE a.severity_level 
                WHEN 'Critical' THEN 1
                WHEN 'High' THEN 2
                WHEN 'Medium' THEN 3
                ELSE 4
            END,
            a.alert_date DESC
        LIMIT 15
        """

        results, columns = self.execute_query(query)
        return results, columns

    def test_data_availability(self):
        """Test function to check if data exists"""
        tables = ['cities', 'hospitals', 'diseases', 'patient_reports', 
                 'environmental_data', 'alerts']

        print("\n=== DATA AVAILABILITY TEST ===")
        for table in tables:
            query = f"SELECT COUNT(*) FROM {table}"
            results, _ = self.execute_query(query)
            count = results[0][0]
            print(f"{table:20}: {count:6} records")

        # Test specific date ranges
        query = """
        SELECT 
            MIN(report_date) as min_date,
            MAX(report_date) as max_date,
            COUNT(*) as total
        FROM patient_reports
        """
        results, _ = self.execute_query(query)
        if results and results[0][0]:
            print(f"\nPatient Reports Date Range:")
            print(f"  Earliest: {results[0][0]}")
            print(f"  Latest:   {results[0][1]}")
            print(f"  Total:    {results[0][2]}")

        return True

# Flask Web Application
app = Flask(__name__)
health_system = HealthWarningSystem()

@app.route('/')
def dashboard():
    """Main dashboard"""
    return render_template('dashboard.html')

@app.route('/api/outbreak-summary')
def api_outbreak_summary():
    """API endpoint for outbreak summary"""
    results, columns = health_system.get_disease_outbreak_summary()
    data = [dict(zip(columns, row)) for row in results]
    print(f"Outbreak API: Returning {len(data)} records")  # ADDED: Debug output
    return jsonify(data)

@app.route('/api/environmental-risk')
def api_environmental_risk():
    """API endpoint for environmental risk"""
    results, columns = health_system.get_environmental_risk_cities()
    data = [dict(zip(columns, row)) for row in results]
    return jsonify(data)

@app.route('/api/hospital-capacity')
def api_hospital_capacity():
    """API endpoint for hospital capacity"""
    results, columns = health_system.get_hospital_capacity_status()
    data = [dict(zip(columns, row)) for row in results]
    return jsonify(data)

@app.route('/api/active-alerts')
def api_active_alerts():
    """API endpoint for active alerts"""
    results, columns = health_system.get_active_alerts()
    data = [dict(zip(columns, row)) for row in results]
    return jsonify(data)

@app.route('/query')
def query_interface():
    """SQL query interface"""
    return render_template('query.html')

@app.route('/api/execute-query', methods=['POST'])
def api_execute_query():
    """Execute custom SQL query"""
    try:
        query = request.json.get('query')
        if not query:
            return jsonify({'error': 'No query provided'}), 400

        # Basic security: only allow SELECT queries
        if not query.strip().upper().startswith('SELECT'):
            return jsonify({'error': 'Only SELECT queries are allowed'}), 400

        results, columns = health_system.execute_query(query)
        data = [dict(zip(columns, row)) for row in results]
        return jsonify({'data': data, 'columns': columns})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/test')
def test_data():
    """Test endpoint to check data availability"""
    health_system.test_data_availability()
    return "Check console for data availability results"

if __name__ == '__main__':
    print("Smart Public Health Warning System - Phase 2 (FIXED)")
    print("=" * 60)

    # Import CSV data on startup
    if not os.path.exists("health_warning_system.db"):
        print("Importing CSV data...")
        health_system.import_csv_data()

    # ADDED: Test data availability
    health_system.test_data_availability()

    print("\nStarting web application...")
    print("Access the dashboard at: http://localhost:5000")
    print("Access SQL query interface at: http://localhost:5000/query")
    print("Test data availability at: http://localhost:5000/test")

    app.run(debug=True, host='0.0.0.0', port=5000)
