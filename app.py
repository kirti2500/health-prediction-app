"""
app.py

Main Flask app. Routes for the patient health-prediction tool:

"""

from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Patient
from validators import validate_patient_form
from predictor import generate_remarks
import os



app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///patients.db"
app.config["SECRET_KEY"] = os.urandom(24)  

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/")
def index():
    # newest first, just feels more natural when demoing
    patients = Patient.query.order_by(Patient.created_at.desc()).all()
    return render_template("index.html", patients=patients)


@app.route("/add", methods=["GET", "POST"])
def add_patient():
    if request.method == "POST":
        errors, cleaned = validate_patient_form(request.form)

        if errors:
            
            return render_template(
                "form.html",
                errors=errors,
                form_data=request.form,
                mode="add"
            )

        remarks = generate_remarks(
            cleaned["glucose"], cleaned["haemoglobin"], cleaned["cholesterol"]
        )

        new_patient = Patient(
            full_name=cleaned["full_name"],
            date_of_birth=cleaned["date_of_birth"],
            email=cleaned["email"],
            glucose=cleaned["glucose"],
            haemoglobin=cleaned["haemoglobin"],
            cholesterol=cleaned["cholesterol"],
            remarks=remarks,
        )
        db.session.add(new_patient)
        db.session.commit()

        flash("Patient record added successfully.", "success")
        return redirect(url_for("index"))

    return render_template("form.html", errors={}, form_data={}, mode="add")


@app.route("/patient/<int:patient_id>")
def view_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    return render_template("view.html", patient=patient)


@app.route("/edit/<int:patient_id>", methods=["GET", "POST"])
def edit_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)

    if request.method == "POST":
        errors, cleaned = validate_patient_form(request.form)

        if errors:
            return render_template(
                "form.html",
                errors=errors,
                form_data=request.form,
                mode="edit",
                patient_id=patient_id
            )

        
        remarks = generate_remarks(
            cleaned["glucose"], cleaned["haemoglobin"], cleaned["cholesterol"]
        )

        patient.full_name = cleaned["full_name"]
        patient.date_of_birth = cleaned["date_of_birth"]
        patient.email = cleaned["email"]
        patient.glucose = cleaned["glucose"]
        patient.haemoglobin = cleaned["haemoglobin"]
        patient.cholesterol = cleaned["cholesterol"]
        patient.remarks = remarks

        db.session.commit()
        flash("Patient record updated.", "success")
        return redirect(url_for("index"))

    
    form_data = {
        "full_name": patient.full_name,
        "email": patient.email,
        "date_of_birth": patient.date_of_birth.strftime("%Y-%m-%d"),
        "glucose": patient.glucose,
        "haemoglobin": patient.haemoglobin,
        "cholesterol": patient.cholesterol,
    }
    return render_template(
        "form.html", errors={}, form_data=form_data, mode="edit", patient_id=patient_id
    )


@app.route("/delete/<int:patient_id>", methods=["POST"])
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    db.session.delete(patient)
    db.session.commit()
    flash("Patient record deleted.", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)