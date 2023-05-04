# Import necessary modules
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_ckeditor.fields import CKEditorField

# Define a form that includes a reCAPTCHA field
class RecaptchaFunction(FlaskForm):
    recaptcha = RecaptchaField()

# Define a form that includes a title field, a CKEditor field for content, and a submit button
class MyForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])  # Add a string field for the title and make it required
    content = CKEditorField('Content', validators=[DataRequired()])  # Add a CKEditor field for the content and make it required
    submit = SubmitField('Submit')  # Add a submit button with the label "Submit"
