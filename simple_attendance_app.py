#!/usr/bin/env python3
"""
Attendance System - Backend API
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import face_recognition
import numpy as np
import pickle
import sqlite3
from datetime import datetime
import os
import base64
from PIL import Image
import io
import csv
import traceback

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# Initialize variables
known_face_encodings = []
known_face_names = []
known_face_ids = []
student_data = {}
student_encodings = {}
marked_today = set()

# File paths
DATA_DIR = "attendance_data"
ENCODINGS_FILE = os.path.join(DATA_DIR, "face_encodings.pkl")
STUDENTS_FILE = os.path.join(DATA_DIR, "students.pkl")
DB_FILE = os.path.join(DATA_DIR, "attendance.db")
STUDENT_PHOTOS_DIR = os.path.join(DATA_DIR, "student_photos")

# Create directories
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(STUDENT_PHOTOS_DIR, exist_ok=True)

print(f"📁 Current working directory: {os.getcwd()}")
print(f"📁 Templates folder exists: {os.path.exists('templates')}")

def init_database():
    """Initialize database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            student_name TEXT NOT NULL,
            class_section TEXT,
            confidence REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            date DATE DEFAULT (date('now'))
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            student_name TEXT NOT NULL,
            class_section TEXT,
            photos_count INTEGER DEFAULT 0,
            registration_date TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized")

def save_data():
    """Save all data"""
    try:
        encoding_data = {
            'encodings': known_face_encodings,
            'names': known_face_names,
            'ids': known_face_ids,
            'student_encodings': student_encodings
        }
        with open(ENCODINGS_FILE, 'wb') as f:
            pickle.dump(encoding_data, f)
        
        with open(STUDENTS_FILE, 'wb') as f:
            pickle.dump(student_data, f)
            
        print(f"✅ Saved {len(known_face_names)} students")
    except Exception as e:
        print(f"Error saving: {e}")

def load_data():
    """Load existing data"""
    global known_face_encodings, known_face_names, known_face_ids, student_data, student_encodings
    
    try:
        if os.path.exists(ENCODINGS_FILE):
            with open(ENCODINGS_FILE, 'rb') as f:
                data = pickle.load(f)
                known_face_encodings = data.get('encodings', [])
                known_face_names = data.get('names', [])
                known_face_ids = data.get('ids', [])
                student_encodings = data.get('student_encodings', {})
        
        if os.path.exists(STUDENTS_FILE):
            with open(STUDENTS_FILE, 'rb') as f:
                student_data = pickle.load(f)
                
        print(f"✅ Loaded {len(known_face_names)} students")
    except Exception as e:
        print(f"Error loading: {e}")

# Initialize
init_database()
load_data()

@app.route('/')
def index():
    """Serve the frontend page"""
    return render_template('index.html')

@app.route('/api/test')
def test():
    """Test API endpoint"""
    return jsonify({'status': 'success', 'message': 'Backend is running!'})

