---
title: Missing Person Finder
emoji: 🔍
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
---

# Missing Person Finder

A Flask-based web application that uses **facial recognition technology** to help find missing persons. It allows users to register missing individuals with their photos and details, then search for matches by uploading new photos.

---

## Table of Contents

1. [Tech Stack](#tech-stack)
2. [How It Works](#how-it-works)
3. [Project Structure](#project-structure)
4. [Installation & Setup](#installation--setup)
5. [Libraries & Their Roles](#libraries--their-roles)
6. [Core Logic Explained](#core-logic-explained)
7. [Database Schema](#database-schema)
8. [Application Flow](#application-flow)
9. [API Routes](#api-routes)
10. [Configuration](#configuration)

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend Framework** | Flask 3.x | Web server, routing, templating |
| **Database** | SQLite | Lightweight file-based database |
| **ORM** | SQLAlchemy (via Flask-SQLAlchemy) | Database abstraction & models |
| **Face Recognition** | `face_recognition` library | Face detection, encoding & comparison |
| **ML Backend** | dlib (C++) | Deep learning face model (used by face_recognition) |
| **Math/Arrays** | NumPy | Face encoding vectors (128-dimensional arrays) |
| **Image Processing** | Pillow (PIL) | Image validation & manipulation |
| **Frontend** | HTML5, Bootstrap 5, Jinja2 | Responsive UI templates |
| **Icons** | Bootstrap Icons | UI iconography |

---

## How It Works

### High-Level Flow

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  User       │     │  Flask App   │     │  face_recognition│
│  (Browser)  │────▶│  (Routes)    │────▶│  (dlib/ML)      │
└─────────────┘     └──────────────┘     └─────────────────┘
                           │                       │
                           ▼                       ▼
                    ┌──────────────┐     ┌─────────────────┐
                    │  SQLite DB   │     │  128-d Face      │
                    │  (Persons)   │◀────│  Encoding Vector │
                    └──────────────┘     └─────────────────┘
```

### The Facial Recognition Process

1. **Face Detection** — Locate face(s) in an image using HOG (Histogram of Oriented Gradients) algorithm
2. **Face Encoding** — Convert the detected face into a 128-dimensional vector (numerical representation)
3. **Storage** — Serialize the encoding as binary (pickle) and store in SQLite
4. **Comparison** — Calculate Euclidean distance between encodings to determine similarity
5. **Matching** — If distance ≤ 0.6 (tolerance), it's considered a match

---

## Project Structure

```
missing-person-finder/
├── app.py                      # Application entry point & factory
├── config.py                   # All configuration settings
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
├── DOCUMENTATION.md            # This file
│
├── models/
│   ├── __init__.py             # SQLAlchemy db instance
│   └── person.py               # Person model (table schema)
│
├── routes/
│   ├── __init__.py
│   ├── register.py             # Registration endpoints
│   └── search.py               # Search & mark-found endpoints
│
├── services/
│   ├── __init__.py
│   └── face_service.py         # Face encoding & matching logic
│
├── templates/
│   ├── base.html               # Base layout (navbar, footer, flash)
│   ├── index.html              # Home page with stats
│   ├── register.html           # Registration form
│   ├── search.html             # Image upload for search
│   └── results.html            # Match results display
│
├── static/
│   └── uploads/                # Stored person images
│       └── .gitkeep
│
└── instance/
    └── missing_finder.db       # SQLite database (auto-created)
```

---

## Installation & Setup

### Prerequisites

- Python 3.10+
- Visual Studio Build Tools (Windows) — needed for dlib C++ compilation
- CMake (usually bundled with dlib build)

### Steps

```bash
# 1. Navigate to project
cd f:\personal\missing-person-finder

# 2. Create virtual environment
python -m venv venv

# 3. Activate it
.\venv\Scripts\Activate.ps1          # PowerShell
# OR
.\venv\Scripts\activate.bat          # CMD

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the application
python app.py

# 6. Open in browser
# http://localhost:5000
```

### If dlib fails to install

dlib requires C++ build tools. On Windows:
1. Install [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. Select "Desktop development with C++" workload
3. Retry `pip install dlib`

---

## Libraries & Their Roles

### 1. Flask (`flask`)
- **Role**: Web framework
- **We use it for**: HTTP routing, request handling, template rendering, flash messages, file uploads
- **Key features used**: Blueprints (modular routes), Jinja2 templating, `request.files` for uploads

### 2. Flask-SQLAlchemy (`flask-sqlalchemy`)
- **Role**: SQLAlchemy integration with Flask
- **We use it for**: Defining database models, running queries, managing sessions
- **Key features used**: `db.Model` base class, `db.session.commit()`, `query.filter_by()`

### 3. face_recognition (`face-recognition`)
- **Role**: High-level facial recognition API (wraps dlib)
- **We use it for**:
  - `face_recognition.load_image_file(path)` — Load image as numpy array
  - `face_recognition.face_encodings(image)` — Get 128-d face vector
  - `face_recognition.face_locations(image)` — Detect face bounding boxes
  - `face_recognition.face_distance(known, unknown)` — Calculate similarity
- **How it works internally**: Uses a pre-trained deep neural network (ResNet) from dlib to generate face embeddings

### 4. dlib (`dlib`)
- **Role**: C++ ML toolkit with Python bindings
- **We use it for**: Backend engine for face_recognition library
- **Key model**: `dlib_face_recognition_resnet_model_v1` — trained on millions of faces
- **Output**: 128 floating-point numbers representing facial features

### 5. NumPy (`numpy`)
- **Role**: Numerical computing
- **We use it for**: Face encodings are numpy arrays (shape: `(128,)`)
- **Key operation**: Euclidean distance calculation between face vectors

### 6. Pillow (`Pillow`)
- **Role**: Image processing
- **We use it for**: Image validation (`Image.open().verify()`) before passing to face_recognition

### 7. Werkzeug (`werkzeug`)
- **Role**: WSGI utilities (comes with Flask)
- **We use it for**: `secure_filename()` — sanitizes uploaded filenames to prevent path traversal attacks

---

## Core Logic Explained

### Face Encoding (Registration)

```python
# When a user registers a missing person:
image = face_recognition.load_image_file(image_path)  # Load as RGB numpy array
encodings = face_recognition.face_encodings(image)     # Returns list of 128-d vectors

# encodings[0] is a numpy array like:
# array([-0.1234, 0.5678, -0.0912, ..., 0.3456])  # 128 values

# We serialize it for SQLite storage:
binary_data = pickle.dumps(encodings[0])  # Convert to bytes
# Stored in the 'face_encoding' BLOB column
```

### Face Matching (Search)

```python
# When a user uploads a photo to search:
uploaded_encoding = get_face_encoding(uploaded_image)  # 128-d vector

# Load all registered persons' encodings
known_encodings = [person.get_encoding() for person in all_persons]

# Calculate Euclidean distances
distances = face_recognition.face_distance(known_encodings, uploaded_encoding)
# Returns array like: [0.45, 0.72, 0.38, 0.91, ...]

# Match criteria: distance <= 0.6 (tolerance)
# Lower distance = more similar faces
# Confidence = (1 - distance) * 100
#   distance 0.3 → 70% confidence
#   distance 0.4 → 60% confidence
#   distance 0.6 → 40% confidence (threshold)
```

### Distance & Tolerance Explained

| Distance | Confidence | Meaning |
|----------|-----------|---------|
| 0.0 | 100% | Identical (same photo) |
| 0.0–0.4 | 60–100% | Very likely the same person |
| 0.4–0.6 | 40–60% | Possibly the same person |
| > 0.6 | < 40% | Likely different people (no match) |

The tolerance of **0.6** is the default threshold. Lowering it reduces false positives but may miss matches.

---

## Database Schema

### `persons` Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER (PK) | Auto-increment primary key |
| `name` | VARCHAR(100) | Full name of person |
| `age` | INTEGER | Age of person |
| `gender` | VARCHAR(10) | Male / Female / Other |
| `last_seen_location` | VARCHAR(200) | Where they were last seen |
| `last_seen_date` | VARCHAR(50) | Date last seen (optional) |
| `contact_info` | VARCHAR(200) | Phone/email for contact |
| `additional_info` | TEXT | Extra details (optional) |
| `image_filename` | VARCHAR(255) | Stored image filename |
| `face_encoding` | BLOB | Pickled 128-d numpy array |
| `created_at` | DATETIME | Registration timestamp |
| `status` | VARCHAR(20) | `missing` or `found` |

---

## Application Flow

### Registration Flow

```
User fills form + uploads photo
         │
         ▼
Validate form fields (name, age, gender, location, contact)
         │
         ▼
Validate file (type: png/jpg/jpeg, size: <16MB)
         │
         ▼
Save image to static/uploads/ with UUID prefix
         │
         ▼
face_service.validate_image() → detect face in image
         │
    ┌────┴────┐
    │ No face │ → Delete image, show error
    └─────────┘
         │ Face found
         ▼
face_service.get_face_encoding() → 128-d vector
         │
         ▼
Create Person record, serialize encoding as BLOB
         │
         ▼
db.session.commit() → Saved to SQLite
         │
         ▼
Flash success message, redirect
```

### Search Flow

```
User uploads photo
         │
         ▼
Save temporarily, get face encoding
         │
         ▼
Delete temporary file (we only need the encoding)
         │
    ┌────┴────┐
    │ No face │ → Show error
    └─────────┘
         │ Face found
         ▼
Load all persons with status="missing" from DB
         │
         ▼
face_service.find_matches() → compare against all encodings
         │
         ▼
Calculate distances, filter by tolerance (≤ 0.6)
         │
         ▼
Sort matches by confidence (highest first)
         │
         ▼
Render results page with match cards + "Mark as Found" button
```

### Mark as Found Flow

```
User clicks "Mark as Found" on a match
         │
         ▼
POST /mark-found/<person_id>
         │
         ▼
person.status = "found"
db.session.commit()
         │
         ▼
Redirect to home → "Found & Reunited" counter increments
```

---

## API Routes

| Method | Route | Blueprint | Purpose |
|--------|-------|-----------|---------|
| GET | `/` | app | Home page with stats |
| GET | `/register` | register | Show registration form |
| POST | `/register` | register | Submit registration |
| GET | `/search` | search | Show search/upload form |
| POST | `/search` | search | Upload image & find matches |
| POST | `/mark-found/<id>` | search | Mark person as found |

---

## Configuration

All settings are in `config.py`:

```python
SECRET_KEY              # Flask session encryption key
SQLALCHEMY_DATABASE_URI # "sqlite:///instance/missing_finder.db"
UPLOAD_FOLDER           # "static/uploads/"
MAX_CONTENT_LENGTH     # 16MB max upload size
ALLOWED_EXTENSIONS     # {"png", "jpg", "jpeg"}
FACE_MATCH_TOLERANCE   # 0.6 (Euclidean distance threshold)
```

---

## Security Measures

- **Filename sanitization**: `secure_filename()` prevents path traversal
- **File type validation**: Only PNG/JPG/JPEG allowed
- **File size limit**: 16MB max
- **UUID prefixed filenames**: Prevents overwriting existing files
- **Temporary search files deleted**: Search images are removed after encoding
- **Flash messages**: Server-side validation feedback

---

## Future Enhancements (Not Yet Implemented)

- View all registered persons page
- Edit/delete registered persons
- Admin authentication
- Multiple photos per person for better accuracy
- Email/SMS notification when match found
- Export data as CSV
- Docker deployment
