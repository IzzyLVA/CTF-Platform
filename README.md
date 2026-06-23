# JUNIOR MEMBER :: CTF

A beginner-friendly Capture The Flag (CTF) platform built with Flask, Python, HTML, CSS, JavaScript, and Docker.

This project was designed to provide hands-on cybersecurity training through interactive web challenges while maintaining a simple, terminal-inspired user interface.

---

## Features

- User Registration & Login
- Challenge-Based Learning
- Server-Side Flag Validation
- Progress Tracking
- Challenge Completion Tracking
- Scoreboard & Leaderboard
- Progress Reset Functionality
- Docker Support
- Terminal-Inspired Cybersecurity Theme

---

## Included Challenges

### Portal
A beginner SQL Injection challenge focused on authentication bypass techniques.

### Cookies
A session hijacking challenge that teaches users how cookies and session data can be manipulated.

### Vault
A challenge that requires investigation and enumeration techniques to locate hidden information.

---

## Technologies Used

- Python
- Flask
- SQLite
- HTML5
- CSS3
- JavaScript
- Docker

---

## Installation

### Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Initialize the Database

```bash
python setup_db.py
```

### Start the Application

```bash
python app.py
```

The application will be available at:

```text
http://127.0.0.1:5000
```

---

## Docker Deployment

Build the container:

```bash
docker build -t junior-member-ctf .
```

Run the container:

```bash
docker run -p 5000:5000 junior-member-ctf
```

---

## Educational Purpose

This platform was created for educational and training purposes. The included vulnerabilities are intentionally designed to teach common web security concepts in a safe environment.

Topics covered include:

- SQL Injection
- Session Security
- Authentication Weaknesses
- Web Enumeration
- Basic CTF Methodology

---

## Project Goals

The primary goals of this project are:

- Teach cybersecurity fundamentals through hands-on learning
- Provide beginner-friendly CTF challenges
- Demonstrate secure and insecure web application concepts
- Serve as a portfolio project for cybersecurity students

---

## Disclaimer

This project is intended for educational use only. Do not use techniques learned from this platform against systems you do not own or have explicit permission to test.

---

## Author

Created by IzzyLVA. as part of cybersecurity education and training initiatives.
