from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models import db
from app.models.attendance import Attendance
from app.models.teacher import Teacher
from app.models.student import Student
from app.models.setting import Setting
from datetime import datetime, date, timedelta
from collections import defaultdict

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/attendance')
@login_required
def attendance_report():
    # Ambil parameter filter
    date_filter = request.args.get('date_filter', 'daily')  # daily, monthly, yearly
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Jika tidak ada filter tanggal, gunakan tanggal hari ini untuk daily
    if not start_date and date_filter == 'daily':
        start_date = date.today().strftime('%Y-%m-%d')
    if not end_date and date_filter == 'daily':
        end_date = date.today().strftime('%Y-%m-%d')
    
    # Konversi string ke objek datetime
    if start_date:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
    else:
        start_date_obj = datetime.combine(date.today().replace(day=1), datetime.min.time())
    
    if end_date:
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
    else:
        end_date_obj = datetime.combine(date.today(), datetime.max.time())
    
    # Query data absensi
    attendances = Attendance.query.filter(
        Attendance.timestamp.between(start_date_obj, end_date_obj)
    ).all()
    
    # Kelompokkan data berdasarkan status
    on_time_count = 0
    late_count = 0
    
    for attendance in attendances:
        if attendance.status == 'on_time':
            on_time_count += 1
        else:
            late_count += 1
    
    # Ambil detail absensi
    attendance_details = []
    for attendance in attendances:
        # Dapatkan nama berdasarkan barcode
        teacher = Teacher.query.filter_by(barcode=attendance.barcode).first()
        student = Student.query.filter_by(barcode=attendance.barcode).first()
        
        person_name = 'Unknown'
        person_type = 'Unknown'
        
        if teacher:
            person_name = teacher.name
            person_type = 'Guru'
        elif student:
            person_name = student.name
            person_type = 'Siswa'
        
        attendance_details.append({
            'person_name': person_name,
            'person_type': person_type,
            'attendance_type': 'Masuk' if attendance.attendance_type == 'in' else 'Pulang',
            'timestamp': attendance.timestamp,
            'status': 'Tepat Waktu' if attendance.status == 'on_time' else 'Tidak Tepat Waktu',
            'location': attendance.location
        })
    
    return render_template('reports/attendance.html', 
                         attendances=attendance_details,
                         on_time_count=on_time_count,
                         late_count=late_count,
                         total_count=len(attendances),
                         date_filter=date_filter,
                         start_date=start_date,
                         end_date=end_date)

@reports_bp.route('/rekap-attendance')
@login_required
def rekap_attendance():
    # Rekap absensi harian
    today = date.today()
    start_of_month = today.replace(day=1)
    start_of_year = today.replace(month=1, day=1)
    
    # Rekap harian
    daily_start = datetime.combine(today, datetime.min.time())
    daily_end = datetime.combine(today, datetime.max.time())
    daily_attendances = Attendance.query.filter(
        Attendance.timestamp.between(daily_start, daily_end)
    ).all()
    
    # Rekap bulanan
    monthly_start = datetime.combine(start_of_month, datetime.min.time())
    monthly_end = datetime.combine(today, datetime.max.time())
    monthly_attendances = Attendance.query.filter(
        Attendance.timestamp.between(monthly_start, monthly_end)
    ).all()
    
    # Rekap tahunan
    yearly_start = datetime.combine(start_of_year, datetime.min.time())
    yearly_end = datetime.combine(today, datetime.max.time())
    yearly_attendances = Attendance.query.filter(
        Attendance.timestamp.between(yearly_start, yearly_end)
    ).all()
    
    # Fungsi untuk menghitung statistik
    def count_attendance_stats(attendances):
        stats = defaultdict(lambda: {'present': 0, 'late': 0})
        
        for attendance in attendances:
            # Dapatkan nama berdasarkan barcode
            teacher = Teacher.query.filter_by(barcode=attendance.barcode).first()
            student = Student.query.filter_by(barcode=attendance.barcode).first()
            
            person_name = 'Unknown'
            if teacher:
                person_name = teacher.name
            elif student:
                person_name = student.name
            
            if attendance.status == 'on_time':
                stats[person_name]['present'] += 1
            else:
                stats[person_name]['late'] += 1
        
        return dict(stats)
    
    daily_stats = count_attendance_stats(daily_attendances)
    monthly_stats = count_attendance_stats(monthly_attendances)
    yearly_stats = count_attendance_stats(yearly_attendances)
    
    return render_template('reports/rekap.html',
                         daily_stats=daily_stats,
                         monthly_stats=monthly_stats,
                         yearly_stats=yearly_stats,
                         today=today,
                         start_of_month=start_of_month,
                         start_of_year=start_of_year)