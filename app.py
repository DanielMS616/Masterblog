import json

from flask import Flask, render_template


# Create the Flask application object.
# __name__ tells Flask where the current application module is located.
app = Flask(__name__)

# Store the filename in one place so all functions use the same file.
BLOG_POSTS_FILE = "blog_posts.json"


def load_blog_posts():
    """Load and return all blog posts from the JSON file."""

    # Open the JSON file in read mode.
    # json.load() converts the JSON data into Python objects.
    with open(BLOG_POSTS_FILE, "r", encoding="utf-8") as file:
        blog_posts = json.load(file)

    return blog_posts


def save_blog_posts(blog_posts):
    """Save the complete list of blog posts to the JSON file."""

    # Open the JSON file in write mode.
    # json.dump() converts the Python list into JSON and writes it
    # into the file. indent=4 keeps the file readable for humans.
    with open(BLOG_POSTS_FILE, "w", encoding="utf-8") as file:
        json.dump(blog_posts, file, indent=4)


@app.route("/")
def index():
    """Display all blog posts on the home page."""

    # Load the current data from the JSON file whenever the home page
    # is requested. This ensures that the page shows the latest posts.
    blog_posts = load_blog_posts()

    # Pass the list to index.html under the template name "posts".
    return render_template("index.html", posts=blog_posts)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4999, debug=True)