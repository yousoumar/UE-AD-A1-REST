from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3201
HOST = "0.0.0.0"

with open("{}/databases/bookings.json".format("."), "r") as jsf:
    bookings = json.load(jsf)["bookings"]


@app.route("/", methods=["GET"])
def home():
    return "<h1 style='color:blue'>Welcome to the Booking service!</h1>"


@app.route("/bookings", methods=["GET"])
def get_json():
    res = make_response(jsonify(bookings), 200)
    return res


@app.route("/bookings/<userid>", methods=["GET"])
def get_booking_for_user(userid):
    for booking in bookings:
        if str(booking["userid"]) == str(userid):
            res = make_response(jsonify(booking), 200)
            return res
    return make_response(
        jsonify({"error": "no booking correspond to the given user ID"}), 400
    )


@app.route("/bookings/<userid>", methods=["POST"])
def add_booking_byuser(userid):
    data = request.get_json()
    res = requests.get("http://172.16.134.10:3202/showtimes")
    schedule = res.json()

    for schedule_item in schedule:
        if (
            schedule_item["date"] == data["date"]
            and data["movieid"] in schedule_item["movies"]
        ):
            for booking in bookings:
                if booking["userid"] == userid:
                    for item in booking["dates"]:
                        if item["date"] == data["date"]:
                            if data["movieid"] in item["movies"]:
                                return make_response(
                                    jsonify(
                                        {"error": "movie already booked by this user"}
                                    ),
                                    409,
                                )
                            item["movies"].append(data["movieid"])
                            return make_response(jsonify(booking), 200)

                    booking["dates"].append(
                        {
                            "date": data["date"],
                            "movies": [data["movieid"]],
                        }
                    )
                    return make_response(jsonify(booking), 200)
            # As of now we assume the userid is valid
            bookings.append(
                {
                    "userid": userid,
                    "dates": [{"date": data["date"], "movies": [data["movieid"]]}],
                }
            )
            return make_response(jsonify(bookings[-1]), 200)

    return make_response(
        jsonify(
            {
                "error": "date or movieid incorect or not provided, make sure you provied a movieid that is part of a exting date in the showtimes"
            }
        ),
        409,
    )


if __name__ == "__main__":
    print("Server running in port %s" % (PORT))
    app.run(host=HOST, port=PORT)
