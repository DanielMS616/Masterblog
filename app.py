import json

from flask import Flask, redirect, render_template, request, url_for


# Create the Flask application object.
# __name__ tells Flask where the current application module is located.
app = Flask(__name__)

# Store the filename in one place so all functions use the same file.
BLOG_POSTS_FILE = "blog_posts.json"

# Older posts may not have a category yet.
DEFAULT_CATEGORY = "Uncategorized"

# Posts created before the like feature may not contain this key.
DEFAULT_LIKES = 0

# Store the available categories in one place.
# The same list is used by the index, add, and update templates.
CATEGORIES = [
    "Python",
    "Flask",
    "AI",
    "Automation",
    "Projects",
    "Personal",
    DEFAULT_CATEGORY
]


def load_blog_posts():
    """Load and return all blog posts from the JSON file."""

    # json.load() converts the JSON array into a Python list
    # containing one dictionary for each blog post.
    with open(BLOG_POSTS_FILE, "r", encoding="utf-8") as file:
        blog_posts = json.load(file)

    return blog_posts


def save_blog_posts(blog_posts):
    """Save the complete list of blog posts to the JSON file."""

    # json.dump() converts the Python list back into JSON.
    # indent=4 keeps the file readable for humans.
    with open(BLOG_POSTS_FILE, "w", encoding="utf-8") as file:
        json.dump(blog_posts, file, indent=4)


def get_next_id(blog_posts):
    """Return the next available ID for a new blog post."""

    # Start with 1 so the first post receives ID 1.
    next_id = 1

    # Move next_id behind the largest ID found in the list.
    for post in blog_posts:
        if post["id"] >= next_id:
            next_id = post["id"] + 1

    return next_id


def fetch_post_by_id(blog_posts, post_id):
    """Return the blog post with the given ID or None."""

    # Search every post dictionary for the requested ID.
    for post in blog_posts:
        if post["id"] == post_id:
            return post

    # None shows that no matching post was found.
    return None


@app.route("/")
def index():
    """Display posts matching the search and category filters."""

    # Load the latest posts whenever the home page is requested.
    blog_posts = load_blog_posts()

    # Read the optional filters from the URL query string.
    search_query = request.args.get("search", "").strip()
    selected_category = request.args.get("category", "").strip()

    # Filter by author, title, content, or category.
    if search_query:
        matching_posts = []
        search_text = search_query.lower()

        for post in blog_posts:
            author = post["author"].lower()
            title = post["title"].lower()
            content = post["content"].lower()

            # get() returns the fallback category when an older post
            # does not yet contain the "category" key.
            category = post.get(
                "category",
                DEFAULT_CATEGORY
            ).lower()

            if (
                search_text in author
                or search_text in title
                or search_text in content
                or search_text in category
            ):
                matching_posts.append(post)

        # Only the matching posts are displayed.
        # The JSON file itself is not changed.
        blog_posts = matching_posts

    # Apply the category filter after the text search.
    if selected_category:
        category_posts = []

        for post in blog_posts:
            post_category = post.get(
                "category",
                DEFAULT_CATEGORY
            )

            if post_category == selected_category:
                category_posts.append(post)

        blog_posts = category_posts

    # Pass the posts, filter values, and available categories
    # to the index template.
    return render_template(
        "index.html",
        posts=blog_posts,
        search_query=search_query,
        selected_category=selected_category,
        categories=CATEGORIES
    )


@app.route("/add", methods=["GET", "POST"])
def add():
    """Display the form or save a newly submitted blog post."""

    # A POST request means that the add form was submitted.
    if request.method == "POST":
        # These keys match the name attributes in add.html.
        author = request.form.get("author")
        title = request.form.get("title")
        content = request.form.get("content")
        category = (
            request.form.get("category")
            or DEFAULT_CATEGORY
        )

        # Load the current posts before adding a new one.
        blog_posts = load_blog_posts()

        # Create one new post dictionary.
        new_post = {
            "id": get_next_id(blog_posts),
            "author": author,
            "title": title,
            "content": content,
            "category": category,
            "likes": DEFAULT_LIKES
        }

        blog_posts.append(new_post)
        save_blog_posts(blog_posts)

        return redirect(url_for("index"))

    # A GET request displays the empty form.
    return render_template(
        "add.html",
        categories=CATEGORIES
    )


@app.route("/delete/<int:post_id>")
def delete(post_id):
    """Delete the blog post with the given ID."""

    blog_posts = load_blog_posts()
    post_to_delete = fetch_post_by_id(blog_posts, post_id)

    # Return HTTP status code 404 when the post does not exist.
    if post_to_delete is None:
        return "Post not found", 404

    # Remove the complete dictionary and save the changed list.
    blog_posts.remove(post_to_delete)
    save_blog_posts(blog_posts)

    return redirect(url_for("index"))


@app.route("/like/<int:post_id>", methods=["POST"])
def like(post_id):
    """Increase the like counter of the selected blog post."""

    # Load the current list so the stored JSON data can be changed.
    blog_posts = load_blog_posts()

    # Find the post whose ID was included in the dynamic URL.
    post = fetch_post_by_id(blog_posts, post_id)

    # Return HTTP status code 404 when the requested post does not exist.
    if post is None:
        return "Post not found", 404

    # Older posts may not have a "likes" key yet.
    # get() returns 0 in that case.
    current_likes = post.get("likes", DEFAULT_LIKES)

    # Increase the stored number by one.
    post["likes"] = current_likes + 1

    # Save the complete list containing the changed post dictionary.
    save_blog_posts(blog_posts)

    # Return to the home page so the new counter becomes visible.
    return redirect(url_for("index"))


@app.route("/update/<int:post_id>", methods=["GET", "POST"])
def update(post_id):
    """Display or process the form for updating a blog post."""

    blog_posts = load_blog_posts()
    post = fetch_post_by_id(blog_posts, post_id)

    if post is None:
        return "Post not found", 404

    # Add a fallback category for older JSON entries.
    if "category" not in post:
        post["category"] = DEFAULT_CATEGORY

    # A POST request means that the update form was submitted.
    if request.method == "POST":
        author = request.form.get("author")
        title = request.form.get("title")
        content = request.form.get("content")
        category = (
            request.form.get("category")
            or DEFAULT_CATEGORY
        )

        # Update the existing dictionary.
        # The ID remains unchanged.
        post["author"] = author
        post["title"] = title
        post["content"] = content
        post["category"] = category

        save_blog_posts(blog_posts)

        return redirect(url_for("index"))

    # A GET request displays the current values in the form.
    return render_template(
        "update.html",
        post=post,
        categories=CATEGORIES
    )


if __name__ == "__main__":
    # Start the Flask development server on port 4999.
    app.run(host="0.0.0.0", port=4999, debug=True)
