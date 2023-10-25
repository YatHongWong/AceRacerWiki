import sqlite3
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from helpers import login_required, admin_required, trusted_required
from flask_ckeditor import CKEditor

# Configure application
app = Flask(__name__)

# Configure CKEditor
ckeditor = CKEditor(app)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


def generate_list(section):
    """Takes in a string and returns a sorted list of options for dropdown menus"""
    result_unsorted = []
    # Connect to database
    with sqlite3.connect("project.db") as con:
        cur = con.cursor()
        # Find all items from the specified section
        cur.execute("SELECT item FROM options WHERE section = ?", (section,))
        res = cur.fetchall()
        # Generate list of items (the options)
        for item in res:
            result_unsorted.append(item[0])
    return sorted(result_unsorted)
    

def get_comments(item):
    """Takes in a string - returns a list of dictionaries of comments and other information"""
    comments = []
    # Connect to database
    with sqlite3.connect("project.db") as con:
        cur = con.cursor()
        # Find all comments belonging to the specific item being accessed by the user in descending order (so newest comments are at the top)
        cur.execute("SELECT id,comment,username FROM comments WHERE item = ? ORDER BY id DESC", (item,))
        res = cur.fetchall()
        # Generate a list of dictionaries, each with a comment, username, id
        for id, comment, username in res:
            comments.append({"comment":comment, "username":username, "id":id})
    return comments


