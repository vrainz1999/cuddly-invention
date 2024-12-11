from flask import Flask, render_template, redirect, url_for, session, request, flash, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import InputRequired
from flask_bootstrap import Bootstrap 
from functools import wraps
from flask_migrate import Migrate
import datetime
from sqlalchemy import or_
import pdfkit
from datetime import date
from decimal import Decimal
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

app = Flask(__name__)

app.config['SECRET_KEY'] = '$#FHenfge24'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/dbklinik'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
bootstrap = Bootstrap(app)

class Login(FlaskForm):
    username = StringField('', validators=[InputRequired()], render_kw={'autofocus': True, 'placeholder': 'Username'})
    password = PasswordField('', validators=[InputRequired()], render_kw={'autofocus': True, 'placeholder': 'Password'})
    level = SelectField('', validators=[InputRequired()], choices=[('Admin', 'Admin'), ('Dokter', 'Dokter'), ('Administrasi', 'Administrasi'), ('Apoteker', 'Apoteker'), ('Kasir', 'Kasir')])

class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150))
    password = db.Column(db.Text)
    level = db.Column(db.String(100))

    pasiens = db.relationship('Pasien', back_populates='user') 

    def __init__(self, username, password, level):
        self.username = username
        if password != '':
            self.password = bcrypt.generate_password_hash(password).decode('UTF-8')
        self.level = level

         

class Dokter(db.Model):
    __tablename__ = 'dokter'
    id = db.Column(db.Integer, primary_key=True)
    id_pegawai = db.Column(db.String(10), db.ForeignKey('pegawai.id_pegawai'))
    jadwal = db.Column(db.String(100))
    tarif_medis = db.Column(db.Numeric(10, 2))

    
    pegawai = db.relationship('Pegawai', back_populates='dokter')
    pembayaran = db.relationship('Pembayaran', back_populates='jasa_dokter_ref')

class Pegawai(db.Model):
    __tablename__ = 'pegawai'
    
    id_pegawai = db.Column(db.String(10), primary_key=True)  
    nama = db.Column(db.String(150), nullable=False)  
    alamat = db.Column(db.Text, nullable=True)  
    no_hp = db.Column(db.String(15), nullable=True)  
    jabatan = db.Column(db.String(100), nullable=True) 
    spesialisasi = db.Column(db.String(100)) 
    
    detailobat = db.relationship('DetailObat', back_populates='pegawai')
    dokter = db.relationship('Dokter', back_populates='pegawai', uselist=False)
    pendaftaran = db.relationship('Pendaftaran', back_populates='pegawai')


    def __init__(self, id_pegawai, nama, alamat, no_hp, jabatan, spesialisasi):
        self.id_pegawai = id_pegawai 
        self.nama = nama
        self.alamat = alamat
        self.no_hp = no_hp
        self.jabatan = jabatan
        self.spesialisasi = spesialisasi


class Suplier(db.Model):
    __tablename__ = 'suplier'
    
    id = db.Column(db.Integer, primary_key=True)
    perusahaan = db.Column(db.String(200))
    kontak = db.Column(db.String(100))
    alamat = db.Column(db.Text)
    supliernya = db.relationship('Obat', backref=db.backref('suplier', lazy=True))

    def __init__(self, perusahaan, kontak, alamat):
        self.perusahaan = perusahaan
        self.kontak = kontak
        self.alamat = alamat

class Pendaftaran(db.Model):
    __tablename__ = 'pendaftaran'
    
    id_daftar = db.Column(db.String(10), primary_key=True)
    nama = db.Column(db.String(150))
    tl = db.Column(db.String(100))
    tg_lahir = db.Column(db.String(100))
    jk = db.Column(db.String(100))
    status = db.Column(db.String(100))
    profesi = db.Column(db.String(100))
    alamat = db.Column(db.Text)
    keterangan = db.Column(db.String(50))

   
    id_pegawai = db.Column(db.String(10), db.ForeignKey('pegawai.id_pegawai'))
    

    pegawai = db.relationship('Pegawai', back_populates='pendaftaran')
    pasien = db.relationship('Pasien', back_populates='pendaftaran')
    pembayaran = db.relationship('Pembayaran', back_populates='pendaftaran')
    detail_obats = db.relationship('DetailObat', back_populates="pendaftaran")
    biaya_obats = db.relationship('BiayaObat', back_populates="pendaftaran")


    def __init__(self, id_daftar, nama, tl, tg_lahir, jk, status, profesi, alamat, id_pegawai, keterangan):
        self.id_daftar = id_daftar
        self.nama = nama
        self.tl = tl
        self.tg_lahir = tg_lahir
        self.jk = jk
        self.status = status
        self.profesi = profesi
        self.alamat = alamat
        self.id_pegawai = id_pegawai
        self.keterangan = keterangan

class Pasien(db.Model):
    __tablename__ = 'pasien'
    
    id = db.Column(db.BigInteger, primary_key=True)
    nama = db.Column(db.String(150))
    keluhan = db.Column(db.Text)
    diagnosa = db.Column(db.String(100))
    resep = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    pendaftaran_id = db.Column(db.String(10), db.ForeignKey('pendaftaran.id_daftar'))
    tanggal = db.Column(db.String(100))

    
    pendaftaran = db.relationship('Pendaftaran', back_populates='pasien')
    user = db.relationship('User', back_populates='pasiens')  

    def __init__(self, nama, keluhan, diagnosa, resep, user_id, pendaftaran_id, tanggal):
        self.nama = nama
        self.keluhan = keluhan
        self.diagnosa = diagnosa
        self.resep = resep
        self.user_id = user_id
        self.pendaftaran_id = pendaftaran_id
        self.tanggal = tanggal
 

