from flask_app import app
from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_bcrypt import Bcrypt
from flask_app.models import user
import re

DB = "tvshows"

class Show:
    
    def __init__(self, show):
        self.id = show["id"]
        self.title = show["title"]
        self.network = show["network"]
        self.date = show["date"]
        self.description = show["description"]
        self.created_at = show["created_at"]
        self.updated_at = show["updated_at"]
        self.user = None

    @classmethod
    def create_valid_show(cls, show_dict):
        if not cls.is_valid(show_dict):
            return False
        
        query = """INSERT INTO shows (title, network, date, description, user_id) VALUES (%(title)s, %(network)s, %(date)s, %(description)s, %(user_id)s);"""
        show_id = connectToMySQL(DB).query_db(query, show_dict)
        show = cls.get_by_id(show_id)

        return show

    @classmethod
    def get_by_id(cls, show_id):
        print(f"get show by id {show_id}")
        data = {"id": show_id}
        query = """SELECT shows.id, shows.created_at, shows.updated_at, network, title, date, description,
                    users.id as user_id, first_name, last_name, email, password, users.created_at as uc, users.updated_at as uu
                    FROM shows
                    JOIN users on users.id = shows.user_id
                    WHERE shows.id = %(id)s;"""
        
        result = connectToMySQL(DB).query_db(query,data)
        
        print("result of query:")
        print(result)
        result = result[0]
        show = cls(result)
        
        show.user = user.User(
                {
                    "id": result["user_id"],
                    "first_name": result["first_name"],
                    "last_name": result["last_name"],
                    "email": result["email"],
                    "password": result["password"],
                    "created_at": result["uc"],
                    "updated_at": result["uu"]
                }
            )

        return show

    @classmethod
    def delete_show_by_id(cls, show_id):

        data = {"id": show_id}
        query = "DELETE from shows WHERE id = %(id)s;"
        connectToMySQL(DB).query_db(query,data)

        return show_id


    @classmethod
    def update_show(cls, show_dict, session_id):

        show = cls.get_by_id(show_dict["id"])
        if show.user.id != session_id:
            flash("You have to be the show poster to update this show.")
            return False

        if not cls.is_valid(show_dict):
            return False
        
        query = """UPDATE shows
                    SET title = %(title)s, network = %(network)s, date=%(date)s, description = %(description)s
                    WHERE id = %(id)s;"""
        result = connectToMySQL(DB).query_db(query,show_dict)
        show = cls.get_by_id(show_dict["id"])
        
        return show

    @classmethod
    def get_all(cls):
        query = """SELECT 
                    shows.id, shows.created_at, shows.updated_at, description, title, network, date,
                    users.id as user_id, first_name, last_name, email, password, users.created_at as uc, users.updated_at as uu
                    FROM shows
                    JOIN users on users.id = shows.user_id;"""
        show_data = connectToMySQL(DB).query_db(query)
        shows = []

        for show in show_data:
            show_obj = cls(show)
            show_obj.user = user.User(
                {
                    "id": show["user_id"],
                    "first_name": show["first_name"],
                    "last_name": show["last_name"],
                    "email": show["email"],
                    "password": show["password"],
                    "created_at": show["uc"],
                    "updated_at": show["uu"]
                }
            )
            shows.append(show_obj)

        return shows

    @staticmethod
    def is_valid(show_dict):
        valid = True
        flash_string = " field is required and must be at least 3 characters."
        if len(show_dict["title"]) < 3:
            flash("Title" + flash_string)
            valid = False
        if len(show_dict["network"]) <= 2:
            flash("Network is required.")
            valid = False
        if len(show_dict["date"]) <= 0:
            flash("Date is required.")
            valid = False
        if len(show_dict["description"]) < 3:
            flash("Description " + flash_string)
            valid = False

        return valid