@app.route('/api/dashboard_stats')
def dashboard_stats():
    """Get dashboard statistics"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        today = datetime.now().date()
        cursor.execute('SELECT COUNT(*) FROM attendance WHERE date = ?', (today,))
        today_count = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'total_students': len(known_face_names),
            'today_attendance': today_count,
            'total_encodings': len(known_face_encodings)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/students')
def get_students():
    """Get all students"""
    students_list = []
    for student_id, data in student_data.items():
        students_list.append({
            'id': student_id,
            'name': data['name'],
            'class_section': data.get('class_section', 'N/A'),
            'photos_count': data.get('photos_count', 0),
            'registration_date': data.get('registration_date', '')
        })
    return jsonify(students_list)

@app.route('/api/register_student', methods=['POST'])
def register_student():
    """Register new student with 5 photos"""
    try:
        data = request.json
        student_id = data.get('student_id')
        student_name = data.get('student_name')
        class_section = data.get('class_section', '')
        photos = data.get('photos', [])
        
        if not student_id or not student_name or len(photos) < 5:
            return jsonify({'error': 'Please provide student details and 5 photos'}), 400
        
        if student_id in student_data:
            return jsonify({'error': 'Student ID already exists'}), 400
        
        encodings = []
        
        for i, photo_base64 in enumerate(photos[:5]):
            # Decode base64 image
            image_data = base64.b64decode(photo_base64.split(',')[1])
            image = Image.open(io.BytesIO(image_data))
            image_np = np.array(image)
            
            # Convert for face_recognition
            if len(image_np.shape) == 3:
                image_np = image_np[:, :, ::-1]
            
            face_locations = face_recognition.face_locations(image_np)
            face_encodings = face_recognition.face_encodings(image_np, face_locations)
            
            if len(face_encodings) == 0:
                return jsonify({'error': f'No face detected in photo {i+1}'}), 400
            
            encodings.append(face_encodings[0])
            
            # Save photo
            student_photo_dir = os.path.join(STUDENT_PHOTOS_DIR, student_id)
            os.makedirs(student_photo_dir, exist_ok=True)
            image.save(os.path.join(student_photo_dir, f'photo_{i+1}.jpg'))
        
        # Average encoding for better accuracy
        avg_encoding = np.mean(encodings, axis=0)
        
        # Store data
        known_face_encodings.append(avg_encoding)
        known_face_names.append(student_name)
        known_face_ids.append(student_id)
        student_encodings[student_id] = encodings
        
        student_data[student_id] = {
            'name': student_name,
            'class_section': class_section,
            'photos_count': 5,
            'registration_date': datetime.now().isoformat()
        }
        
        # Save to database
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO students (student_id, student_name, class_section, photos_count, registration_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (student_id, student_name, class_section, 5, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        
        save_data()
        
        return jsonify({'success': True, 'message': f'Student {student_name} registered successfully!'})
        
    except Exception as e:
        print(f"Registration error: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/mark_attendance', methods=['POST'])
def mark_attendance():
    """Mark attendance from group photo"""
    try:
        data = request.json
        photo_base64 = data.get('photo')
        
        if not photo_base64:
            return jsonify({'error': 'No photo provided'}), 400
        
        if len(known_face_encodings) == 0:
            return jsonify({'error': 'No students registered yet!'}), 400
        
        # Decode image
        image_data = base64.b64decode(photo_base64.split(',')[1])
        image = Image.open(io.BytesIO(image_data))
        image_np = np.array(image)
        
        if len(image_np.shape) == 3:
            image_np = image_np[:, :, ::-1]
        
        face_locations = face_recognition.face_locations(image_np)
        face_encodings = face_recognition.face_encodings(image_np, face_locations)
        
        if len(face_encodings) == 0:
            return jsonify({'error': 'No faces detected in the photo'}), 400
        
        recognized_students = []
        
        for face_encoding in face_encodings:
            best_match = None
            best_confidence = 0
            
            for idx, known_encoding in enumerate(known_face_encodings):
                face_distance = face_recognition.face_distance([known_encoding], face_encoding)[0]
                confidence = 1 - face_distance
                
                if confidence > 0.5 and confidence > best_confidence:
                    best_confidence = confidence
                    best_match = idx
            
            if best_match is not None:
                student_id = known_face_ids[best_match]
                student_name = known_face_names[best_match]
                
                # Mark attendance
                current_time = datetime.now()
                today = current_time.date()
                session_key = f"{student_id}_{today}"
                
                if session_key not in marked_today:
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    
                    cursor.execute('SELECT COUNT(*) FROM attendance WHERE student_id = ? AND date = ?', 
                                  (student_id, today))
                    count = cursor.fetchone()[0]
                    
                    if count == 0:
                        class_section = student_data.get(student_id, {}).get('class_section', '')
                        cursor.execute('''
                            INSERT INTO attendance (student_id, student_name, class_section, confidence, timestamp, date)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (student_id, student_name, class_section, best_confidence,
                              current_time.strftime('%Y-%m-%d %H:%M:%S'), today))
                        conn.commit()
                        marked_today.add(session_key)
                    
                    conn.close()
                
                recognized_students.append({
                    'id': student_id,
                    'name': student_name,
                    'confidence': round(best_confidence * 100, 2)
                })
        
        return jsonify({
            'success': True,
            'recognized': recognized_students,
            'total_faces': len(face_encodings),
            'unknown': len(face_encodings) - len(recognized_students)
        })
        
    except Exception as e:
        print(f"Attendance error: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/today_attendance')
def today_attendance():
    """Get today's attendance"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        today = datetime.now().date()
        cursor.execute('''
            SELECT student_id, student_name, timestamp, confidence 
            FROM attendance WHERE date = ?
            ORDER BY timestamp DESC
        ''', (today,))
        records = cursor.fetchall()
        conn.close()
        
        attendance_list = []
        for record in records:
            attendance_list.append({
                'student_id': record[0],
                'student_name': record[1],
                'timestamp': record[2],
                'confidence': round(record[3] * 100, 2) if record[3] else 0
            })
        
        return jsonify(attendance_list)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export_csv')
def export_csv():
    """Export attendance to CSV"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        today = datetime.now().date()
        cursor.execute('''
            SELECT student_id, student_name, timestamp 
            FROM attendance WHERE date = ?
            ORDER BY timestamp DESC
        ''', (today,))
        records = cursor.fetchall()
        conn.close()
        
        if not records:
            return jsonify({'error': 'No records found'}), 404
        
        filename = f"attendance_{today}.csv"
        filepath = os.path.join(DATA_DIR, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Student ID', 'Student Name', 'Timestamp'])
            writer.writerows(records)
        
        return send_file(filepath, as_attachment=True)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reset_session', methods=['POST'])
def reset_session():
    """Reset today's session"""
    global marked_today
    marked_today.clear()
    return jsonify({'success': True, 'message': 'Session reset successfully'})

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Attendance System Backend Starting...")
    print("="*60)
    print(f"📍 Current directory: {os.getcwd()}")
    print(f"📁 Templates folder: {os.path.abspath('templates')}")
    print(f"🌐 Open browser: http://localhost:5000")
    print("="*60 + "\n")
    app.run(debug=True, host='localhost', port=5000)