class BiayaPendaftaran(db.Model):
    __tablename__ = 'biayapendaftaran'
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    biaya = db.Column(db.Float, nullable=False)  

    def __init__(self, nama, biaya):
        self.nama = nama
        self.biaya = biaya

class BiayaAdministrasi(db.Model):
    __tablename__ = 'biayaadministrasi'
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    biaya = db.Column(db.Float, nullable=False)  

    pembayaran = db.relationship('Pembayaran', back_populates='biaya_admin_ref')

    def __init__(self, nama, biaya):
        self.nama = nama
        self.biaya = biaya

class Pembayaran(db.Model):
    __tablename__ = 'pembayaran'

    id_bmedis = db.Column(db.String(10), primary_key=True)
    id_daftar = db.Column(db.String(10), db.ForeignKey('pendaftaran.id_daftar'))
    tanggal_bayar = db.Column(db.Date, nullable=False)
    admin_id= db.Column(db.Integer, db.ForeignKey('biayaadministrasi.id'))   
    dokter_id = db.Column(db.Integer, db.ForeignKey('dokter.id'))
    total_bayar = db.Column(db.Numeric(10, 2), nullable=False, default=0)

    
    pendaftaran = db.relationship('Pendaftaran', back_populates='pembayaran')

    
    biaya_admin_ref = db.relationship('BiayaAdministrasi', back_populates='pembayaran')
    jasa_dokter_ref = db.relationship('Dokter', back_populates='pembayaran')

    def __init__(self, id_bmedis, id_daftar, tanggal_bayar, admin_id, dokter_id, total_bayar=0):
        self.id_bmedis = id_bmedis
        self.id_daftar = id_daftar
        self.tanggal_bayar = tanggal_bayar
        self.admin_id = admin_id
        self.dokter_id = dokter_id
        self.total_bayar = total_bayar



class Obat(db.Model):
    __tablename__ = 'obat'
    
    id = db.Column(db.Integer, primary_key=True)
    namaObat = db.Column(db.String(150))
    jenisObat = db.Column(db.String(150))
    harga_beli = db.Column(db.Integer)
    harga_jual = db.Column(db.Integer)
    kondisi = db.Column(db.String(80))
    suplier_id = db.Column(db.Integer, db.ForeignKey('suplier.id'))

    detailobat = db.relationship('DetailObat', back_populates='obat')

    def __init__(self, namaObat, jenisObat, harga_beli, harga_jual, kondisi, suplier_id):
        self.namaObat = namaObat
        self.jenisObat = jenisObat
        self.harga_beli = harga_beli
        self.harga_jual = harga_jual
        self.kondisi = kondisi
        self.suplier_id = suplier_id


class DetailObat(db.Model):
    __tablename__ = 'detailobat'
    id_dobt = db.Column(db.String(10), primary_key=True)
    daftar_id = db.Column(db.String(10), db.ForeignKey('pendaftaran.id_daftar'))
    id_obat = db.Column(db.Integer, db.ForeignKey('obat.id'))
    qty = db.Column(db.Integer, nullable=False)
    harga = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False, default=0.0)
    tanggal_resep = db.Column(db.Date, nullable=False)
    pegawai_id = db.Column(db.String(10), db.ForeignKey('pegawai.id_pegawai')) 

    pendaftaran = db.relationship('Pendaftaran', back_populates="detail_obats")
    obat = db.relationship('Obat', backref='detail_obat')
    pegawai = db.relationship('Pegawai', backref='detail_obat')

    def __init__(self, id_dobt, daftar_id, id_obat, qty, harga, total, tanggal_resep, pegawai_id):
        self.id_dobt = id_dobt
        self.daftar_id = daftar_id
        self.id_obat = id_obat
        self.qty = qty
        self.harga = harga
        self.total = total
        self.tanggal_resep = tanggal_resep
        self.pegawai_id = pegawai_id

class BiayaObat(db.Model):
    __tablename__ = 'biaya_obat'

    id_bobt = db.Column(db.String(10), primary_key=True)
    daftar_id = db.Column(db.String(10), db.ForeignKey('pendaftaran.id_daftar'))
    total_bayar = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    metode_bayar = db.Column(db.String(20), nullable=False)

    pendaftaran = db.relationship('Pendaftaran', back_populates="biaya_obats")
    
    def __init__(self, id_bobt, daftar_id, total_bayar, metode_bayar):
        self.id_dobt = id_bobt
        self.daftar_id = daftar_id
        self.total_bayar = total_bayar
        self.metode_bayar = metode_bayar

with app.app_context():
    db.create_all()


def login_dulu(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'login' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrap

@app.route('/')
def index():
    if session.get('login') == True :
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('login') == True :
        return redirect(url_for('dashboard')) 
    form = Login()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data) and user.level == form.level.data:
                session['login'] = True
                session['id'] = user.id
                session['level'] = user.level
                return redirect(url_for('dashboard'))
        pesan = "Username atau Password anda salah"
        return render_template("login.html", pesan=pesan, form=form)
    return render_template('login.html', form=form)

@app.route('/dashboard')
@login_dulu
def dashboard():
    data1 = db.session.query(Dokter).count()
    data2 = db.session.query(Pendaftaran).count()
    data3 = db.session.query(User).count()
    data4 = db.session.query(func.sum(Obat.harga_jual)).filter(Obat.kondisi == "Rusak").scalar()
    data5 = db.session.query(func.sum(Obat.harga_jual)).filter(Obat.kondisi == "Baik").scalar()
    return render_template('dashboard.html', data1=data1, data2=data2, data3=data3, data4=data4, data5=data5 )

