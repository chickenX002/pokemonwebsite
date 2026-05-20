from flask import Flask, request, redirect, url_for, render_template_string, session
import json
import os

app = Flask(__name__)
app.secret_key = "super_secret_key_change_this"

CONFIG_FILE = "config.json"

# Default config
DEFAULT_CONFIG = {
    "password": "admin123",
    "listings": []
}

# Create config file if it doesn't exist
if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "w") as f:
        json.dump(DEFAULT_CONFIG, f, indent=4)


def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)


@app.route("/")
def home():
    config = load_config()
    listings = config.get("listings", [])

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>My eBay Listings</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f4f4f4;
                margin: 0;
                padding: 20px;
            }

            h1 {
                text-align: center;
            }

            .container {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                max-width: 1200px;
                margin: auto;
            }

            .card {
                background: white;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                transition: 0.2s;
            }

            .card:hover {
                transform: scale(1.02);
            }

            .card img {
                width: 100%;
                height: 220px;
                object-fit: cover;
            }

            .card-content {
                padding: 15px;
            }

            .card-content a {
                text-decoration: none;
                color: #0077cc;
                font-size: 18px;
                font-weight: bold;
            }

            .price {
                margin-top: 10px;
                font-size: 20px;
                color: green;
            }

            .topbar {
                width: 100%;
                background: #222;
                padding: 10px;
                text-align: right;
                box-sizing: border-box;
            }

            .topbar a {
                color: white;
                text-decoration: none;
                margin-right: 20px;
            }
        </style>
    </head>
    <body>

        <div class="topbar">
            <a href="/config">Config Panel</a>
        </div>

        <h1>eBay Listings</h1>

        <div class="container">
            {% for item in listings %}
            <div class="card">
                <a href="{{ item.link }}" target="_blank">
                    <img src="{{ item.image }}">
                </a>

                <div class="card-content">
                    <a href="{{ item.link }}" target="_blank">
                        {{ item.title }}
                    </a>

                    <div class="price">
                        {{ item.price }}
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>

    </body>
    </html>
    """, listings=listings)


@app.route("/config", methods=["GET", "POST"])
def config():
    config = load_config()

    # Login
    if not session.get("logged_in"):
        if request.method == "POST":
            password = request.form.get("password")

            if password == config["password"]:
                session["logged_in"] = True
                return redirect(url_for("config"))

            return render_template_string(LOGIN_HTML, error="Wrong password")

        return render_template_string(LOGIN_HTML, error="")

    # Add listing
    if request.method == "POST":
        action = request.form.get("action")

        if action == "add_listing":
            title = request.form.get("title")
            image = request.form.get("image")
            price = request.form.get("price")
            link = request.form.get("link")

            config["listings"].append({
                "title": title,
                "image": image,
                "price": price,
                "link": link
            })

            save_config(config)
            return redirect(url_for("config"))

        elif action == "change_password":
            new_password = request.form.get("new_password")

            if new_password:
                config["password"] = new_password
                save_config(config)

            return redirect(url_for("config"))

        elif action == "delete_listing":
            index = int(request.form.get("index"))

            if 0 <= index < len(config["listings"]):
                config["listings"].pop(index)
                save_config(config)

            return redirect(url_for("config"))

    return render_template_string(CONFIG_HTML, listings=config["listings"])


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("config"))


LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
    <style>
        body {
            font-family: Arial;
            background: #f4f4f4;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }

        .login-box {
            background: white;
            padding: 30px;
            border-radius: 10px;
            width: 300px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        input {
            width: 100%;
            padding: 10px;
            margin-top: 10px;
            box-sizing: border-box;
        }

        button {
            width: 100%;
            padding: 10px;
            margin-top: 15px;
            background: #0077cc;
            color: white;
            border: none;
            cursor: pointer;
        }

        .error {
            color: red;
            margin-top: 10px;
        }
    </style>
</head>
<body>

<div class="login-box">
    <h2>Config Login</h2>

    <form method="POST">
        <input type="password" name="password" placeholder="Password" required>
        <button type="submit">Login</button>
    </form>

    <div class="error">{{ error }}</div>
</div>

</body>
</html>
"""


CONFIG_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Config Panel</title>

    <style>
        body {
            font-family: Arial;
            background: #f4f4f4;
            margin: 0;
            padding: 20px;
        }

        .container {
            max-width: 900px;
            margin: auto;
        }

        .box {
            background: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        input {
            width: 100%;
            padding: 10px;
            margin-top: 10px;
            box-sizing: border-box;
        }

        button {
            padding: 10px 20px;
            margin-top: 15px;
            background: #0077cc;
            color: white;
            border: none;
            cursor: pointer;
        }

        .listing {
            border: 1px solid #ddd;
            padding: 10px;
            margin-top: 10px;
            border-radius: 8px;
        }

        .delete-btn {
            background: red;
        }

        a {
            text-decoration: none;
        }
    </style>
</head>
<body>

<div class="container">

    <div class="box">
        <h2>Add eBay Listing</h2>

        <form method="POST">
            <input type="hidden" name="action" value="add_listing">

            <input type="text" name="title" placeholder="Listing title" required>
            <input type="text" name="image" placeholder="Image URL" required>
            <input type="text" name="price" placeholder="Price" required>
            <input type="text" name="link" placeholder="eBay listing link" required>

            <button type="submit">Add Listing</button>
        </form>
    </div>


    <div class="box">
        <h2>Change Password</h2>

        <form method="POST">
            <input type="hidden" name="action" value="change_password">

            <input type="password" name="new_password" placeholder="New password" required>

            <button type="submit">Change Password</button>
        </form>
    </div>


    <div class="box">
        <h2>Current Listings</h2>

        {% for item in listings %}
            <div class="listing">
                <strong>{{ item.title }}</strong><br>
                {{ item.price }}<br>
                <a href="{{ item.link }}" target="_blank">Open Listing</a>

                <form method="POST">
                    <input type="hidden" name="action" value="delete_listing">
                    <input type="hidden" name="index" value="{{ loop.index0 }}">

                    <button class="delete-btn" type="submit">Delete</button>
                </form>
            </div>
        {% endfor %}
    </div>


    <div class="box">
        <a href="/logout">
            <button>Logout</button>
        </a>
    </div>

</div>

</body>
</html>
"""


if __name__ == "__main__":
    app.run(debug=True)
