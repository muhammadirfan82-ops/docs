from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import db
from app.models.user import User
from app.models.teacher import Teacher
from app.models.student import Student
from app.models.setting import Setting
from app.forms.auth import UserForm
from app.forms.teacher import TeacherForm
from app.forms.student import StudentForm
from app.forms.setting import SettingForm
import qrcode
from PIL import Image
import os

admin_bp = Blueprint('admin', __name__)

def check_admin_permission():
    """Memeriksa apakah user memiliki akses admin"""
    return current_user.role in ['super_admin', 'admin']

@admin_bp.route('/')
@login_required
def dashboard():
    # Hitung jumlah data
    total_users = User.query.count()
    total_teachers = Teacher.query.count()
    total_students = Student.query.count()
    total_settings = Setting.query.count()
    
    return render_template('admin/dashboard.html', 
                         total_users=total_users,
                         total_teachers=total_teachers,
                         total_students=total_students,
                         total_settings=total_settings)

@admin_bp.route('/users')
@login_required
def users():
    if not check_admin_permission():
        flash('Anda tidak memiliki akses ke halaman ini!', 'error')
        return redirect(url_for('admin.dashboard'))
    
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
def create_user():
    if not check_admin_permission():
        flash('Anda tidak memiliki akses ke halaman ini!', 'error')
        return redirect(url_for('admin.dashboard'))
    
    form = UserForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User berhasil dibuat!', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/user_form.html', form=form, title='Tambah User')

@admin_bp.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    if not check_admin_permission():
        flash('Anda tidak memiliki akses ke halaman ini!', 'error')
        return redirect(url_for('admin.dashboard'))
    
    user = User.query.get_or_404(id)
    form = UserForm(obj=user)
    form.password.validators = []  # Tidak wajib saat edit
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role = form.role.data
        
        if form.password.data:  # Jika password diisi
            user.set_password(form.password.data)
            
        db.session.commit()
        flash('User berhasil diupdate!', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/user_form.html', form=form, title='Edit User', user=user)

@admin_bp.route('/users/delete/<int:id>')
@login_required
def delete_user(id):
    if not check_admin_permission():
        flash('Anda tidak memiliki akses ke halaman ini!', 'error')
        return redirect(url_for('admin.dashboard'))
    
    user = User.query.get_or_404(id)
    if user.role == 'super_admin':
        flash('Tidak dapat menghapus Super Admin!', 'error')
        return redirect(url_for('admin.users'))
    
    db.session.delete(user)
    db.session.commit()
    flash('User berhasil dihapus!', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/teachers')
@login_required
def teachers():
    teachers = Teacher.query.all()
    return render_template('admin/teachers.html', teachers=teachers)

@admin_bp.route('/teachers/create', methods=['GET', 'POST'])
@login_required
def create_teacher():
    form = TeacherForm()
    if form.validate_on_submit():
        # Generate barcode
        import uuid
        barcode = str(uuid.uuid4().hex)[:12]  # Generate unique barcode
        
        teacher = Teacher(
            nip=form.nip.data,
            name=form.name.data,
            phone=form.phone.data,
            email=form.email.data,
            address=form.address.data,
            barcode=barcode
        )
        db.session.add(teacher)
        db.session.commit()
        flash('Guru berhasil ditambahkan!', 'success')
        return redirect(url_for('admin.teachers'))
    
    return render_template('admin/teacher_form.html', form=form, title='Tambah Guru')

@admin_bp.route('/teachers/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_teacher(id):
    teacher = Teacher.query.get_or_404(id)
    form = TeacherForm(obj=teacher)
    
    if form.validate_on_submit():
        teacher.nip = form.nip.data
        teacher.name = form.name.data
        teacher.phone = form.phone.data
        teacher.email = form.email.data
        teacher.address = form.address.data
        db.session.commit()
        flash('Data guru berhasil diupdate!', 'success')
        return redirect(url_for('admin.teachers'))
    
    return render_template('admin/teacher_form.html', form=form, title='Edit Guru', teacher=teacher)

@admin_bp.route('/teachers/delete/<int:id>')
@login_required
def delete_teacher(id):
    teacher = Teacher.query.get_or_404(id)
    db.session.delete(teacher)
    db.session.commit()
    flash('Guru berhasil dihapus!', 'success')
    return redirect(url_for('admin.teachers'))

@admin_bp.route('/students')
@login_required
def students():
    students = Student.query.all()
    return render_template('admin/students.html', students=students)

@admin_bp.route('/students/create', methods=['GET', 'POST'])
@login_required
def create_student():
    form = StudentForm()
    if form.validate_on_submit():
        # Generate barcode
        import uuid
        barcode = str(uuid.uuid4().hex)[:12]  # Generate unique barcode
        
        student = Student(
            nis=form.nis.data,
            name=form.name.data,
            class_name=form.class_name.data,
            phone=form.phone.data,
            email=form.email.data,
            address=form.address.data,
            barcode=barcode
        )
        db.session.add(student)
        db.session.commit()
        flash('Siswa berhasil ditambahkan!', 'success')
        return redirect(url_for('admin.students'))
    
    return render_template('admin/student_form.html', form=form, title='Tambah Siswa')

@admin_bp.route('/students/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_student(id):
    student = Student.query.get_or_404(id)
    form = StudentForm(obj=student)
    
    if form.validate_on_submit():
        student.nis = form.nis.data
        student.name = form.name.data
        student.class_name = form.class_name.data
        student.phone = form.phone.data
        student.email = form.email.data
        student.address = form.address.data
        db.session.commit()
        flash('Data siswa berhasil diupdate!', 'success')
        return redirect(url_for('admin.students'))
    
    return render_template('admin/student_form.html', form=form, title='Edit Siswa', student=student)

@admin_bp.route('/students/delete/<int:id>')
@login_required
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash('Siswa berhasil dihapus!', 'success')
    return redirect(url_for('admin.students'))

@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if not check_admin_permission():
        flash('Anda tidak memiliki akses ke halaman ini!', 'error')
        return redirect(url_for('admin.dashboard'))
    
    setting = Setting.query.first()
    if not setting:
        setting = Setting()
        db.session.add(setting)
        db.session.commit()
    
    form = SettingForm(obj=setting)
    if form.validate_on_submit():
        setting.attendance_start_time = form.attendance_start_time.data
        setting.attendance_end_time = form.attendance_end_time.data
        setting.late_time = form.late_time.data
        setting.must_present_for_leave = form.must_present_for_leave.data
        db.session.commit()
        flash('Pengaturan berhasil disimpan!', 'success')
        return redirect(url_for('admin.settings'))
    
    return render_template('admin/settings.html', form=form, setting=setting)

@admin_bp.route('/generate-barcode/<string:barcode_type>/<int:id>')
@login_required
def generate_barcode(barcode_type, id):
    if barcode_type == 'teacher':
        person = Teacher.query.get_or_404(id)
        barcode_data = person.barcode
        name = person.name
    elif barcode_type == 'student':
        person = Student.query.get_or_404(id)
        barcode_data = person.barcode
        name = person.name
    else:
        flash('Tipe barcode tidak valid!', 'error')
        return redirect(url_for('admin.dashboard'))
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(barcode_data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save image
    filename = f"{barcode_type}_{id}.png"
    filepath = os.path.join('app/static/images/barcodes', filename)
    
    # Create directory if not exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    img.save(filepath)
    
    flash(f'Barcode untuk {name} berhasil dibuat!', 'success')
    if barcode_type == 'teacher':
        return redirect(url_for('admin.teachers'))
    else:
        return redirect(url_for('admin.students'))