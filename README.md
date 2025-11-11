# POWERGRID Face Recognition System

An AI-powered photo discovery platform that automatically matches employees with event photos using state-of-the-art facial recognition technology.

## 🎯 Overview

This system enables employees to instantly access all photos they appear in across company events. It uses deep learning (ArcFace model) to automatically detect and match faces in event photographs.

## ✨ Features

- **Automatic Face Recognition**: Uses ArcFace deep learning model for high-accuracy face matching
- **Employee Portal**: Self-service web interface for employees to view their photos
- **Event Management**: Organize photos by events with metadata (date, location, etc.)
- **Download Capabilities**: Download matched photos as ZIP files or CSV reports
- **Secure Authentication**: Employee ID and password protected access
- **Scalable Architecture**: Built to handle thousands of photos and employees

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **AI/ML**: DeepFace, TensorFlow, Keras
- **Database**: MySQL
- **Image Processing**: OpenCV, Pillow
- **Scientific Computing**: NumPy, SciPy

## 📋 Prerequisites

- Python 3.8+
- MySQL Server
- Virtual environment (recommended)

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd powergrid-face-recognition
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv faceenv
   # On Windows
   .\faceenv\Scripts\Activate.ps1
   # On Linux/Mac
   source faceenv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up MySQL database**
   - Create a MySQL database named `powergrid_face_db`
   - Run the database schema: `database_schema.sql`
   - Update database credentials in `app.py`, `main.py`, and `employee_encoder_deepface.py`
   - **Note**: For production, use environment variables or a config file (see `config.py.example`)

5. **Configure the application**
   - Update database connection settings in the code files
   - Set a secure secret key in `app.py` (replace `'your_secret_key_here'`)
   - Add employee data to the `employee_data/` directory
   - Add event photos to the `event_data/` directory

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Access the application**
   - Open your browser and navigate to `http://localhost:5000`

## 📁 Project Structure

```
powergrid-face-recognition/
├── app.py                      # Main Flask application
├── main.py                     # Employee encoding script
├── employee_encoder_deepface.py # DeepFace encoding utility
├── requirements.txt            # Python dependencies
├── database_schema.sql         # MySQL database schema
├── employee_data/              # Employee reference photos (excluded from git)
├── event_data/                 # Event photos (excluded from git)
├── static/                     # Static files (CSS, images)
│   ├── matched_photos/         # Matched photos (excluded from git)
│   └── css/
├── templates/                  # HTML templates
│   ├── index.html             # Login page
│   ├── events.html            # Events listing page
│   └── profile.html           # Photo gallery page
└── README.md                   # This file
```

## 🔒 Security Notes

⚠️ **Important**: Before deploying to production:

1. **Change database credentials**: Update MySQL username and password in all code files
2. **Set secure secret key**: Replace `'your_secret_key_here'` in `app.py` with a strong random key
3. **Use environment variables**: Consider using environment variables or a config file for sensitive data
4. **Hash passwords**: Implement password hashing instead of plaintext storage
5. **Enable HTTPS**: Use HTTPS in production for secure communication

## 📝 Usage

### Encoding Employee Photos

1. Place employee photos in `employee_data/{employee_id}/` directory
2. Add `metadata.txt` file with employee details
3. Run the encoding script:
   ```bash
   python employee_encoder_deepface.py
   ```

### Processing Event Photos

1. Place event photos in `event_data/{event_name}/` directory
2. Add `metadata.txt` file with event details (date, location, etc.)
3. Run the main processing script:
   ```bash
   python main.py
   ```

### Accessing the Web Portal

1. Start the Flask application: `python app.py`
2. Log in with employee ID and password
3. View matched photos by event
4. Download photos or CSV reports

## 🧪 Testing

- Test the face recognition accuracy with known employee photos
- Verify database connections and queries
- Test the web interface with different browsers
- Verify download functionality (ZIP and CSV)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is proprietary and confidential.

## 👥 Authors

- POWERGRID Development Team

## 🙏 Acknowledgments

- DeepFace library for face recognition capabilities
- Flask community for web framework
- MySQL for robust database management

## 📧 Support

For issues or questions, please contact the development team.

---

**Note**: This repository excludes sensitive data including:
- Employee photos
- Event photos
- Database credentials (use config files)
- Virtual environment
- Matched photos cache

Make sure to configure these locally before running the application.

