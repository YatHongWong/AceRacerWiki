
# Ace Racer Wiki
***
#### Video Demo: https://youtu.be/f_iTcykOrrk
#### Description: Acer Racer Wiki is a web application that allows users to collaborate and create a wealth of information about the game Ace Racer. Users with appropriate privileges are able to edit each article with a rich text editor.
#### Motivation: I play Ace Racer a lot but finding detailed information about the contents of the game is difficult because the game didn't have a wiki page, and in game descriptions are not sufficient.
***
## Technologies

* Python 3
* SQLite 3
* Flask
* Bootstrap 5
* HTML
* CSS
* CKEditor 4
***

## Features

#### Any user
* Account registration
* View articles and comments

#### Registered users
* Password Change
* Login/Logout
* Messaging
* Inbox
* View Dashboard
* Commenting

#### Trusted users
* Article editing (with CKEditor 4)

#### Administrators
* Change a user's privilege level
* Delete comments
***

## Files and Folders
* misc
    * update_options.py - A simple python script used to update contents of the website after a game update
* static
    * ckeditor - A folder containing a custom build of CKEditor 4
    * images - A folder containing images used for index page and navbar
    * styles.css - CSS file containing styles for the website
* templates - This folder contains all the HTML files
    * changepass.html
    * display.html
    * edit.html
    * inbox.html
    * index.html
    * layout.html
    * list.html
    * login.html
    * message.html
    * panel.html
    * profile.html
    * register.html
    * search.html
    * userlist.html
* app.py - Main python file, contains most of the code needed for the web app to run
* helpers.py - Helper file, includes decorators needed in app.py
* project.db - SQLite3 database containing all tables needed (comments, contents, edits, messages, options, users), stores data essential for the web app
* README.md
***

## Installation
* Download all files and folders
* Install the python libraries: flask, flask_session, flask_ckeditor, wtforms
* Type "flask run" in the terminal
***

## How to use?
* Register an account on the website
* To get admin privileges, use SQLite3 to directly alter the users table, setting the admin value to 1 for your username
* Login
* Search or use dropdown menus to find the desired article page
* From here you can click the edit button to edit
* Save edit
* Explore the website
***

## Pages

#### Index
Contains general information about Ace Racer and the wiki. Also contains a small website statistics section, showing the number of users, edits, comments and the newest user.

#### Login
Allows for user login

#### Registration
Allows user registration, passwords will be hashed and put into the db along with the username.

#### Display
Displays the article of selected item, including comments and the last editor of the article.

#### Dashboard
Shows an account summary, includes the user's number of edits, comments and level. There is also a list of all the user's comments with where it was commented. The Dashboard also allows the user to change password and log out.

#### Change password
Allows user to change password.

#### Profile
Displays profile which has the user's number of edits, comments and the user's level. Admins will have a red name, Trusted members will have a blue name and normal users will have a grey name.
There is a message button to message this user. Administrators will see a Demote/Promote button which is used to give or take away trusted level.

#### Message
Users can use this to message any other user by entering their username. If this page is accessed from clicking the message button on a user's profile, the username section will be autofilled with that user's username.

#### Inbox
Check all messages, timestamps included and quick access to the sender's profile.

#### Users
List of users, separated into 3 categories, admins, trusted and normal members. You can click on each username to quickly access their profile.

#### Content list
Accessible via the index, shows a list of all content separated into their corresponding sections. Clicking on an item will bring you to the display page of that item.

#### Search
The search function can be used on the nav bar, it will show you a list of matching items separated into 4 categories: Cars, Maps, ECUs and Users.
***