@app.route('/kelola_user')
@login_dulu
def kelola_user():
    data = User.query.all()
    return render_template('user.html', data=data)

@app.route("/tambahuser", methods=["GET","POST"])
@login_dulu
def tambahuser():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        level = request.form["level"]
        db.session.add(User(username,password,level))
        db.session.commit()
        return redirect(url_for("kelola_user"))

@app.route('/edituser/<id>', methods=['GET','POST'])    
@login_dulu
def edituser(id):
    data = User.query.filter_by(id=id).first()
    if request.method == "POST":
        try:
            data.username = request.form["username"]
            new_password = request.form["password"]
            if new_password != "":
                data.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            data.level = request.form["level"]
            db.session.commit()
            return redirect(url_for("kelola_user"))    
        except:
            flash("Ada trouble")
            return redirect(request.referrer)
    return render_template('edituser.html', data=data)
        
@app.route('/hapususer/<id>', methods=['GET', 'POST'])
@login_dulu
def hapususer(id):
    data = User.query.filter_by(id=id).first()
    db.session.delete(data)
    db.session.commit()
    return redirect(url_for("kelola_user")) 

@app.route('/pendaftaran')
@login_dulu
def pendaftaran():
    pegawai_data = Pegawai.query.all()
    pendaftaran_data = Pendaftaran.query.all()
    return render_template('pendaftaran.html', pegawai_data=pegawai_data, pendaftaran_data=pendaftaran_data)  

@app.route('/tambahdaftar', methods=["POST"])
@login_dulu
def tambahdaftar():
    try:
        
        id_daftar = request.form.get('id_daftar')
        nama = request.form.get('nama')
        tl = request.form.get('tl')
        tg_lahir = request.form.get('tg_lahir')
        jk = request.form.get('jk')
        status = request.form.get('status')
        profesi = request.form.get('profesi')
        alamat = request.form.get('alamat')
        keterangan = request.form.get('keterangan')
        id_pegawai = request.form.get('pegawai_id')

        print(f'Keterangan: {keterangan}') 
        
        
        
        db.session.add(Pendaftaran(id_daftar=id_daftar, nama=nama, tl=tl, tg_lahir=tg_lahir, jk=jk, status=status, profesi=profesi, alamat=alamat, keterangan=keterangan, id_pegawai=id_pegawai))
        db.session.commit()
        
        flash('Dokter berhasil ditambah!', 'success')
        return redirect(url_for('pendaftaran'))
    except Exception as e:
        db.session.rollback()  
        print(e)  
        flash('Terjadi kesalahan saat menambah dokter.', 'danger')
        return redirect(url_for('pendaftaran'))
           
@app.route('/editdaftar/<string:id_daftar>', methods=['GET', 'POST'])
@login_dulu
def editdaftar(id_daftar):
    patient = Pendaftaran.query.filter_by(id_daftar=id_daftar).first()
    if request.method == 'POST':
        print(request.form)
        try:
            patient.nama = request.form.get('nama')
            patient.tl = request.form.get('tl')
            patient.tg_lahir = request.form.get('tg_lahir')
            patient.jk = request.form.get('jk')
            patient.status = request.form.get('status')
            patient.profesi = request.form.get('profesi')
            patient.alamat = request.form.get('alamat')
            patient.keterangan = request.form.get('keterangan', 'Diproses')  
            patient.id_pegawai = request.form.get('pegawai_id')

           
            db.session.commit()
            return redirect(url_for('pendaftaran'))  
        except KeyError as e:
            print(f"Missing form field: {e}")
            return "Bad Request: Missing form field", 400
    return render_template('pendaftaran.html', patient=patient)
  

@app.route('/hapusdaftar/<id>', methods=['POST'])
@login_dulu
def hapusdaftar(id):
    try:
        data = Pendaftaran.query.filter_by(id=id).first()
        if data:
            db.session.delete(data)
            db.session.commit()
            return redirect(request.referrer)
        else:
            flash('Record not found', 'danger')
            return redirect(request.referrer)
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting record: {e}", 'danger')
        return redirect(request.referrer)

@app.route('/apotik')
@login_dulu
def apotik():
    data = Obat.query.all()
    data1 = Suplier.query.all()
    return render_template('apotik.html', data=data, data1=data1)

@app.route('/tambahobat', methods=['GET', 'POST'])
@login_dulu
def tambahobat():
    try:
        namaObat = request.form.get('namaObat')
        jenisObat = request.form.get('jenisObat')
        harga_beli = request.form.get('harga_beli')
        harga_jual = request.form.get('harga_jual')
        kondisi = request.form.get('kondisi')
        suplier_id = request.form.get('suplier_id')
        
        db.session.add(Obat(namaObat, jenisObat, harga_beli, harga_jual, kondisi, suplier_id))
        db.session.commit()
        
        flash('Obat berhasil ditambah!', 'success')
        return redirect(url_for('apotik'))
    except Exception as e:
        print(e)
        flash('Terjadi kesalahan saat tambah obat.', 'danger')
        return redirect(url_for('apotik'))

    
@app.route('/editobat/<int:id>', methods=['POST'])
@login_dulu
def editobat(id):
    try:
        
        data = Obat.query.get(id)
        if data:
            
            data.namaObat = request.form['namaObat']
            data.jenisObat = request.form['jenisObat']
            data.harga_beli = request.form['harga_beli']
            data.harga_jual= request.form['harga_jual']
            data.kondisi = request.form['kondisi']
            data.suplier_id = request.form['suplier_id']

        db.session.commit()
        flash('Obat berhasil diperbarui!', 'success')
        return redirect(url_for('apotik'))
    except Exception as e:
        print(e)
        flash('Terjadi kesalahan saat memperbarui obat.', 'danger')
        return redirect(url_for('apotik'))

