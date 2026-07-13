import hashlib
import json
from datetime import datetime

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

# Store all locally available avatar filenames.
AVATAR_FILES = [
    "avatar-01.webp",
    "avatar-02.webp",
    "avatar-03.webp",
    "avatar-04.webp",
    "avatar-05.webp",
    "avatar-06.webp",
    "avatar-07.webp",
    "avatar-08.webp"
]


def get_avatar_filename(author):
    """Return a stable avatar filename for an author name."""

    # Remove unnecessary spaces and ignore uppercase differences.
    # casefold() also handles names containing characters such as ä or ß.
    normalized_author = author.strip().casefold()

    # Convert the normalized name into stable binary hash data.
    author_hash = hashlib.sha256(
        normalized_author.encode("utf-8")
    ).digest()

    # The first hash byte is a number between 0 and 255.
    # The modulo operation converts it into a valid list index.
    avatar_index = author_hash[0] % len(AVATAR_FILES)

    return AVATAR_FILES[avatar_index]


def get_author_initials(author):
    """Return one or two initials for the given author name."""

    # split() separates the name into its individual words.
    name_parts = author.strip().split()

    if not name_parts:
        return "?"

    # A single name uses up to its first two letters.
    if len(name_parts) == 1:
        return name_parts[0][:2].upper()

    # For multiple names, use the first and last initial.
    first_initial = name_parts[0][0]
    last_initial = name_parts[-1][0]

    return f"{first_initial}{last_initial}".upper()


def prepare_post_for_display(post):
    """Add temporary avatar data used by the HTML templates."""

    author = post.get("author", "")

    # These values are only added to the in-memory dictionary.
    # They are not written to the JSON file.
    post["avatar_filename"] = get_avatar_filename(author)
    post["author_initials"] = get_author_initials(author)


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


def get_current_timestamp():
    """Return the current local date and time in ISO format."""

    # isoformat() creates a structured timestamp.
    # timespec="minutes" removes seconds and microseconds.
    return datetime.now().isoformat(timespec="minutes")


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

    # Add the avatar filename and initials to every displayed post.
    for post in blog_posts:
        prepare_post_for_display(post)

    # Display newer posts before older posts.
    # Posts without a creation date receive an empty string and appear last.
    blog_posts.sort(
        key=lambda post: post.get("created_at", ""),
        reverse=True
    )

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


@app.route("/post/<int:post_id>")
def post_detail(post_id):
    """Display the complete details of one blog post."""

    # Load all posts from the JSON file.
    blog_posts = load_blog_posts()

    # Find the post whose ID was included in the URL.
    post = fetch_post_by_id(blog_posts, post_id)

    # Return HTTP status code 404 if the post does not exist.
    if post is None:
        return "Post not found", 404

    # Prepare the avatar filename and initials for post.html.
    prepare_post_for_display(post)

    # Pass the selected post dictionary to post.html.
    return render_template(
        "post.html",
        post=post
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
            "likes": DEFAULT_LIKES,
            "created_at": get_current_timestamp()
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

    # Load the current posts so the selected dictionary can be changed.
    blog_posts = load_blog_posts()

    # Find the post whose ID was included in the URL.
    post = fetch_post_by_id(blog_posts, post_id)

    # Return HTTP status code 404 when the post does not exist.
    if post is None:
        return "Post not found", 404

    # Older posts may not contain the likes key yet.
    current_likes = post.get("likes", DEFAULT_LIKES)

    # Increase the stored like counter by one.
    post["likes"] = current_likes + 1

    # Save the complete list containing the changed dictionary.
    save_blog_posts(blog_posts)

    # The hidden form field tells Flask where the user clicked Like.
    return_page = request.form.get("return_page", "index")

    # Return to the detail page when the Like button was clicked there.
    if return_page == "detail":
        return redirect(
            url_for(
                "post_detail",
                post_id=post_id
            )
        )

    # Otherwise return to the main blog page.
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
