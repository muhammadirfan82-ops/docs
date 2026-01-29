from app.models import db
from datetime import datetime

class Attendance(db.Model):
    __tablename__ = 'attendances'
    
    id = db.Column(db.Integer, primary_key=True)
    barcode = db.Column(db.String(50), nullable=False)
    attendance_type = db.Column(db.String(10), nullable=False)  # 'in' for masuk, 'out' for pulang
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    location = db.Column(db.String(200))  # Lokasi absensi
    status = db.Column(db.String(20), default='on_time')  # 'on_time', 'late', 'early_leave'
    note = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Attendance {self.barcode} {self.attendance_type}>'