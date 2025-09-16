CREATE DATABASE internship_db;

USE internship_db;

CREATE TABLE interns (
    emp_id VARCHAR(20) PRIMARY KEY,
    student_name VARCHAR(100),
    domain VARCHAR(100),
    duration VARCHAR(50),
    start_date DATE,
    award_date DATE,
    photo VARCHAR(255),
    qr_generated BOOLEAN DEFAULT FALSE
);

CREATE TABLE admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- Example: Insert admin after generating hashed password in Python
-- INSERT INTO admins (username, password) VALUES ('admin', 'hashed_password_here');