from flask_login import LoginManager
from .app import app, db

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Classname4444@localhost/database'
db.init_app(app)

from .views import views

app.register_blueprint(views, url_prefix='/')


def create_database(app):
    db.create_all(app=app)


create_database(app)

from .models import User

login_manager = LoginManager()
login_manager.login_view = 'views.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


