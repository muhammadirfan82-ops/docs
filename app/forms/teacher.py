from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class TeacherForm(FlaskForm):
    nip = StringField('NIP', validators=[DataRequired(), Length(min=6, max=20)])
    name = StringField('Nama Lengkap', validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField('No. Telepon', validators=[Length(max=15)])
    email = StringField('Email', validators=[Length(max=120)])
    address = TextAreaField('Alamat')
    submit = SubmitField('Simpan')