# Pass dropdown options to layout.html
@app.context_processor
def layout():
    """Returns a dictionary of lists"""
    cars = generate_list("cars")
    maps = generate_list("maps")
    ecus = generate_list("ecus")

    # make a dictionary of all the options for dropdowns
    lists = {"cars":cars, "maps":maps, "ecus":ecus}

    # Also reset messaging preset
    session["preset"] = ""
    return lists


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    """Generate the site's index page"""
    # Connect to database
    # Get website statistics
    with sqlite3.connect("project.db") as con:
        cur = con.cursor()

        # Get number of users
        cur.execute("SELECT COUNT(id) FROM users")
        num_users = cur.fetchone()[0]

        # Get total number of edits
        cur.execute("SELECT COUNT(id) FROM edits")
        num_edits = cur.fetchone()[0]

        # Get total number of comments
        cur.execute("SELECT COUNT(id) FROM comments")
        num_comments = cur.fetchone()[0]

        # Get newest user
        cur.execute("SELECT username, admin FROM users ORDER BY id DESC")
        new_user, new_user_level = cur.fetchone()

        # Assign the new user's username a colour by level
        if new_user_level == 1:
            colour = "link-danger"
        elif new_user_level == 2:
            colour = "link-info"
        elif new_user_level == 0:
            colour = "link-secondary"

        # Get list of admins
        admins = []
        cur.execute("SELECT username FROM users WHERE admin = 1")
        for row in cur.fetchall():
            admins.append(row[0])
    return render_template("index.html", num_edits=num_edits, num_users=num_users, num_comments=num_comments, new_user=new_user, admins=admins, colour=colour)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    
    # Forget any session information (if any somehow exist)
    session.clear()

    if request.method == "POST":

        # Check if username was provided
        if not request.form.get("username"):
            flash("username not provided")
            return render_template("login.html")
        
        # Check if password was provided
        elif not request.form.get("password"):
            flash("password not provided")
            return render_template("login.html")
        
        # Connect to database to check username and password
        with sqlite3.connect("project.db") as con:
            cur = con.cursor()

            # Check username and password
            cur.execute("SELECT id, username, hash, admin FROM users WHERE username = ?", (request.form.get("username"),))
            res = cur.fetchone()
            if res != None:
                id, username, hash, admin = res
                if not check_password_hash(hash, request.form.get("password")):
                    # Redirect to login page and alert user that their login credentials are incorrect
                    flash("Password or username incorrect! Please try again.") 
                    return render_template("login.html")
            else:
                flash("Password or username incorrect! Please try again.")
                return render_template("login.html")
            # Remember who has logged in
            # Store id in session
            session["user_id"] = id

            # Store username in session
            session["username"] = username

            # Store user's permission level in session
            session["admin"] = admin

            # Set default preset for sending a message
            session["preset"] = ""

            # Alert user of successful login
            flash(f"Welcome, {username}.")

            # Redirect user to home page if login was successful
            return redirect("/")
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""
    # Forget all session information (user_id, username, admin, preset)
    session.clear()

    # Alert user for successfully logging out
    flash("Logged out.")
    
    # Redirect user to homepage
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        # Generate list of existing usernames
        usernames = []
        with sqlite3.connect("project.db") as con:
            cur = con.cursor()
            cur.execute("SELECT username FROM users")
            for names in cur.fetchall():
                usernames.append(names[0])

        # Check if username was filled in
        if not request.form.get("username"):
            flash("Please enter a username")
            return redirect("/register")

        # Check if username already exists
        elif request.form.get("username") in usernames:
            flash("Username already taken")
            return redirect("/register")

        # Check if password was filled in
        elif not request.form.get("password"):
            flash("Enter a password")
            return redirect("/register")

        # Check if confirmation password was filled in
        elif not request.form.get("confirmation_password"):
            flash("Confirm your password")
            return redirect("/register")

        # Check if confirmation password matches
        elif request.form.get("confirmation_password") != request.form.get("password"):
            flash("Confirmation password does not match password")
            return redirect("/register")

        # Add username and hash of password to database
        else:
            username = request.form.get("username")
            hash = generate_password_hash(request.form.get("password"))

            with sqlite3.connect("project.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, hash))
                con.commit()

                # Alert user of successful registration and redirect to login page
                flash("You are registered, please login.")
                return render_template("login.html")
    else:
        return render_template("register.html")
    

# Selected items from dropdown menu are sent to be displayed here
@app.route("/<section>/<item>", methods=["GET", "POST"])
def info(section, item): 
    """Display page with information about the selected item"""
    # Search database to find the article body
    with sqlite3.connect("project.db") as con:
        cur = con.cursor()
        cur.execute("SELECT article_body FROM contents WHERE names = ?", (item,))
        res = cur.fetchone()

        # Search for comments
        comments = get_comments(item)

        # Check who edited it last
        cur.execute("SELECT username FROM edits WHERE item = ? AND section = ? ORDER BY id DESC", (item, section))
        editor = ""
        res2 = cur.fetchone()
        if res2 == None:
            editor = "Be the first to edit!"
        else:
            cur.execute("SELECT admin FROM users WHERE username = ?", (res2[0],))
            if cur.fetchone()[0] == 1:
                editor = f'Last edited by: <a class="link-danger" href="/users/{res2[0]}">{res2[0]}</a>'
            else:
                editor = f'Last edited by: <a class="link-info" href="/users/{res2[0]}">{res2[0]}</a>'
        # If no body exists, let them know there is no information here yet
        if res == None:
            return render_template("display.html", admin=session.get("admin"), comments=comments, section=section, item=item, article_body="No information here yet", editor=editor)
        
        # If an article body was found, display it
        else:
            article_body = res[0]
            return render_template("display.html", admin=session.get("admin"), comments=comments, section=section, item=item, article_body=article_body, editor=editor)


@app.route("/edit", methods=["POST"])
@login_required
@trusted_required
def edit():
    """Display rich text editor for editing information"""
    section = request.form.get("section")
    item = request.form.get("item")
    article_body = request.form.get("article_body")
    return render_template("edit.html", section=section, item=item, article_body=article_body)


@app.route("/editing", methods=["POST"])
@login_required
@trusted_required
def process_edit():
    """Save changes made to article body"""
    # Make sure all required information to make a table entry is here
    if not request.form.get("section"):
        return
    elif not request.form.get("item"):
        return
    elif not request.form.get("ckeditor"):
        return
    else:
        # Get all required information to save changes
        section = request.form.get("section")
        item = request.form.get("item")
        edited_article = request.form.get("ckeditor")

        # Connect to database to save changes
        with sqlite3.connect("project.db") as con:
            cur = con.cursor()
            cur.execute("SELECT article_body FROM contents WHERE names = ?", (item,))
            res = cur.fetchone()
            # Check if any information was already stored
            # If not, create a table entry
            if res == None:
                cur.execute("INSERT INTO contents (article_body, names) VALUES (?, ?)", (edited_article, item))
            
            # If there is an existing article, overwrite it
            else:
                cur.execute("UPDATE contents SET article_body = ? WHERE names = ?", (edited_article, item))
            con.commit()   
            cur.execute("INSERT INTO edits (item, section, username) VALUES (?, ?, ?)", (item, section, session["username"]))

        # Load edited page and alert user of the successful edit
        flash("Changes saved.")
        return redirect(url_for("info", section=section, item=item))
    

@app.route("/dashboard")
@login_required
def panel():
    """Load the user's dashboard"""
    user_comments = []
    with sqlite3.connect("project.db") as con:
        cur = con.cursor()

        # Generate the list of comments by the user
        cur.execute("SELECT item, comment FROM comments WHERE username = ?", (session["username"],))
        for item, comment in cur.fetchall():
            user_comments.append({"item":item, "comment":comment})
        
        # Get number of edits by the user
        cur.execute("SELECT COUNT(item) FROM edits WHERE username = ?", (session["username"],))
        num_edits = cur.fetchone()[0]

        # Get the user's total number of comments
        cur.execute("SELECT COUNT(comment) FROM comments WHERE username = ?", (session["username"],))
        num_comments = cur.fetchone()[0]
    return render_template("panel.html", user_comments=user_comments, username=session["username"], admin=session["admin"], id=session["user_id"], num_edits=num_edits, num_comments=num_comments)


@app.route("/comment", methods=["POST"])
@login_required
def comment():
    """Add a new comment"""

    # Check all needed information is present
    if not request.form.get("comment"):
        return "comment error: comment not found"
    
    elif not request.form.get("item"):
        return "comment error: item not found"

    else:
        # Take information from form
        username = session["username"]
        item = request.form.get("item")
        comment = request.form.get("comment")
        section = request.form.get("section")

        # Add comment to database
        with sqlite3.connect("project.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO comments (item, comment, username) VALUES (?, ?, ?)", (item, comment, username))
            con.commit()

        # Tell user comment has been posted and show them the updated page
        flash("Comment posted successfully.")
        return redirect(url_for("info", section=section, item=item))

    

@app.route("/delete", methods=["POST"])
@login_required
@admin_required
def delete_comment():
    """Delete a comment"""

    # Check that all information needed for deleting is present
    if not request.form.get("id"):
        return "delete failed: no comment id"

    elif not request.form.get("item"):
        return "delete failed: no item"
    
    elif not request.form.get("section"):
        return "delete failed: no section"
    
    id = request.form["id"]
    item = request.form["item"]
    section = request.form["section"]

    # Delete comment based on comment id
    with sqlite3.connect("project.db") as con:
        cur = con.cursor()
        cur.execute("DELETE FROM comments WHERE id = ?", (id,))
        con.commit()

    # Let user know the comment was deleted and show updated page
    flash("Comment deleted.")
    return redirect(url_for("info", section=section, item=item))


@app.route("/search", methods=["POST"])
def search():
    """Search items, takes in a search query and shows a search page with matching information"""
    # Make sure user has inputted something to search for
    if not request.form.get("search"):
        return "nothing inputted"
    
    # Searching process
    else:
        search = request.form["search"]
        with sqlite3.connect("project.db") as con:
            cur = con.cursor()

            # Get pages
            cur.execute("SELECT section, item FROM options WHERE item LIKE ?", (search+"%",))
            res = cur.fetchall()

            # Generate a results list of dictionaries with all matching items' pages
            results = []
            for section, item in res:
                results.append({"section": section, "item": item})
            
            # Sort the results list into smaller categorised lists based on section
            cars_search = []
            ecus_search = []
            maps_search = []
            
            for row in results:
                if row["section"] == "cars":
                    cars_search.append(row["item"])
                elif row["section"] == "ecus":
                    ecus_search.append(row["item"])
                elif row["section"] == "maps":
                    maps_search.append(row["item"])

            # Get matching usernames
            users_search = []
            cur.execute("SELECT username FROM users WHERE username LIKE ?",(search+"%",))
            for user in cur.fetchall():
                users_search.append(user[0])
            
            # Let the page know if a list is empty
            all_results = [cars_search, maps_search, ecus_search, users_search]
            for l in all_results:
                if not l:
                    l.append("No matches")

        return render_template("search.html", cars_search=cars_search, maps_search=maps_search, ecus_search=ecus_search, users_search=users_search)


@app.route("/changepass", methods=["GET","POST"])
@login_required
def changepass():
    """Allow user to change password"""
    if request.method == "POST":
        
        # Check if current password was provided
        if not request.form.get("password"):
            flash("Password not entered")
            return redirect("/changepass")
        
        # Check if new password was provided
        elif not request.form.get("new_password"):
            flash("New password not entered")
            return redirect("/changepass")
        
        # Check if new password confirmation was provided
        elif not request.form.get("confirmation_password"):
            flash("New password not confirmed") 
            return redirect("/changepass")
        
        # check password and username
        else:
            with sqlite3.connect("project.db") as con:
                cur = con.cursor()

                # Check password
                cur.execute("SELECT username, hash FROM users WHERE username = ?", (session["username"],))
                res = cur.fetchone()
                if res != None:
                    username, hash = res
                    if not check_password_hash(hash, request.form["password"]):
                        flash("Incorrect password")
                        return redirect("/changepass")
                    
                    # Check that new password is the same as the confirmation password
                    elif request.form["new_password"] != request.form["confirmation_password"]:
                        flash("Confirmation password does not match new password")
                        return redirect("/changepass")
                    
                    # Update password hash
                    else:
                        hash = generate_password_hash(request.form["new_password"])
                        cur.execute("UPDATE users SET hash = ? WHERE username = ?", (hash, username))
                        con.commit()
                        return redirect("/logout")
                else:
                    flash("Username error")
                    return redirect("/changepass")
                
    else:
        return render_template("changepass.html")
    

@app.route("/users/<name>")
def profile(name):
    """Access another user's profile page"""
    with sqlite3.connect("project.db") as con:
        cur = con.cursor()

        # Make sure user exists
        cur.execute("SELECT id, admin FROM users WHERE username = ?", (name,))
        res = cur.fetchone()
        if res == None:
            return "User not found"    
        else:
            uid, admin = res

            # Decide user font colour depending on level
            if admin == 1:
                is_admin = "Administrator"
                color = "text-danger"
            elif admin == 2:
                is_admin = "Trusted"
                color = "text-info"
            else:
                is_admin = "User"
                color = "text"

            # Get number of edits
            cur.execute("SELECT COUNT(item) FROM edits WHERE username = ?", (name,))
            num_edits = cur.fetchone()[0]

            # Get number of comments
            cur.execute("SELECT COUNT(comment) FROM comments WHERE username = ?", (name,))
            num_comments = cur.fetchone()[0]
            return render_template("profile.html",is_admin=is_admin, name=name, uid=uid, num_edits=num_edits, num_comments=num_comments, color=color, level=admin, admin=session.get("admin"))


@app.route("/list")
def list():
    """Show a simple list of contents"""
    return render_template("list.html")


@app.route("/message", methods=["GET","POST"])
@login_required
def message():
    """Send a message"""
    if request.method == "POST":

        # Check if user entered a recipient
        if not request.form.get("recipient"):
            flash("No recipient entered.")
            return redirect("/message")
        
        # Check if user entered a message
        elif not request.form.get("message"):
            flash("No message entered.")
            return redirect("/message") 

        else:
            recipient = request.form["recipient"]
            message = request.form["message"]
            # Check if recipient exists
            with sqlite3.connect("project.db") as con:
                cur = con.cursor()
                cur.execute("SELECT username FROM users WHERE username = ?", (recipient,))
                res = cur.fetchone()
                if res == None:
                    flash("Recipient username incorrect or does not exist.")
                    return redirect("/message")
                # Insert message into database (send)
                elif recipient == session["username"]: 
                    flash("Cannot send messages to yourself.")
                    return redirect("/message")

                else:
                    cur.execute("INSERT INTO messages (message, sender, recipient, datetime) VALUES (?, ?, ?, ?)", (message, session["username"], recipient, datetime.now().strftime("%m/%d/%Y %H:%M:%S")))
                    flash("Message sent.")
                    return redirect("/message")
        
    else:
        return render_template("message.html", preset=session["preset"])
    

@app.route("/inbox")
@login_required
def inbox():
    """Show all recieved messages"""
    with sqlite3.connect("project.db") as con:
        cur = con.cursor()
        cur.execute("SELECT message, sender, datetime FROM messages WHERE recipient = ? ORDER BY id DESC", (session["username"],))
        res = cur.fetchall()

        # Generate list of dictionaries of messages sent to user
        messages=[]
        for message, sender, datetime in res:
            messages.append({"message": message, "sender": sender, "datetime": datetime})
    return render_template("inbox.html", messages=messages)


@app.route("/messagepreset/<preset>")
@login_required
def presetmessage(preset):
    """Auto-fill recipient box using session"""
    session["preset"] = preset
    return redirect("/message")

@app.route("/users")
def userlist():
    """Show list of users categorised by level"""
    with sqlite3.connect("project.db") as con:
        cur = con.cursor()
        
        # Generate list of admins
        admins = []
        cur.execute("SELECT username FROM users WHERE admin = 1")
        for user in cur.fetchall():
            admins.append(user[0])

        # Generate list of trusted members
        trusted = []
        cur.execute("SELECT username FROM users WHERE admin = 2")
        for user in cur.fetchall():
            trusted.append(user[0])

        # Generate list of members
        members = []
        cur.execute("SELECT username FROM users WHERE admin = 0")
        for user in cur.fetchall():
            members.append(user[0])
    
    return render_template("userlist.html", admins=admins, trusted=trusted, members=members)


@app.route("/levelchange", methods=["POST"])
@login_required
@admin_required
def levelchange():
    """Change a user's level"""
    username = request.form["username"]
    level = int(request.form["level"])
    with sqlite3.connect("project.db") as con:
        cur = con.cursor()
        # Demote to regular member
        if level == 2:
            cur.execute("UPDATE users SET admin = 0 WHERE username = ?", (username,))

        # Promote to trusted
        elif level == 0:
            cur.execute("UPDATE users SET admin = 2 WHERE username = ?", (username,))
        con.commit()

    flash("User level changed.")
    return redirect("/users")
