import os
import uuid

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename

from models import db
from models.person import Person
from services.face_service import FaceService

register_bp = Blueprint("register", __name__)
face_service = FaceService()


def allowed_file(filename):
    return "." in filename and \
        filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]


@register_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    # Validate form fields
    name = request.form.get("name", "").strip()
    age = request.form.get("age", "").strip()
    gender = request.form.get("gender", "").strip()
    last_seen_location = request.form.get("last_seen_location", "").strip()
    last_seen_date = request.form.get("last_seen_date", "").strip()
    contact_info = request.form.get("contact_info", "").strip()
    additional_info = request.form.get("additional_info", "").strip()

    if not all([name, age, gender, last_seen_location, contact_info]):
        flash("Please fill in all required fields.", "error")
        return redirect(url_for("register.register"))

    # Validate age
    try:
        age = int(age)
        if age < 0 or age > 150:
            raise ValueError
    except ValueError:
        flash("Please enter a valid age.", "error")
        return redirect(url_for("register.register"))

    # Validate image
    if "image" not in request.files:
        flash("Please upload an image.", "error")
        return redirect(url_for("register.register"))

    file = request.files["image"]
    if file.filename == "":
        flash("No image selected.", "error")
        return redirect(url_for("register.register"))

    if not allowed_file(file.filename):
        flash("Invalid file type. Please upload PNG, JPG, or JPEG.", "error")
        return redirect(url_for("register.register"))

    # Save the image
    filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
    upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
    file.save(upload_path)

    # Validate face in image
    is_valid, message = face_service.validate_image(upload_path)
    if not is_valid:
        os.remove(upload_path)
        flash(message, "error")
        return redirect(url_for("register.register"))

    # Get face encoding
    encoding = face_service.get_face_encoding(upload_path)
    if encoding is None:
        os.remove(upload_path)
        flash("Could not encode the face. Please try a different image.", "error")
        return redirect(url_for("register.register"))

    # Save to database
    person = Person(
        name=name,
        age=age,
        gender=gender,
        last_seen_location=last_seen_location,
        last_seen_date=last_seen_date,
        contact_info=contact_info,
        additional_info=additional_info,
        image_filename=filename,
    )
    person.set_encoding(encoding)

    db.session.add(person)
    db.session.commit()

    flash(f"'{name}' has been registered successfully.", "success")
    return redirect(url_for("register.register"))
