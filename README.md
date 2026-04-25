# Smart Attendance System with Face Recognition

A comprehensive Python GUI application for automated attendance tracking using facial recognition technology.

## Features

### 🎯 **Core Functionality**
- **Student Registration**: Register students with ID, name, and class/section
- **Face Recognition**: Advanced face detection and recognition using face_recognition library
- **Real-time Attendance**: Live webcam feed that detects multiple faces simultaneously
- **Automatic Logging**: Attendance records saved to SQLite database with timestamps
- **Data Export**: Export attendance records to CSV format

### 🖥️ **User Interface**
- **Professional GUI**: Clean, intuitive Tkinter-based interface
- **Dual Modes**: Switch between Registration and Attendance modes
- **Live Video Feed**: Real-time camera display with face detection overlays
- **Status Monitoring**: System status and attendance counters
- **Records Viewer**: Built-in attendance records browser

### 📊 **Data Management**
- **SQLite Database**: Robust local database for attendance records
- **Pickle Storage**: Efficient face encodings and student data storage
- **CSV Export**: Generate attendance reports for external use
- **Data Persistence**: All data saved locally and loaded on startup

## Installation

### Prerequisites
- Python 3.7 or higher
- Webcam/Camera device
- Windows/Linux/macOS

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: On some systems, you may need to install additional dependencies:

**For Windows:**
```bash
pip install cmake
pip install dlib
pip install face-recognition
```

**For Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install cmake
sudo apt-get install python3-dev
pip install dlib
pip install face-recognition
```

**For macOS:**
```bash
brew install cmake
pip install dlib
pip install face-recognition
```

### Step 2: Run the Application

```bash
python smart_attendance_app.py
```

## Usage Guide

### 🔧 **Initial Setup**

1. **Start the Application**
   ```bash
   python smart_attendance_app.py
   ```

2. **Start Camera**
   - Click "Start Camera" to activate webcam feed
   - Ensure good lighting for optimal face detection

### 👤 **Student Registration**

1. **Select Registration Mode**
   - Choose "Student Registration" radio button
   - Registration panel will be highlighted

2. **Enter Student Details**
   - **Student ID**: Unique identifier (e.g., "STU001", "2023001")
   - **Student Name**: Full name of the student
   - **Class/Section**: Class or section information

3. **Capture Face**
   - Position student in front of camera
   - Ensure only one face is visible in frame
   - Click "Capture Face" button
   - System will detect and encode the face automatically

4. **Confirmation**
   - Success message will appear
   - Student count will update
   - Form will clear for next registration

### 📋 **Attendance Marking**

1. **Select Attendance Mode**
   - Choose "Attendance Marking" radio button
   - Attendance panel will be highlighted

2. **Automatic Recognition**
   - System continuously scans for faces
   - Recognized students show **green** bounding boxes with names
   - Unknown faces show **red** bounding boxes labeled "Unknown"
   - Attendance is marked automatically (once per day per student)

3. **Monitor Attendance**
   - View today's attendance count
   - See recent attendance list in real-time
   - Check system status

### 📊 **Data Management**

1. **View Records**
   - Click "View Records" to see all attendance data
   - Records displayed in sortable table format
   - Shows Student ID, Name, Class, Date, and Time

2. **Export Data**
   - Click "Export to CSV" to save attendance report
   - Choose location and filename
   - Opens in Excel or any CSV-compatible application

## File Structure

```
smart-attendance-system/
├── smart_attendance_app.py    # Main application
├── requirements.txt           # Python dependencies
├── README.md                 # This file
└── attendance_data/          # Created automatically
    ├── face_encodings.pkl    # Face recognition data
    ├── students.pkl          # Student information
    └── attendance.db         # SQLite attendance database
```

## Technical Details

### 🔍 **Face Recognition**
- **Library**: face_recognition (based on dlib)
- **Algorithm**: 128-dimensional face encoding
- **Accuracy**: High accuracy with proper lighting
- **Speed**: Real-time processing at ~30 FPS

### 🎥 **Camera Handling**
- **Library**: OpenCV (cv2)
- **Resolution**: Automatic (typically 640x480)
- **Frame Rate**: ~30 FPS
- **Mirror Effect**: Horizontal flip for natural interaction

### 💾 **Data Storage**
- **Face Encodings**: Pickle format for fast loading
- **Student Data**: Pickle format with metadata
- **Attendance Records**: SQLite database with timestamps
- **Exports**: CSV format for compatibility

### 🖼️ **GUI Framework**
- **Library**: Tkinter (built-in Python GUI)
- **Design**: Professional, responsive layout
- **Threading**: Separate thread for video processing
- **Real-time Updates**: Live status and attendance updates

## Troubleshooting

### 🚫 **Common Issues**

**Camera not working:**
- Check if camera is connected and not used by other applications
- Try different camera index (modify `cv2.VideoCapture(0)` to `cv2.VideoCapture(1)`)
- Ensure camera permissions are granted

**Face not detected:**
- Improve lighting conditions
- Position face directly toward camera
- Remove glasses or accessories if necessary
- Ensure face is clearly visible and not too far

**Installation errors:**
- Install Visual Studio Build Tools (Windows)
- Update pip: `pip install --upgrade pip`
- Install dependencies one by one if batch install fails

**Recognition accuracy issues:**
- Re-register with better lighting
- Ensure consistent lighting between registration and attendance
- Register multiple angles if needed

### 🔧 **Performance Optimization**

**For better performance:**
- Close other camera applications
- Ensure good lighting
- Use a decent quality webcam
- Keep the application window active

**For large databases:**
- The system handles hundreds of students efficiently
- Face recognition speed may decrease with very large databases
- Consider periodic database cleanup for old records

## Security & Privacy

### 🔒 **Data Security**
- All data stored locally (no cloud dependency)
- Face encodings are mathematical representations, not images
- Student photos are not stored, only face encodings
- Database can be encrypted if needed

### 🛡️ **Privacy Considerations**
- Inform students about face recognition usage
- Comply with local privacy regulations
- Provide opt-out mechanisms if required
- Secure the data directory appropriately

## Customization

### 🎨 **UI Customization**
- Modify colors in the code (search for color codes like `#2c3e50`)
- Adjust window size by changing `geometry("1200x800")`
- Add school/organization logo by modifying the title frame

### ⚙️ **Functionality Extensions**
- Add photo capture during registration
- Implement attendance reports with charts
- Add email notifications for attendance
- Integrate with existing school management systems

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or contributions:
1. Check the troubleshooting section
2. Review the code comments for technical details
3. Test with different lighting conditions
4. Ensure all dependencies are properly installed

---

**Note**: This system is designed for educational and small-scale institutional use. For large-scale deployments, consider additional security measures and performance optimizations.