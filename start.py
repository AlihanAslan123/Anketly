from flask import Flask,render_template,request,redirect,url_for
from flask_bcrypt import Bcrypt
from views import account,process
from utils import my_login_manager,my_bcrypt,log_start
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin


app = Flask(__name__)
app.secret_key = "gizli_anahtar"

my_login_manager.init_app(app)
my_bcrypt.init_app(app)


app.register_blueprint(account)
app.register_blueprint(process)





@app.route('/')
@app.route('/anasayfa')
def home_page():
    return render_template('index.html')



@app.route('/anketler/<kategori>')
def get_by_category(kategori):
    return render_template('anketler.html',kategori=kategori)





    


if __name__ == '__main__':
    log_start('myJob')
    app.run(debug=True)