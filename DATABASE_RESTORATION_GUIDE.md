# Database Restoration Guide
## Rebuilding Your POWERGRID Face Recognition Database

---

## 📋 Overview

This guide will help you:
1. Install MySQL on Windows
2. Recreate the database schema
3. Rebuild all employee and event data
4. Get your project running again

**Estimated Time**: 30-45 minutes (depending on number of photos)

---

## Step 1: Install MySQL

### Option A: MySQL Installer (Recommended for Windows)

1. **Download MySQL**
   - Go to: https://dev.mysql.com/downloads/installer/
   - Download **MySQL Installer for Windows** (the full installer, ~400MB)
   - Choose: **mysql-installer-community-8.0.x.x.msi** (or latest version)

2. **Install MySQL**
   - Run the installer
   - Choose **Developer Default** or **Server only**
   - Follow the installation wizard
   - **Important**: Remember the root password you set! (Use `!manish!` if you want to keep it the same)
   - Complete the installation

3. **Verify Installation**
   - Open Command Prompt or PowerShell
   - Run: `mysql --version`
   - You should see MySQL version info

### Option B: XAMPP (Easier Alternative)

1. Download XAMPP: https://www.apachefriends.org/
2. Install XAMPP (includes MySQL)
3. Start MySQL from XAMPP Control Panel

---

## Step 2: Create Database and Tables

1. **Open MySQL Command Line Client**
   - Search for "MySQL Command Line Client" in Windows Start Menu
   - Enter your root password (or `!manish!` if you set it)

   **OR** use MySQL Workbench (GUI tool):
   - Download: https://dev.mysql.com/downloads/workbench/
   - Connect with root credentials

2. **Run the Schema File**

   **Method 1: Using Command Line**
   ```bash
   mysql -u root -p < database_schema.sql
   ```
   (Enter password when prompted)

   **Method 2: Using MySQL Workbench**
   - Open MySQL Workbench
   - File → Open SQL Script → Select `database_schema.sql`
   - Click Execute (⚡ icon)

   **Method 3: Copy-Paste**
   - Open `database_schema.sql` in a text editor
   - Copy all content
   - Paste into MySQL Command Line Client or Workbench
   - Execute

---

## Step 3: Verify Database Creation

Run these commands in MySQL:

```sql
USE powergrid_face_db;
SHOW TABLES;
```

You should see:
- users
- employees
- events
- matched_photos

```sql
DESCRIBE employees;
DESCRIBE events;
DESCRIBE matched_photos;
DESCRIBE users;
```

All tables should exist with correct columns.

---

## Step 4: Create Test User Account (Optional but Recommended)

You'll need at least one user to log in. Run this in MySQL:

```sql
USE powergrid_face_db;

-- Create a test user (replace with actual employee ID)
INSERT INTO users (employee_id, password) 
VALUES ('1001', 'test123');
```

**Note**: The password is plaintext in your current setup. You can change it later.

---

## Step 5: Rebuild Employee Database

1. **Activate Your Python Virtual Environment**
   ```powershell
   cd "C:\Users\Manish\Desktop\powergrid - Copy"
   .\faceenv\Scripts\Activate.ps1
   ```

2. **Run Employee Encoder Script**
   ```powershell
   python employee_encoder_deepface.py
   ```

   This script will:
   - Read all folders in `employee_data/`
   - Process each employee's photos
   - Generate face embeddings using DeepFace
   - Insert into MySQL `employees` table

   **What to expect:**
   ```
   [+] Encoded John Doe - photo1.jpg
   [+] Encoded John Doe - photo2.jpg
   [✅] Saved 8 employees to MySQL database.
   ```

   **Time**: Depends on number of employees and photos (typically 1-5 minutes)

---

## Step 6: Rebuild Event Photos Database

1. **Run Event Encoder Script**
   ```powershell
   python main.py
   ```

   This script will:
   - Read all folders in `event_data/`
   - Process each event's photos
   - Extract faces from all images
   - Generate embeddings for each detected face
   - Insert into MySQL `matched_photos` and `events` tables

   **What to expect:**
   ```
   [⚙️] Rebuilding event face database into MySQL...
   [📁] Inserted event: powergrid (ID: 1) ✅
   [🚀] Encoding 60 photos using multiprocessing (2 workers)...
   Encoding 'powergrid': 100%|████████| 60/60 [02:30<00:00, 2.5s/image]
   [✅] Finished event: powergrid — Encoded 60/60
   
   [🏁] All done. Total events: 4, total faces encoded: 240
   ```

   **Time**: This takes longer! Each photo processes multiple faces. 
   - 60 photos ≈ 2-5 minutes
   - 200 photos ≈ 10-20 minutes
   - Be patient, it shows a progress bar!

