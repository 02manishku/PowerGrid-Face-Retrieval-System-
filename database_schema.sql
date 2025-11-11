-- POWERGRID Face Recognition Database Schema
-- Run this script to recreate the database and tables

CREATE DATABASE IF NOT EXISTS powergrid_face_db;
USE powergrid_face_db;

-- Users table for authentication
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_employee_id (employee_id)
);

-- Employees table - stores employee information and face embeddings
CREATE TABLE IF NOT EXISTS employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    embedding JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_employee_id (employee_id)
);

-- Events table - stores event information
CREATE TABLE IF NOT EXISTS events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_name VARCHAR(255) NOT NULL,
    venue VARCHAR(255),
    date DATE,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_event_name (event_name),
    INDEX idx_date (date)
);

-- Matched photos table - stores face embeddings from event photos
CREATE TABLE IF NOT EXISTS matched_photos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id VARCHAR(50),
    event_id INT NOT NULL,
    photo_path VARCHAR(500) NOT NULL,
    similarity_score DECIMAL(5,4),
    embedding JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    INDEX idx_employee_id (employee_id),
    INDEX idx_event_id (event_id),
    INDEX idx_similarity (similarity_score)
);

