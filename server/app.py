
import os

from flask import Flask, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, User, UserSchema, Article, ArticlesSchema

app = Flask(__name__)


os.makedirs(app.instance_path, exist_ok=True)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False


app.secret_key = b"dev"

db.init_app(app)
migrate = Migrate(app, db)

api = Api(app)


class ClearSession(Resource):
    def get(self):
        session["user_id"] = None
        return {}, 204


class Login(Resource):
    def post(self):
        data = request.get_json() or {}
        username = data.get("username")

        if not username:
            return {}, 401

        user = User.query.filter(User.username == username).first()
        if not user:
            return {}, 401

        session["user_id"] = user.id
        return UserSchema().dump(user), 200


class Logout(Resource):
    def delete(self):
        session["user_id"] = None
        return {}, 204


class CheckSession(Resource):
    def get(self):
        user_id = session.get("user_id")
        if not user_id:
            return {}, 401

        user = User.query.get(user_id)
        if not user:
            return {}, 401

        return UserSchema().dump(user), 200


class IndexArticle(Resource):
    def get(self):
        articles = [ArticlesSchema().dump(article) for article in Article.query.all()]
        return articles, 200


api.add_resource(ClearSession, "/clear")
api.add_resource(Login, "/login")
api.add_resource(Logout, "/logout")
api.add_resource(CheckSession, "/check_session")
api.add_resource(IndexArticle, "/articles")


if __name__ == "__main__":
    app.run(port=5555, debug=True)