@app.route('/hapusobat/<int:id>', methods=['GET', 'POST'])
@login_dulu
def hapusobat(id):
    data = Obat.query.filter_by(id=id).first()
    db.session.delete(data)
    db.session.commit()
    return redirect(request.referrer) 

@app.route('/pegawai')
@login_dulu
def pegawai():
    data = Pegawai.query.all()
    return render_template('pegawai.html', data=data)

@app.route('/tambahpegawai', methods=['GET', 'POST']) 
@login_dulu
def tambahpegawai():
    if request.method == 'POST':
        try:
            id_pegawai = request.form['id_pegawai']
            nama = request.form['nama']
            alamat = request.form['alamat']
            no_hp = request.form['no_hp']
            jabatan = request.form['jabatan']
            spesialisasi = request.form['spesialisasi']
            
            
            db.session.add(Pegawai(id_pegawai, nama, alamat, no_hp, jabatan, spesialisasi))
            db.session.commit()

            flash('Pegawai berhasil ditambah!', 'success')
            
           
            return redirect(url_for('pegawai'))

        except Exception as e:
            print(e)
            flash('Terjadi kesalahan saat tambah pegawai.', 'danger')
            return redirect(url_for('pegawai'))

    return render_template('tambahpegawai.html')

@app.route('/editpegawai/<id_pegawai>', methods=['GET', 'POST'])  
@login_dulu
def editpegawai(id_pegawai):
    data = Pegawai.query.filter_by(id_pegawai=id_pegawai).first()
    if request.method == 'POST':
        
        print(request.form)
        
        try:
            
            data.id_pegawai = request.form['id_pegawai']
            data.nama = request.form['nama']
            data.alamat = request.form['alamat']
            data.no_hp = request.form['no_hp']
            data.jabatan = request.form['jabatan']
            data.spesialisasi = request.form['spesialisasi']
            
            
            db.session.commit()
            return redirect(url_for('pegawai'))  
        except KeyError as e:
            print(f"Missing form field: {e}")
            return "Bad Request: Missing form field", 400
    return render_template('editpegawai.html', data=data)

@app.route('/hapuspegawai/<string:id_pegawai>', methods=['POST'])  
@login_dulu
def hapuspegawai(id_pegawai):
    data = Pegawai.query.filter_by(id_pegawai=id_pegawai).first()
    if data:
        db.session.delete(data)
        db.session.commit()
    return redirect(request.referrer)       

@app.route('/dokter')
@login_dulu
def dokter():
    pegawai_data = Pegawai.query.all()
    dokter_data = Dokter.query.all()
    return render_template('dokter.html', pegawai_data=pegawai_data, dokter_data=dokter_data)

@app.route('/tambahdokter', methods=['POST'])
@login_dulu
def tambahdokter():
    try:
        pegawai_id = request.form['pegawai_id']
        jadwal = request.form['jadwal']
        tarif_medis = request.form['tarif_medis']

        db.session.add(Dokter(id_pegawai=pegawai_id, jadwal=jadwal, tarif_medis=tarif_medis))
        db.session.commit()

        flash('Dokter berhasil ditambah!', 'success')
        return redirect(url_for('dokter'))
    except Exception as e:
        print(e)
        flash('Terjadi kesalahan saat menambah dokter.', 'danger')
        return redirect(url_for('dokter'))

@app.route('/editdokter/<int:id>', methods=['GET', 'POST'])
def edit_dokter(id):
    dokter = Dokter.query.get(id)
    if not dokter:
        flash('Dokter tidak ditemukan!', 'danger')
        return redirect(url_for('dokter'))

    if request.method == 'POST':
        dokter.id_pegawai = request.form['pegawai_id']
        dokter.jadwal = request.form['jadwal']
        dokter.tarif_medis = request.form['tarif_medis']

        db.session.commit()
        flash('Data dokter berhasil diperbarui!', 'success')
        return redirect(url_for('dokter'))

    return render_template('edit_dokter.html', dokter=dokter)

@app.route('/hapusdokter/<int:id>', methods=['POST'])
@login_dulu
def hapus_dokter(id):
    try:
        # Ambil `id_pegawai` dari data yang dikirim melalui form
        id_pegawai = request.form.get('id_pegawai')
        if not id_pegawai:
            raise ValueError("Missing id_pegawai")

        # Ambil record berdasarkan primary key komposit
        dokter = db.session.get(Dokter, (id, id_pegawai))
        if dokter:
            db.session.delete(dokter)
            db.session.commit()
            return redirect('/dokter')
        else:
            return "Doctor not found", 404
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting doctor: {e}")
        return "Error deleting doctor", 500

        

@app.route('/pendaftaran')
def view_pendaftaran():
    pendaftaran_list = Pendaftaran.query.all()
    print(pendaftaran_list)
    return render_template('pendaftaranhtml', pendaftaran_list=pendaftaran_list)


@app.route('/tambahpendaftaran', methods=['GET', 'POST'])
def tambahpendaftaran():
    if request.method == 'POST':
       
        id_daftar = request.form['id_daftar']
        nama = request.form['nama']
        tl = request.form['tl']
        tg_lahir = request.form['tg_lahir']
        jk = request.form['jk']
        status = request.form['status']
        profesi = request.form['profesi']
        alamat = request.form['alamat']
        id_pegawai = request.form['id_pegawai']
        keterangan = request.form.get('keterangan', 'Diproses')
        
        
        new_pendaftaran = Pendaftaran(id_daftar=id_daftar,
            nama=nama, tl=tl, tg_lahir=tg_lahir, jk=jk, 
            status=status, profesi=profesi, alamat=alamat, 
            id_pegawai=id_pegawai, keterangan=keterangan
        )
        
        
        db.session.add(new_pendaftaran)
        db.session.commit()
        
        flash("Pendaftaran record added successfully", "success")
        return redirect(url_for('pendaftaran'))
    

    pegawai_list = Pegawai.query.all()
    return render_template('pendaftaran.html', pegawai_list=pegawai_list)


