import json

from flask import Flask, redirect, render_template, request, url_for


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


def get_next_id(blog_posts):
    """Return the next available ID for a new blog post."""

    # Start with ID 1. This is also the correct ID when the list
    # of blog posts is currently empty.
    next_id = 1

    # Check every existing blog post.
    # If a post uses next_id or a larger number, move next_id
    # to the number directly after that post's ID.
    for post in blog_posts:
        if post["id"] >= next_id:
            next_id = post["id"] + 1

    return next_id


@app.route("/")
def index():
    """Display all blog posts on the home page."""

    # Load the current data from the JSON file whenever the home page
    # is requested. This ensures that the page shows the latest posts.
    blog_posts = load_blog_posts()

    # Pass the list to index.html under the template name "posts".
    return render_template("index.html", posts=blog_posts)


@app.route("/add", methods=["GET", "POST"])
def add():
    """Display the form or save a newly submitted blog post."""

    # A POST request means that the user submitted the HTML form.
    if request.method == "POST":
        # request.form contains the values submitted by the form.
        # The keys must match the name attributes in add.html.
        author = request.form.get("author")
        title = request.form.get("title")
        content = request.form.get("content")

        # Load all currently stored posts before adding a new one.
        blog_posts = load_blog_posts()

        # Create a new dictionary using the submitted form values.
        # get_next_id() ensures that the new post receives a unique ID.
        new_post = {
            "id": get_next_id(blog_posts),
            "author": author,
            "title": title,
            "content": content
        }

        # Add the new post to the Python list.
        blog_posts.append(new_post)

        # Save the complete updated list back to the JSON file.
        save_blog_posts(blog_posts)

        # Redirect the browser to the index route after saving.
        # url_for("index") creates the URL belonging to index().
        return redirect(url_for("index"))

    # A GET request displays the form for creating a new post.
    return render_template("add.html")


@app.route("/delete/<int:post_id>")
def delete(post_id):
    """Delete the blog post with the given ID."""

    # Load the current blog posts directly from the JSON file.
    blog_posts = load_blog_posts()

    # Start with no selected post. If a matching ID is found,
    # this variable will contain the corresponding dictionary.
    post_to_delete = None

    # Check every blog-post dictionary until the requested ID is found.
    for post in blog_posts:
        if post["id"] == post_id:
            post_to_delete = post
            break

    # Return an HTTP 404 response if no post has the requested ID.
    if post_to_delete is None:
        return "Post not found", 404

    # Remove the complete post dictionary from the Python list.
    blog_posts.remove(post_to_delete)

    # Save the changed list back to the JSON file so the deletion
    # remains permanent after the application restarts.
    save_blog_posts(blog_posts)

    # Redirect the browser to the index page after deleting the post.
    return redirect(url_for("index"))


if __name__ == "__main__":
    # Start the Flask development server on port 4999.
    app.run(host="0.0.0.0", port=4999, debug=True)
