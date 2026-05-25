import face_recognition
import numpy as np
from PIL import Image

from models.person import Person


class FaceService:
    """Handles face encoding and matching operations."""

    def __init__(self, tolerance=0.6):
        self.tolerance = tolerance

    def get_face_encoding(self, image_path):
        """
        Load an image and return the face encoding.
        Returns None if no face is detected.
        Returns the first face encoding if multiple faces are found.
        """
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)

        if len(encodings) == 0:
            return None

        return encodings[0]

    def find_matches(self, uploaded_encoding, persons):
        """
        Compare an uploaded face encoding against all registered persons.
        Returns a list of matches with confidence scores, sorted by best match.
        """
        if not persons:
            return []

        matches = []

        known_encodings = []
        for person in persons:
            known_encodings.append(person.get_encoding())

        # Calculate face distances (lower = more similar)
        face_distances = face_recognition.face_distance(known_encodings, uploaded_encoding)

        for i, distance in enumerate(face_distances):
            if distance <= self.tolerance:
                confidence = round((1 - distance) * 100, 2)
                matches.append({
                    "person": persons[i],
                    "confidence": confidence,
                    "distance": round(distance, 4),
                })

        # Sort by confidence (highest first)
        matches.sort(key=lambda x: x["confidence"], reverse=True)
        return matches

    def validate_image(self, image_path):
        """
        Validate that the image is readable and contains at least one face.
        Returns (is_valid, message).
        """
        try:
            img = Image.open(image_path)
            img.verify()
        except Exception:
            return False, "Invalid image file."

        image = face_recognition.load_image_file(image_path)
        face_locations = face_recognition.face_locations(image)

        if len(face_locations) == 0:
            return False, "No face detected in the image. Please upload a clear photo with a visible face."

        if len(face_locations) > 1:
            return True, "Multiple faces detected. Using the first face found."

        return True, "Face detected successfully."