@app.route('/pendaftaran/edit/<int:id>', methods=['GET', 'POST'])
def edit_pendaftaran(id):
    pendaftaran = Pendaftaran.query.get_or_404(id)
    
    if request.method == 'POST':
        pendaftaran.nama = request.form['nama']
        pendaftaran.tl = request.form['tl']
        pendaftaran.tg_lahir = request.form['tg_lahir']
        pendaftaran.jk = request.form['jk']
        pendaftaran.status = request.form['status']
        pendaftaran.profesi = request.form['profesi']
        pendaftaran.alamat = request.form['alamat']
        pendaftaran.id_pegawai = request.form['id_pegawai']
        pendaftaran.keterangan = request.form['keterangan']
        
        
        db.session.commit()
        
        flash("Pendaftaran record updated successfully", "success")
        return redirect(url_for('view_pendaftaran'))
    
    
    pegawai_list = Pegawai.query.all()
    return render_template('edit_pendaftaran.html', pendaftaran=pendaftaran, pegawai_list=pegawai_list)


@app.route('/pendaftaran/delete/<int:id>', methods=['POST'])
def delete_pendaftaran(id):
    pendaftaran = Pendaftaran.query.get_or_404(id)
    db.session.delete(pendaftaran)
    db.session.commit()
    flash("Pendaftaran record deleted successfully", "success")
    return redirect(url_for('view_pendaftaran'))        

@app.route('/suplier')
@login_dulu
def suplier():
    data = Suplier.query.all()
    return render_template('suplier.html', data=data)

@app.route('/tambahsuplier', methods=['GET', 'POST'])
@login_dulu
def tambahsuplier():
    try:
        perusahaan = request.form.get('perusahaan')
        kontak = request.form.get('kontak')
        alamat = request.form.get('alamat')
        db.session.add(Suplier(perusahaan, kontak, alamat))
        db.session.commit()
        
        return jsonify({"success": True})
    except Exception as e:
        print(e)  
        return jsonify({"success": False}), 500

@app.route('/editsuplier/<int:id>', methods=['GET', 'POST']) 
@login_dulu
def editsuplier(id):
    try:
       
        data = Suplier.query.get(id)
        if data:
            
            data.perusahaan = request.form['perusahaan']
            data.kontak = request.form['kontak']
            data.alamat = request.form['alamat']         
            db.session.commit()
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Record not found'})
    except Exception as e:
        db.session.rollback()
        print(f"Error editing record: {e}")
        return jsonify({'success': False, 'error': str(e)})
    
@app.route('/hapussuplier/<int:id>', methods=['GET', 'POST'])
@login_dulu
def hapussuplier(id):
    data = Suplier.query.filter_by(id=id).first()
    db.session.delete(data)
    db.session.commit()
    return redirect(request.referrer)     

@app.route('/tangani_pasien')
@login_dulu
def tangani_pasien():
    data = Pendaftaran.query.filter_by(keterangan="Diproses").all()
    return render_template('tangani.html', data=data)

@app.route('/diagnosis/<id_daftar>', methods=['GET', 'POST'])
@login_dulu
def diagnosis(id_daftar):
    data = Pendaftaran.query.filter_by(id_daftar=id_daftar).first()
    
    if not data:
        flash('Pasien tidak ditemukan', 'error')
        return redirect(url_for('tangani_pasien'))

    if request.method == "POST":
        nama = request.form['nama']
        keluhan = request.form['keluhan']
        diagnosa = request.form['diagnosa']
        resep = request.form['resep']
        user_id = request.form['user_id']
        pendaftaran_id = request.form['pendaftaran_id']
        tanggal = datetime.datetime.now().strftime("%d %B %Y Jam %H:%M:%S")
        
        
        data.keterangan = "Selesai"
        db.session.commit()

       
        new_pasien = Pasien(nama=nama, keluhan=keluhan, diagnosa=diagnosa, resep=resep, user_id=user_id, pendaftaran_id=pendaftaran_id, tanggal=tanggal)
        db.session.add(new_pasien)
        db.session.commit()

        return redirect(url_for('tangani_pasien'))
    return render_template('diagnosis.html', data=data)

@app.route('/pencarian')
@login_dulu
def pencarian():
    return render_template('pencarian.html')


@app.route('/cari_data', methods=['GET', 'POST'])
@login_dulu
def cari_data():
    if request.method == "POST":
        keyword = request.form["q"]
        formt = "%{0}%".format(keyword)
        
        # Join Pasien with Pendaftaran and User
        datanya = Pasien.query.join(Pendaftaran).join(User).filter(Pasien.tanggal.like(formt)).all()
        
        return render_template('pencarian.html', datanya=datanya)

#@app.route('/cari_data', methods=['GET', 'POST'])
#@login_dulu
#def cari_data():
#    if request.method  == "POST":
#        keyword = request.form["q"]
#        formt = "%{0}%".format(keyword)
#        datanya = Pasien.query.join(User, Pasien.user_id == User.id).filter(or_(Pasien.tanggal.like(formt))).all()
#        return render_template('pencarian.html', datanya=datanya)
    

