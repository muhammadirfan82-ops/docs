from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import db
from app.models.attendance import Attendance
from app.models.teacher import Teacher
from app.models.student import Student
from app.models.setting import Setting
from datetime import datetime, date, time

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/')
def index():
    # Halaman utama untuk scan barcode
    return render_template('attendance/index.html')

@attendance_bp.route('/scan', methods=['POST'])
def scan_attendance():
    barcode = request.form.get('barcode')
    location = request.form.get('location', 'Unknown')
    
    if not barcode:
        return jsonify({'success': False, 'message': 'Barcode tidak valid!'})
    
    # Cek apakah barcode milik guru atau siswa
    teacher = Teacher.query.filter_by(barcode=barcode).first()
    student = Student.query.filter_by(barcode=barcode).first()
    
    if not teacher and not student:
        return jsonify({'success': False, 'message': 'Barcode tidak ditemukan!'})
    
    # Dapatkan nama orang yang absen
    person_name = teacher.name if teacher else student.name
    person_type = 'Guru' if teacher else 'Siswa'
    
    # Dapatkan pengaturan absensi
    setting = Setting.query.first()
    if not setting:
        setting = Setting()
        db.session.add(setting)
        db.session.commit()
    
    current_time = datetime.now().time()
    current_datetime = datetime.now()
    
    # Cek apakah waktu absensi masuk atau pulang
    is_late = current_time > setting.late_time if setting.late_time else False
    is_on_time = current_time <= setting.attendance_end_time if setting.attendance_end_time else True
    
    # Tentukan tipe absensi (masuk atau pulang)
    # Cek apakah sudah absen masuk hari ini
    today_start = datetime.combine(date.today(), time.min)
    today_end = datetime.combine(date.today(), time.max)
    
    existing_attendance = Attendance.query.filter(
        Attendance.barcode == barcode,
        Attendance.timestamp.between(today_start, today_end),
        Attendance.attendance_type == 'in'
    ).first()
    
    attendance_type = 'in'
    status = 'on_time'
    
    # Jika sudah absen masuk, maka ini adalah absen pulang
    if existing_attendance:
        attendance_type = 'out'
        if current_time > setting.attendance_end_time:
            status = 'late'  # Pulang terlambat
        else:
            status = 'on_time'
    else:
        # Ini adalah absen masuk
        if is_late:
            status = 'late'  # Masuk terlambat
        else:
            status = 'on_time'
        
        # Jika setting must_present_for_leave aktif, cek apakah ini absen masuk
        if setting.must_present_for_leave and attendance_type == 'out':
            return jsonify({
                'success': False, 
                'message': 'Anda harus absen masuk terlebih dahulu sebelum bisa absen pulang!'
            })
    
    # Buat record absensi
    attendance = Attendance(
        barcode=barcode,
        attendance_type=attendance_type,
        timestamp=current_datetime,
        location=location,
        status=status
    )
    
    db.session.add(attendance)
    db.session.commit()
    
    # Tentukan pesan berdasarkan status
    if status == 'on_time':
        message = f'{person_type} {person_name} - Anda Tepat Waktu'
    else:
        message = f'{person_type} {person_name} - Anda Tidak Tepat Waktu'
    
    # Tambahkan info tambahan
    time_info = current_datetime.strftime('%H:%M:%S')
    date_info = current_datetime.strftime('%Y-%m-%d')
    
    return jsonify({
        'success': True,
        'message': message,
        'person_name': person_name,
        'person_type': person_type,
        'attendance_type': 'Masuk' if attendance_type == 'in' else 'Pulang',
        'status': 'Tepat Waktu' if status == 'on_time' else 'Tidak Tepat Waktu',
        'time': time_info,
        'date': date_info,
        'location': location
    })

@attendance_bp.route('/manual-scan')
@login_required
def manual_scan():
    return render_template('attendance/manual_scan.html')

@attendance_bp.route('/api/scan', methods=['POST'])
def api_scan():
    data = request.get_json()
    barcode = data.get('barcode')
    location = data.get('location', 'Unknown')
    
    if not barcode:
        return jsonify({'success': False, 'message': 'Barcode tidak valid!'})
    
    # Cek apakah barcode milik guru atau siswa
    teacher = Teacher.query.filter_by(barcode=barcode).first()
    student = Student.query.filter_by(barcode=barcode).first()
    
    if not teacher and not student:
        return jsonify({'success': False, 'message': 'Barcode tidak ditemukan!'})
    
    # Dapatkan nama orang yang absen
    person_name = teacher.name if teacher else student.name
    person_type = 'Guru' if teacher else 'Siswa'
    
    # Dapatkan pengaturan absensi
    setting = Setting.query.first()
    if not setting:
        setting = Setting()
        db.session.add(setting)
        db.session.commit()
    
    current_time = datetime.now().time()
    current_datetime = datetime.now()
    
    # Cek apakah waktu absensi masuk atau pulang
    is_late = current_time > setting.late_time if setting.late_time else False
    is_on_time = current_time <= setting.attendance_end_time if setting.attendance_end_time else True
    
    # Tentukan tipe absensi (masuk atau pulang)
    # Cek apakah sudah absen masuk hari ini
    today_start = datetime.combine(date.today(), time.min)
    today_end = datetime.combine(date.today(), time.max)
    
    existing_attendance = Attendance.query.filter(
        Attendance.barcode == barcode,
        Attendance.timestamp.between(today_start, today_end),
        Attendance.attendance_type == 'in'
    ).first()
    
    attendance_type = 'in'
    status = 'on_time'
    
    # Jika sudah absen masuk, maka ini adalah absen pulang
    if existing_attendance:
        attendance_type = 'out'
        if current_time > setting.attendance_end_time:
            status = 'late'  # Pulang terlambat
        else:
            status = 'on_time'
    else:
        # Ini adalah absen masuk
        if is_late:
            status = 'late'  # Masuk terlambat
        else:
            status = 'on_time'
        
        # Jika setting must_present_for_leave aktif, cek apakah ini absen masuk
        if setting.must_present_for_leave and attendance_type == 'out':
            return jsonify({
                'success': False, 
                'message': 'Anda harus absen masuk terlebih dahulu sebelum bisa absen pulang!'
            })
    
    # Buat record absensi
    attendance = Attendance(
        barcode=barcode,
        attendance_type=attendance_type,
        timestamp=current_datetime,
        location=location,
        status=status
    )
    
    db.session.add(attendance)
    db.session.commit()
    
    # Tentukan pesan berdasarkan status
    if status == 'on_time':
        message = f'{person_type} {person_name} - Anda Tepat Waktu'
    else:
        message = f'{person_type} {person_name} - Anda Tidak Tepat Waktu'
    
    return jsonify({
        'success': True,
        'message': message,
        'person_name': person_name,
        'person_type': person_type,
        'attendance_type': 'Masuk' if attendance_type == 'in' else 'Pulang',
        'status': 'Tepat Waktu' if status == 'on_time' else 'Tidak Tepat Waktu',
        'time': current_datetime.strftime('%H:%M:%S'),
        'date': current_datetime.strftime('%Y-%m-%d'),
        'location': location
    })