---

## Step 7: Test the Application

1. **Make sure MySQL is running**
   - Check MySQL service is active

2. **Start Flask Application**
   ```powershell
   python app.py
   ```

3. **Open Browser**
   - Go to: http://127.0.0.1:5000
   - Login with:
     - Employee ID: `1001` (or any employee ID you created in users table)
     - Password: `test123` (or the password you set)

4. **Verify It Works**
   - You should see events where you appear (if matching was successful)
   - Click on events to see photos
   - Test download features

---

## 🔧 Troubleshooting

### Error: "Access denied for user 'root'@'localhost'"

**Solution**: Your MySQL password might be different
- Check if you set a different password during installation
- Update password in `app.py`, `main.py`, `employee_encoder_deepface.py`:
  ```python
  password="your_actual_password"
  ```

### Error: "Unknown database 'powergrid_face_db'"

**Solution**: Database wasn't created
- Run `database_schema.sql` again
- Or manually create:
  ```sql
  CREATE DATABASE powergrid_face_db;
  ```

### Error: "Table 'employees' doesn't exist"

**Solution**: Tables weren't created
- Run the full `database_schema.sql` script
- Make sure you're using the correct database:
  ```sql
  USE powergrid_face_db;
  ```

### Error: "ModuleNotFoundError: No module named 'deepface'"

**Solution**: Virtual environment not activated or packages missing
```powershell
.\faceenv\Scripts\Activate.ps1
pip install deepface flask mysql-connector-python numpy scipy opencv-python tqdm
```

### No Photos Appearing After Rebuild

**Possible Causes:**
1. **No matches found**: The similarity threshold (0.55) might be too strict
2. **Employees not in database**: Make sure `employee_encoder_deepface.py` ran successfully
3. **Events not processed**: Make sure `main.py` completed without errors
4. **Login issue**: Verify the employee_id you're logging in with exists in both `users` and `employees` tables

**Debug Steps:**
```sql
-- Check if employees exist
SELECT COUNT(*) FROM employees;

-- Check if events exist
SELECT * FROM events;

-- Check if matched_photos have embeddings
SELECT COUNT(*) FROM matched_photos WHERE embedding IS NOT NULL;

-- Check specific employee
SELECT * FROM employees WHERE employee_id = '1001';
```

---

## 📊 Database Verification Commands

After rebuilding, verify everything is correct:

```sql
USE powergrid_face_db;

-- Count records
SELECT 'Employees' AS table_name, COUNT(*) AS count FROM employees
UNION ALL
SELECT 'Events', COUNT(*) FROM events
UNION ALL
SELECT 'Matched Photos', COUNT(*) FROM matched_photos
UNION ALL
SELECT 'Users', COUNT(*) FROM users;

-- Check sample data
SELECT employee_id, name, email FROM employees LIMIT 5;
SELECT event_name, venue, date FROM events;
SELECT COUNT(*) as total_faces, COUNT(DISTINCT event_id) as events_with_faces 
FROM matched_photos;
```

---

## 🚀 Quick Setup Script

If you want to automate this, create a PowerShell script:

```powershell
# restore_database.ps1
Write-Host "Creating database..."
mysql -u root -p!manish! < database_schema.sql

Write-Host "Rebuilding employee data..."
python employee_encoder_deepface.py

Write-Host "Rebuilding event data..."
python main.py

Write-Host "Done! Starting Flask app..."
python app.py
```

---

## 📝 Important Notes

1. **Backup Next Time**: Before deleting MySQL again, export your data:
   ```bash
   mysqldump -u root -p powergrid_face_db > backup.sql
   ```

2. **Image Paths**: Make sure photo paths in `matched_photos` table are correct. They should be relative to your project root.

3. **Performance**: First run of `main.py` will take time. Subsequent runs are faster if you're only adding new events.

4. **Similarity Threshold**: Current threshold is 0.55 in `app.py`. If you're not getting matches, you might need to adjust this (lower = more matches, but more false positives).

---

## ✅ Checklist

- [ ] MySQL installed and running
- [ ] Database `powergrid_face_db` created
- [ ] All 4 tables created (users, employees, events, matched_photos)
- [ ] Test user created in `users` table
- [ ] Employee data rebuilt (ran `employee_encoder_deepface.py`)
- [ ] Event data rebuilt (ran `main.py`)
- [ ] Flask app starts without errors
- [ ] Can log in successfully
- [ ] Photos appear in the interface

---

**Need Help?** Check the troubleshooting section or verify each step was completed successfully.

