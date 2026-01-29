from app.models import db
from datetime import time

class Setting(db.Model):
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    attendance_start_time = db.Column(db.Time, default=time(7, 0))  # Jam masuk: 07:00
    attendance_end_time = db.Column(db.Time, default=time(16, 0))   # Jam pulang: 16:00
    late_time = db.Column(db.Time, default=time(7, 15))            # Terlambat setelah: 07:15
    must_present_for_leave = db.Column(db.Boolean, default=True)    # Harus absen masuk sebelum bisa absen pulang
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    def __repr__(self):
        return f'<Setting {self.id}>'