@app.route('/cetak_pdf/<keyword>', methods=['GET', 'POST'])
@login_dulu
def cetak_pdf(keyword):
    formt = "%{0}%".format(keyword)
    datanya = Pasien.query.join(User, Pasien.user_id == User.id).filter(or_(Pasien.tanggal.like(formt))).all()
    html = render_template("pdf.html", datanya=datanya)
    config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
    pdf = pdfkit.from_string(html, False, configuration=config)  
    response = make_response(pdf)
    response.headers["Content-Type"] = 'application/pdf'
    response.headers["Content-Disposition"] = 'inline; filename=laporan.pdf'
    return response

@app.route('/biayapendaftaran')
@login_dulu
def biayapendaftaran():
    data = BiayaPendaftaran.query.all()
    return render_template('biayapendaftaran.html', data=data)

@app.route('/tambahbiayapendaftaran', methods=['GET', 'POST'])
@login_dulu
def tambahbiayapendaftaran():
    if request.method == 'POST':
        nama = request.form['nama']
        biaya = request.form['biaya']

        
        biaya_pendaftaran_baru = BiayaPendaftaran(nama=nama, biaya=biaya)

        
        try:
            db.session.add(biaya_pendaftaran_baru)
            db.session.commit()
            flash("Biaya Pendaftaran berhasil ditambahkan!", "success")
            return redirect('/biayapendaftaran')
        except:
            db.session.rollback()
            flash("Gagal menambahkan Biaya Pendaftaran.", "danger")
            return redirect('/tambahbiayapendaftaran')

    
    return render_template('tambahbiayapendaftaran.html')

@app.route('/editbiayapendaftaran/<int:id>', methods=['GET', 'POST'])
@login_dulu
def editbiayapendaftaran(id):
    try:
        
        data = BiayaPendaftaran.query.get(id)
        if data:
            
            data.nama = request.form['nama']
            data.biaya = request.form['biaya']     
            db.session.commit()

        db.session.commit()
        flash('Biaya Pendaftaran berhasil diperbarui!', 'success')
        return redirect(url_for('biayapendaftaran'))
    except Exception as e:
        print(e)
        flash('Terjadi kesalahan saat memperbarui biaya pendaftaran.', 'danger')
        return redirect(url_for('biayapendaftaran'))


@app.route('/hapusbiayapendaftaran/<int:id>', methods=['POST'])
def hapusbiayapendaftaran(id):
    biaya_daftar = BiayaPendaftaran.query.get_or_404(id)

    
    try:
        db.session.delete(biaya_daftar)
        db.session.commit()
        flash("Biaya Pendaftaran berhasil dihapus!", "success")
        return redirect('/biayapendaftaran')
    except:
        db.session.rollback()
        flash("Gagal menghapus Biaya Pendaftaran.", "danger")
        return redirect('/biayapendaftaran')

@app.route('/biayaadministrasi')
@login_dulu
def biayaadministrasi():
    data = BiayaAdministrasi.query.all()
    return render_template('biayaadministrasi.html', data=data)

@app.route('/tambahbiayaadministrasi', methods=['GET', 'POST'])
@login_dulu
def tambahbiayaadministrasi():
    if request.method == 'POST':
        nama = request.form['nama']
        biaya = request.form['biaya']

        
        biaya_admin_baru = BiayaAdministrasi(nama=nama, biaya=biaya)

        
        try:
            db.session.add(biaya_admin_baru)
            db.session.commit()
            flash("Biaya Administrasi berhasil ditambahkan!", "success")
            return redirect('/biayaadministrasi')
        except:
            db.session.rollback()
            flash("Gagal menambahkan Biaya Administrasi.", "danger")
            return redirect('/tambahbiayaadministrasi')

    
    return render_template('tambahbiayaadministrasi.html')

@app.route('/editbiayaadministrasi/<int:id>', methods=['GET', 'POST'])
@login_dulu
def editbiayaadministrasi(id):
    try:
        
        data = BiayaAdministrasi.query.get(id)
        if data:
            
            data.nama = request.form['nama']
            data.biaya = request.form['biaya']     
            db.session.commit()

        db.session.commit()
        flash('Obat berhasil diperbarui!', 'success')
        return redirect(url_for('biayaadministrasi'))
    except Exception as e:
        print(e)
        flash('Terjadi kesalahan saat memperbarui obat.', 'danger')
        return redirect(url_for('biayaadministrasi'))


@app.route('/hapusbiayaadministrasi/<int:id>', methods=['POST'])
def hapusbiayaadministrasi(id):
    biaya_admin = BiayaAdministrasi.query.get_or_404(id)

    
    try:
        db.session.delete(biaya_admin)
        db.session.commit()
        flash("Biaya Administrasi berhasil dihapus!", "success")
        return redirect('/biayaadministrasi')
    except:
        db.session.rollback()
        flash("Gagal menghapus Biaya Administrasi.", "danger")
        return redirect('/biayaadministrasi')


@app.template_filter('decimal')
def decimal_filter(value):
    """Convert a value to Decimal."""
    try:
        return Decimal(value)
    except (ValueError, TypeError):
        return Decimal(0)  


@app.route('/pembayaran')
def pembayaran():
    pembayaran_list = Pembayaran.query.all()
    pasien = Pendaftaran.query.all()
    admin_data = BiayaAdministrasi.query.all()
    dokter_data = Dokter.query.all()

    
    for pembayaran in pembayaran_list:
        
        if pembayaran.biaya_admin_ref and pembayaran.jasa_dokter_ref:
            pembayaran.biaya_admin_ref.biaya = Decimal(pembayaran.biaya_admin_ref.biaya) if pembayaran.biaya_admin_ref.biaya else Decimal(0)
            pembayaran.jasa_dokter_ref.tarif_medis = Decimal(pembayaran.jasa_dokter_ref.tarif_medis) if pembayaran.jasa_dokter_ref.tarif_medis else Decimal(0)
    
    
    return render_template('pembayaran.html', 
                           pembayaran_list=pembayaran_list, 
                           pasien=pasien, 
                           admin_data=admin_data, 
                           dokter_data=dokter_data, 
                           decimal=Decimal)

