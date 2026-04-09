# Overview

As a software developer, I am focused on expanding my ability to build modern web applications that use cloud services for persistent data storage. With this project, my goal was to strengthen my understanding of cloud databases, data relationships, and how web applications can interact with remote services in real time.

LoreForge is a web-based world-building application that allows users to create and manage fantasy factions and characters. The software integrates with Google Firebase Firestore as its cloud database, where all faction data, character records, mentorship relationships, and activity logs are stored. Users can create, view, edit, and delete both factions and characters through the web interface, while the data is stored and retrieved directly from the cloud.

The purpose of this software was to learn how cloud databases can replace local storage solutions while maintaining full CRUD functionality, data validation, and relationship management across multiple collections.

# Cloud Database

This project uses **Google Firebase Firestore** as its cloud database service. Firestore is a NoSQL document database that stores data in collections and documents, making it flexible for applications with evolving structures and nested relationships.

The database currently contains three main collections:

- **factions**
  - Stores faction information such as name and leader name
- **characters**
  - Stores character name, role, faction ID, mentor ID, and creation date
- **activity_logs**
  - Stores world events such as faction creation, character updates, and deletions

Relationships are maintained through document IDs:

- `faction_id` connects characters to factions
- `mentor_id` connects characters to other characters

This allows the application to build recursive mentorship trees and preserve world structure.

# Development Environment

## Tools Used

- **Visual Studio Code** — primary development environment
- **Git & GitHub** — version control and project tracking
- **Firebase Console** — cloud database setup and monitoring
- **Google Firestore** — cloud data storage

## Programming Language and Libraries

- **Python**
- **Django**
- **Firebase Admin SDK**
- **HTML**
- **CSS**
- **JavaScript**

Main Python library used for cloud integration:

```bash
pip install firebase-admin
```

## Execution Instructions

Run locally with:

```bash
python manage.py runserver
```

Then open:

```text
http://127.0.0.1:8000/
```

# Useful Websites

- [Firebase Documentation](https://firebase.google.com/docs/firestore)
- [Django Documentation](https://docs.djangoproject.com/)
- [Firebase Admin Python SDK](https://firebase.google.com/docs/admin/setup)
- [MDN Web Docs](https://developer.mozilla.org/)
- [Stack Overflow](https://stackoverflow.com/)

# Future Work

- Improve visual design and responsive layout
- Add user authentication with Firebase Auth
- Add real-time Firestore listeners for live updates
- Improve mentorship tree visualization
- Add search and filtering tools for large worlds
