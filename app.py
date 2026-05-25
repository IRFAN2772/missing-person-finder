import os

from flask import Flask, render_template

from config import Config
from models import db
from models.person import Person
from routes.register import register_bp
from routes.search import search_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure required directories exist
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(os.path.join(app.instance_path), exist_ok=True)

    # Initialize database
    db.init_app(app)

    with app.app_context():
        db.create_all()

    # Register blueprints
    app.register_blueprint(register_bp)
    app.register_blueprint(search_bp)

    # Home route
    @app.route("/")
    def home():
        total_registered = Person.query.count()
        total_missing = Person.query.filter_by(status="missing").count()
        total_found = Person.query.filter_by(status="found").count()
        return render_template(
            "index.html",
            total_registered=total_registered,
            total_missing=total_missing,
            total_found=total_found,
        )

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 7860))
    app.run(debug=False, host="0.0.0.0", port=port)