@app.route('/tambah_pembayaran', methods=['POST'])
@login_dulu
def tambah_pembayaran():
    try:
        admin_id = int(request.form['admin_id'])
        dokter_id = int(request.form['dokter_id'])

        biayaadministrasi = BiayaAdministrasi.query.get(admin_id)
        dokter = Dokter.query.get(dokter_id)

        if not biayaadministrasi or not dokter:
            flash("Biaya Administrasi atau Jasa Dokter tidak ditemukan.", "danger")
            return redirect(url_for('pembayaran'))

        total_bayar = Decimal(biayaadministrasi.biaya) + Decimal(dokter.tarif_medis)

        new_pembayaran = Pembayaran(
            id_bmedis=request.form['id_bmedis'],
            id_daftar=request.form['id_daftar'],
            tanggal_bayar=request.form.get('tanggalPembayaran', date.today()),
            admin_id=admin_id,
            dokter_id=dokter_id,
            total_bayar=total_bayar,
        )
        db.session.add(new_pembayaran)
        db.session.commit()
        flash("Pembayaran berhasil ditambahkan.", "success")
    except Exception as e:
        print(f"Error: {e}")
        flash("Terjadi kesalahan saat menambahkan pembayaran.", "danger")

    return redirect(url_for('pembayaran'))

@app.route('/edit_pembayaran/<string:id_bmedis>', methods=['GET', 'POST'])
@login_dulu
def edit_pembayaran(id_bmedis):
    pembayaran = Pembayaran.query.filter_by(id_bmedis=id_bmedis).first_or_404()

    if request.method == 'POST':
        try:
            # Ambil data dari form
            admin_id = int(request.form['admin_id'])
            dokter_id = int(request.form['dokter_id'])

            biayaadministrasi = BiayaAdministrasi.query.filter_by(id=admin_id).first()
            dokter = Dokter.query.filter_by(id=dokter_id).first()

            if not biayaadministrasi or not dokter:
                flash("Data Administrasi atau Dokter tidak valid.", "danger")
                return redirect(url_for('edit_pembayaran', id_bmedis=id_bmedis))

            # Hitung ulang total bayar
            total_bayar = Decimal(biayaadministrasi.biaya) + Decimal(dokter.tarif_medis)

            # Update objek pembayaran
            pembayaran.id_daftar = request.form['id_daftar']
            pembayaran.tanggal_bayar = request.form.get('tanggal_bayar', date.today())
            pembayaran.admin_id = admin_id
            pembayaran.dokter_id = dokter_id
            pembayaran.total_bayar = total_bayar

            # Simpan perubahan
            db.session.commit()
            flash("Pembayaran berhasil diperbarui.", "success")
        except Exception as e:
            print(f"Error: {e}")
            flash("Terjadi kesalahan saat memperbarui pembayaran.", "danger")

        return redirect(url_for('pembayaran'))

    return render_template('edit_pembayaran.html', pembayaran=pembayaran)

@app.route('/delete_pembayaran/<string:id_bmedis>', methods=['GET'])
@login_dulu
def delete_pembayaran(id_bmedis):
    try:
        
        pembayaran = Pembayaran.query.get_or_404(id_bmedis)

        
        db.session.delete(pembayaran)
        db.session.commit()

        flash('Pembayaran berhasil dihapus!', 'success')
    except Exception as e:
        print(f"Error: {e}")
        flash('Terjadi kesalahan saat menghapus pembayaran.', 'danger')

    return redirect(url_for('pembayaran'))

@app.route('/detail_obat')
@login_dulu
def detail_obat():
    # Ambil semua data dari Pendaftaran, Obat, dan Pegawai untuk dropdown atau keperluan lain
    pasiennya = Pendaftaran.query.all()  
    print("Data pasien:", [(p.id_daftar, p.nama) for p in pasiennya])
    obatnya = Obat.query.all()  
    pegawai = Pegawai.query.all()  
    data = DetailObat.query.all()  

    total = sum(detail.qty * detail.harga for detail in data)

    return render_template(
        'detailobat.html', 
        pasiennya=pasiennya, 
        obatnya=obatnya, 
        pegawai=pegawai, 
        data=data,
        total=total
    )

@app.route('/tambahdetailobat', methods=['POST'])
@login_dulu
def tambahdetailobat():
    print("Received POST request")
    print("Form data received:")
    print(f"id_dobt: {request.form.get('id_dobt')}")
    print(f"daftar_id: {request.form.get('daftar_id')}")
    print(f"id_obat: {request.form.get('id_obat')}")
    print(f"qty: {request.form.get('qty')}")
    print(f"harga: {request.form.get('harga')}")
    print(f"total: {request.form.get('total')}")
    print(f"tanggal_resep: {request.form.get('tanggal_resep')}")
    print(f"pegawai_id: {request.form.get('pegawai_id')}")

    try:
        # Mengambil data dari form
        id_dobt = request.form.get('id_dobt', None)
        daftar_id = request.form.get('daftar_id', None)
        id_obat = request.form.get('id_obat', None)
        qty = int(request.form.get('qty', 0))
        harga = float(request.form.get('harga', 0.0))
        tanggal_resep = date.fromisoformat(request.form.get('tanggal_resep', ''))
        pegawai_id = request.form.get('pegawai_id', None)

        # Validasi id_daftar
        if not daftar_id:
            flash('ID Pasien (id_daftar) harus dipilih.', 'danger')
            return redirect(url_for('tambahdetailobat'))

        total = qty * harga

        # Menambahkan data ke database
        detail_obat = DetailObat(
            id_dobt=id_dobt,
            daftar_id=daftar_id,
            id_obat=id_obat,
            qty=qty,
            harga=harga,
            total=total,
            tanggal_resep=tanggal_resep,
            pegawai_id=pegawai_id
        )
        db.session.add(detail_obat)
        db.session.commit()

        flash('Detail obat berhasil ditambahkan!', 'success')
    except Exception as e:
        db.session.rollback()
        print("Error:", e)
        flash('Terjadi kesalahan saat menambahkan detail obat.', 'danger')

    return redirect(url_for('detail_obat'))

