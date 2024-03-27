import base64
from datetime import datetime
from http import HTTPStatus
import os
from uuid import UUID, uuid4
from bson import ObjectId
from flask import Flask, make_response, redirect, render_template, request, url_for
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

from pymongo import MongoClient

app = Flask(__name__)
auth = HTTPBasicAuth()

# Connect to MongoDB

mongodb_uri = os.environ.get("MONGODB_URI")
client = MongoClient(mongodb_uri, uuidRepresentation="standard")

db = client["wishlist"]

common = db["common"]
wishes = db["wishes"]

# auth details
admin_user = "admin"
admin_pass = generate_password_hash(os.environ.get("ADMIN_PASS", "admin"))


@auth.verify_password
def verify_password(username, password):
    return username == admin_user and check_password_hash(admin_pass, password)


@app.route("/")
def index():
    common_wishes = list(common.find({}, sort=[("created_at", -1)]))
    wishlist = list(wishes.find())
    user_id = (
        UUID(request.cookies.get("user_id")) if "user_id" in request.cookies else None
    )

    return render_template(
        "index.html", common_wishes=common_wishes, wishlist=wishlist, user_id=user_id
    )


@app.route("/admin")
@auth.login_required
def admin():
    common_wishes = list(common.find())
    wishlist = list(wishes.find())

    return render_template("admin.html", common_wishes=common_wishes, wishlist=wishlist)


@app.post("/admin/common/delete")
@auth.login_required
def delete_common():
    id = request.form["id"]
    common.delete_one({"_id": ObjectId(id)})

    return redirect(url_for("admin"))


@app.post("/admin/common/add")
@auth.login_required
def add_common():
    name = request.form["name"]
    common.insert_one({"name": name, "created_at": datetime.now()})

    return redirect(url_for("admin"))


@app.post("/admin/wish/delete")
@auth.login_required
def delete_wish():
    id = request.form["id"]
    wishes.delete_one({"_id": ObjectId(id)})

    return redirect(url_for("admin"))


@app.post("/admin/wish/add")
@auth.login_required
def add_wish():
    name = request.form["name"]
    if "image" in request.files:
        image = base64.b64encode(request.files["image"].read()).decode()
    else:
        image = None

    wishes.insert_one({"name": name, "image": image, "created_at": datetime.now()})

    return redirect(url_for("admin"))


@app.post("/wish/claim")
def claim_wish():
    user_id = (
        UUID(request.cookies.get("user_id")) if "user_id" in request.cookies else None
    )
    if user_id is None:
        # set user_id cookie to random uuid
        user_id = uuid4()

    id = request.form["id"]

    wish = wishes.find_one({"_id": ObjectId(id)})
    if wish is None:
        return make_response("Wish not found", HTTPStatus.NOT_FOUND)

    if "owner" in wish and wish["owner"] is not None and wish["owner"] != user_id:
        return make_response("Wish already claimed", HTTPStatus.BAD_REQUEST)

    wishes.update_one({"_id": ObjectId(id)}, {"$set": {"owner": user_id}})

    response = make_response(redirect(url_for("index")))
    response.set_cookie("user_id", str(user_id))
    return response


@app.post("/wish/unclaim")
def unclaim_wish():
    user_id = UUID(request.cookies.get("user_id"))
    if user_id is None:
        # set user_id cookie to random uuid
        user_id = uuid4()

    id = request.form["id"]

    wish = wishes.find_one({"_id": ObjectId(id)})
    if wish is None:
        return make_response("Wish not found", HTTPStatus.NOT_FOUND)

    if wish.get("owner") != user_id:
        return make_response("Wish not claimed by you", HTTPStatus.BAD_REQUEST)

    wishes.update_one({"_id": ObjectId(id)}, {"$set": {"owner": None}})

    return redirect(url_for("index"))
