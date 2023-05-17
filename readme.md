# Local Setup

- Run `pip install -r requirements.txt` to install all dependencies required to run the app mentioned in `requirements.txt` which is inside `docs` folder

# Local Developments Run

- `python3 app.py` will start the flask application in `development`. This is for running app on local system.

# Replit Run

- Add the `requirements.txt` in `poetry`
- Go to the shell and run `pip install --upgrade poetry`
- Select and open the `main.py` python file and click the Run button.
- The web app will be available at
- Format will be sort of https://..repl.co

# Folder Structure

- `project_database.sqlite3` is the sqlite database. It can be anywhere on the machine just the adjustment in path in `app.py` is required. One of the database is shipped for testing purpose.
- The application code for my app is `/`
- `static` a folder in which we have the images and css files used in the app.
  - `blogs` is the folder where blog upload imgs are stored.
  - `profile` is the folder where profile pics are stored.
- `templates` is the default folder where templates are stored

```
mad1-project/


├── app.py
├── modals.py
├── database.sqlite3
├── static
    ├──login_signup.css
    ├──mains.css
    ├──comments.css
    ├──start.css
    ├──imgs
    └──profile
       └── profile-pic
    └──blogs
       └── blog-images
├── readme.md
└── templates
   ├── blog.html
   └── comments.html
   └── edit_profile.html
   └── editblog.html
   └── followers.html
   └── following.html
   └── login.html
   └── postBlog.html
   └── postengage.html
   └── profile.html
   └── recentsPosts.html
   └── search.html
   └── start.html
   └── user_home.html
```
