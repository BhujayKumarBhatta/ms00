from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade

db = SQLAlchemy()
migrate = Migrate()


# flask_app_var = Flask(__name__)

# from app1.views import views_bp
# flask_app_var.register_blueprint(views_bp)
def create_app(config_map_list=None, blue_print_list=None):
    app = Flask(__name__)
    if config_map_list:
        for m in config_map_list:
            app.config.update(m)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:welcome123@tldbserver100:3306/auth'    
    db.init_app(app)
    with app.app_context():

        if db.engine.url.drivername == 'pymysql':
            migrate.init_app(app, db,  render_as_batch=True)
        else:
            migrate.init_app(app, db )
#         db.create_all()
#         db.session.commit()
        #migrate.init_app(app, db, render_as_batch=True)
#         upgrade(directory=migraion_dir)
    
    if blue_print_list:
        for bp in blue_print_list:
            app.register_blueprint(bp)
    
    return app
