from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3203
HOST = "localhost"

with open("{}/databases/users.json".format("."), "r") as jsf:
    users = json.load(jsf)["users"]


@app.route("/", methods=["GET"])
def home():
    return "<h1 style='color:blue'>Welcome to the User service!</h1>"


@app.route("/users", methods=["GET"])
def get_users():
    res = make_response(jsonify(users), 200)
    return res


@app.route("/users/<userid>", methods=["GET"])
def get_user_by_id(userid):
    for user in users:
        if str(user["id"]) == str(userid):
            res = make_response(jsonify(user), 200)
            return res
    return make_response(jsonify({"error": "User not found"}), 400)


@app.route("/users/<userid>/bookings", methods=["GET"])
def get_user_bookings(userid):
    res = requests.get("http://localhost:3201/bookings/{}".format(userid))
    booking = res.json()
    for date_item in booking["dates"]:
        mapped_movies = []
        for movie_id in date_item["movies"]:
            res = requests.get("http://localhost:3200/movies/{}".format(movie_id))
            movie = res.json()
            mapped_movies.append(movie)
        date_item["movies"] = mapped_movies
    return make_response(jsonify(booking), res.status_code)


@app.route("/users/<userid>/bookings", methods=["POST"])
def book_for_user(userid):
    data = request.get_json()
    res = requests.post("http://localhost:3201/bookings/{}".format(userid), json=data)
    booking = res.json()

    return make_response(jsonify(booking), res.status_code)


if __name__ == "__main__":
    print("Server running in port %s" % (PORT))
    app.run(host=HOST, port=PORT)
