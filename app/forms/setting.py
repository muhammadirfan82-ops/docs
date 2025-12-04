from flask_wtf import FlaskForm
from wtforms import TimeField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class SettingForm(FlaskForm):
    attendance_start_time = TimeField('Jam Masuk', validators=[DataRequired()])
    attendance_end_time = TimeField('Jam Pulang', validators=[DataRequired()])
    late_time = TimeField('Batas Keterlambatan', validators=[DataRequired()])
    must_present_for_leave = BooleanField('Wajib Absen Masuk Sebelum Bisa Absen Pulang')
    submit = SubmitField('Simpan Pengaturan')