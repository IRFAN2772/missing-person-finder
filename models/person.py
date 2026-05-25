import pickle
from datetime import datetime

from models import db


class Person(db.Model):
    __tablename__ = "persons"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    last_seen_location = db.Column(db.String(200), nullable=False)
    last_seen_date = db.Column(db.String(50), nullable=True)
    contact_info = db.Column(db.String(200), nullable=False)
    additional_info = db.Column(db.Text, nullable=True)
    image_filename = db.Column(db.String(255), nullable=False)
    face_encoding = db.Column(db.LargeBinary, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="missing")  # missing / found

    def set_encoding(self, encoding_array):
        """Serialize numpy array to binary for storage."""
        self.face_encoding = pickle.dumps(encoding_array)

    def get_encoding(self):
        """Deserialize binary back to numpy array."""
        return pickle.loads(self.face_encoding)

    def __repr__(self):
        return f"<Person {self.name} - {self.status}>"
