import os
import uuid

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename

from models import db
from models.person import Person
from services.face_service import FaceService

search_bp = Blueprint("search", __name__)
face_service = FaceService()


def allowed_file(filename):
    return "." in filename and \
        filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]


@search_bp.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "GET":
        return render_template("search.html")

    # Validate image upload
    if "image" not in request.files:
        flash("Please upload an image to search.", "error")
        return redirect(url_for("search.search"))

    file = request.files["image"]
    if file.filename == "":
        flash("No image selected.", "error")
        return redirect(url_for("search.search"))

    if not allowed_file(file.filename):
        flash("Invalid file type. Please upload PNG, JPG, or JPEG.", "error")
        return redirect(url_for("search.search"))

    # Save temporarily
    filename = f"search_{uuid.uuid4().hex}_{secure_filename(file.filename)}"
    upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
    file.save(upload_path)

    # Get face encoding from uploaded image
    encoding = face_service.get_face_encoding(upload_path)

    # Clean up the search image
    os.remove(upload_path)

    if encoding is None:
        flash("No face detected in the uploaded image. Please try a clearer photo.", "error")
        return redirect(url_for("search.search"))

    # Compare against all registered persons
    persons = Person.query.filter_by(status="missing").all()

    if not persons:
        flash("No missing persons registered in the database yet.", "info")
        return redirect(url_for("search.search"))

    matches = face_service.find_matches(encoding, persons)

    return render_template("results.html", matches=matches, total_checked=len(persons))


@search_bp.route("/mark-found/<int:person_id>", methods=["POST"])
def mark_found(person_id):
    person = Person.query.get_or_404(person_id)
    person.status = "found"
    db.session.commit()
    flash(f"'{person.name}' has been marked as found! 🎉", "success")
    return redirect(url_for("home"))
