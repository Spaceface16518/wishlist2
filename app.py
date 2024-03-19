import base64
from http import HTTPStatus
from bson import ObjectId
from flask import Flask, redirect, render_template, request
from pymongo import MongoClient

app = Flask(__name__)

# Connect to MongoDB

client = MongoClient("mongodb://localhost:27017/")

db = client["wishlist"]

common = db["common"]
wishes = db["wishes"]


@app.route("/")
def index():
    common_wishes = list(common.find())
    wishlist = list(wishes.find())

    return render_template("index.html", common_wishes=common_wishes, wishlist=wishlist)


@app.route("/admin")
def admin():
    common_wishes = list(common.find())
    wishlist = list(wishes.find())

    return render_template("admin.html", common_wishes=common_wishes, wishlist=wishlist)


@app.post("/admin/common/delete")
def delete_common():
    id = request.form["id"]
    common.delete_one({"_id": ObjectId(id)})

    return redirect("/admin")


@app.post("/admin/common/add")
def add_common():
    name = request.form["name"]
    common.insert_one({"name": name})

    return redirect("/admin")


@app.post("/admin/wish/delete")
def delete_wish():
    id = request.form["id"]
    wishes.delete_one({"_id": ObjectId(id)})

    return redirect("/admin")


@app.post("/admin/wish/add")
def add_wish():
    name = request.form["name"]
    print(request.files)
    if "image" in request.files:
        image = base64.b64encode(request.files["image"].read()).decode()
        print(image)
    else:
        image = None

    wishes.insert_one({"name": name, "image": image})

    return redirect("/admin")


@app.post("/wish/claim")
def claim_wish():
    id = request.form["id"]

    wishes.update_one({"_id": ObjectId(id)}, {"$set": {"owner": "ur mom"}})

    return redirect("/")