@app.route('/edit_detail_obat/<string:id_dobt>', methods=['GET', 'POST'])
@login_dulu
def edit_detail_obat(id_dobt):
    detail = DetailObat.query.get_or_404(id_dobt)
    print("Detail obat:", detail)

    if request.method == 'POST':
        try:
            detail.daftar_id = request.form['daftar_id']
            detail.id_obat = request.form['id_obat']
            detail.qty = int(request.form['qty'])
            detail.harga = float(request.form['harga'])
            detail.tanggal_resep = datetime.strptime(request.form['tanggal_resep'], '%Y-%m-%d')
            detail.pegawai_id = request.form['pegawai_id']

            # Perhitungan ulang total harga
            detail.total = detail.qty * detail.harga

            # Menyimpan perubahan ke database
            db.session.commit()
            flash('Detail obat berhasil diperbarui!', 'success')
            return redirect(url_for('detail_obat'))

        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", 'danger')

    pasiennya = Pendaftaran.query.all()
    obatnya = Obat.query.all()
    pegawai = Pegawai.query.all()

    return render_template(
        'editdetailobat.html',
        detail=detail,
        pasiennya=pasiennya,
        obatnya=obatnya,
        pegawai=pegawai
    )

@app.route('/hapus_detail_obat/<string:id_dobt>', methods=['POST'])
@login_dulu
def hapus_detail_obat(id_dobt):
    detail = DetailObat.query.get_or_404(id_dobt)
    try:
        db.session.delete(detail)
        db.session.commit()
        flash('Detail obat berhasil dihapus!', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", 'danger')

    return redirect(url_for('detail_obat'))

@app.route('/biaya_obat')
@login_dulu
def bayar_obat():
    pasiennya = Pendaftaran.query.all()  
    print("Data pasien:", [(p.id_daftar, p.nama) for p in pasiennya])
    data = BiayaObat.query.all()  

    return render_template(
        'bayarobat.html', 
        pasiennya=pasiennya, 
        data=data
    )

@app.route('/tambah_biayaobat', methods=['POST'])
def tambah_biayaobat():
    data = request.get_json()
    daftar_id = data.get('daftar_id')
    metode_bayar = data.get('metode_bayar')

    # Hitung total biayaobat dari detail_obat
    total_biaya = db.session.query(db.func.sum(DetailObat.qty * DetailObat.harga)) \
                            .filter_by(daftar_id=daftar_id).scalar()

    if not total_biaya:
        return jsonify({"message": f"Tidak ada data detail_obat untuk daftar_id '{daftar_id}'"}), 404

    # Buat data pembayaran obat baru
    new_biayaobat = BiayaObat(
        id_bobt=f"BO_{daftar_id}",
        daftar_id=daftar_id,
        total_bayar=total_biaya,
        metode_bayar=metode_bayar
    )

    # Simpan ke database
    db.session.add(new_biayaobat)
    db.session.commit()

    return jsonify({"message": "Data biaya obat berhasil ditambahkan", "data": {
        "id_bobt": new_biayaobat.id_bobt,
        "daftar_id": new_biayaobat.daftar_id,
        "total_bayar": new_biayaobat.total_bayar,
        "metode_bayar": new_biayaobat.metode_bayar
    }}), 201

@app.route('/edit_biayaobat/<id_bobt>', methods=['PUT'])
def edit_biayaobat(id_bobt):
    data = request.get_json()
    metode_bayar = data.get('metode_bayar')

    biayaobat = BiayaObat.query.filter_by(id_bobt=id_bobt).first()

    if not biayaobat:
        return jsonify({"message": f"Data biaya obat dengan id '{id_bobt}' tidak ditemukan"}), 404

    if metode_bayar:
        biayaobat.metode_bayar = metode_bayar

    # Update total biayaobat jika diperlukan
    total_biaya = db.session.query(db.func.sum(DetailObat.qty * DetailObat.harga)) \
                            .filter_by(daftar_id=biayaobat.daftar_id).scalar()
    biayaobat.total_biaya = total_biaya

    db.session.commit()

    return jsonify({"message": "Data pembayaran obat berhasil diperbarui", "data": {
        "id_bobt": biayaobat.id_bobt,
        "daftar_id": biayaobat.daftar_id,
        "total_bayar": biayaobat.total_bayar,
        "metode_bayar": biayaobat.metode_bayar
    }})
	
@app.route('/hapus_biayaobat/<id_bobt>', methods=['DELETE'])
def hapus_bayarobat(id_bobt):
    biayaobat = BiayaObat.query.filter_by(id_bobt=id_bobt).first()

    if not biayaobat:
        return jsonify({"message": f"Data biaya obat dengan id '{id_bobt}' tidak ditemukan"}), 404

    db.session.delete(biayaobat)
    db.session.commit()

    return jsonify({"message": "Data pembayaran obat berhasil dihapus"}), 200



@app.route('/logout')
@login_dulu
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
 #   app.run(debug=True, port=7000)
 app.run(host='0.0.0.0', port=7000)