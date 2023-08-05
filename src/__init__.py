from flask import Flask, redirect,jsonify
import os
from src.constants.http_status_codes import *
from src.auth import auth
from src.bookmarks import bookmarks
from src.database import db,Bookmark
from flask_jwt_extended import JWTManager
from flasgger import Swagger, swag_from #swag_from enables us create a yaml file where
#we can define our specs

from src.config.swagger import*


#create_app is the application factory function. you'all add to it later 
def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    #tells flask that we must have some configs that might have some files outside here
    #__name__ is the name of the current python module. the app needs to know where its located
    #to set up some paths, and __name__ is the convenient way to tell it that
    #instance_relative_config=True tells the app that configuration files are relative to the
    #instance folder, the instance folder is located outside the flaskr package and can hold
    #local data that shouldnt be committed to version control, such as configuration secrets
    #and the database file
    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=os.environ.get("SECRET_KEY"),
            SQLALCHEMY_DATABASE_URI=os.environ.get("SQLALCHEMY_DB_URI"),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY'),

            SWAGGER={
                'title':"Bookmarks API",
                'uiversion':3
            }
        )
        #app.config.from_mapping sets some default configuration that the app will use
    else:
        #load the test config if passed in
        app.config.from_mapping(test_config)
    db.app=app
    db.init_app(app) 

    #==setup the jwt manager
    JWTManager(app)


    app.register_blueprint(auth)
    app.register_blueprint(bookmarks)

    #configuring swagger for the appplication
    Swagger(app, config=swagger_config, template=template)

    @app.get('/<short_url>')
    @swag_from('./docs/short_url.yaml')
    def redirect_to_url(short_url):
        bookmark = Bookmark.query.filter_by(short_url=short_url).first_or_404()
        #==incement the visits
        if bookmark:
            bookmark.visits += 1
            db.session.commit()
            return redirect(bookmark.url)

    #===route for handling errors 
    @app.errorhandler(HTTP_404_NOT_FOUND)
    def handle_404(e):
        return jsonify({'error':'Not found'}, HTTP_404_NOT_FOUND)
    
    #===route for handling server error
    @app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
    def handle_500(e):
        return jsonify(
            {'error':'Something went wrong, We are on it'}, HTTP_500_INTERNAL_SERVER_ERROR)
    

    return app