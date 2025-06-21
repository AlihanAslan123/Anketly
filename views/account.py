from flask import Flask,render_template,request, Blueprint ,current_app , flash ,redirect, url_for
from flask_bcrypt import Bcrypt
from utils import register_user,get_db_engine,my_bcrypt,my_login_manager,get_categorys,sum_anket
from sqlalchemy import text
from classes import User
import re

from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin


"""
     Kayıt ve Authentication işlemlerinin yapıldığı Blueprint
"""

account = Blueprint('account',__name__,template_folder='templates',static_folder="static")

login_manager = my_login_manager
login_manager.login_view = "account.get_login"
bcrypt = my_bcrypt

engine = get_db_engine()



@login_manager.user_loader
def load_user(user_id:int):
    '''
        parametre olarak aldığı id deki userı databaseden yükler ve bir nesne olarak geri döndürür.
        
    '''
    query = text("SELECT id,email from tbl_users where id = :id")
    with engine.connect() as conn:
        result = conn.execute(query,{'id':user_id}).fetchone()
        if result:
            return User(id=result[0],email=result[1])
    return None



@account.route('/login' ,methods=['POST','GET'])
def get_login():
    
    if request.method == "GET":
        return render_template('login.html')
    
    
    elif request.method == "POST":
        
        email = request.form.get("mail")
        password = request.form.get("password")
        remember = request.form.get("remember")
        
        if not email or not password:
            flash("Email ve parola alanları boş bırakılamaz !","danger")
            return redirect(url_for('account.get_login'))
        
        query = text('Select id,email,password FROM tbl_users where email= :email')
        with engine.connect() as conn:        
            user = conn.execute(query,{'email':email}).fetchone()
        
        
        if user and bcrypt.check_password_hash(user[2],password):
            user_obj = User(id=user[0],email=user[1])
            if remember == "1":
                login_user(user_obj,remember=True)
            else:
                login_user(user_obj)
            
            flash("Giriş başarılı","success")            
            return redirect(url_for('home_page'))
        else:
            
            flash("Giriş bilgileri hatalı","danger")
            return redirect(url_for('account.get_login'))
        


@account.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Başarıyla Çıkış yaptınız","info")
    return redirect(url_for('home_page'))
    
            
            


@account.route('/register' , methods=["POST"])
def create_register():
    email = request.form.get("mail")
    # regex kontrolü
    valid = re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)
    password = request.form.get("password")
    cinsiyet = request.form.get("cinsiyet")
    if all([email, password, cinsiyet]) and valid:
        success = register_user(current_app, email, password, cinsiyet)
        if success:
            flash("Kayıt başarılı! Giriş yapabilirsiniz.", "success")
            return redirect(url_for("account.get_login"))  # login sayfasına yönlendir
        else:
            flash("Kayıt sırasında bir hata oluştu. Lütfen tekrar deneyin.", "danger")
            return redirect(url_for("account.get_login"))  # kayıt sayfasına geri dön
    else:
        flash("Kayıt sırasında bir hata oluştu. Lütfen tekrar deneyin.", "danger")
        return redirect(url_for("account.get_login"))
    
    




@account.route('/dashboard',methods=['GET'])
@login_required
def get_dashboard():
    olusturulmus_anket_sayisi,cozulen_anket_sayisi = sum_anket()
    return render_template('dashboard.html',olusturulmus_anket_sayisi=olusturulmus_anket_sayisi,cozulen_anket_sayisi=cozulen_anket_sayisi)


@account.route('/anketOlustur',methods=['GET','POST'])
@login_required
def create_anket():
    '''
    anket oluşturma sayfasını açar. ve kategoriler comboboxına değerleri parametre olarak verir.
    '''
    kategoriler_dizisi = get_categorys(engine=engine)
    return render_template('anketOlustur.html',kategoriler_dizisi=kategoriler_dizisi)

