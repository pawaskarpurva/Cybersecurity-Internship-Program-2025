from flask import Flask, request, redirect, render_template_string
import sqlite3, string, random

app = Flask(__name__)

# Step 1: Create database if not exists
def init_db():
    conn = sqlite3.connect("urls.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS urls
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  slug TEXT UNIQUE,
                  original_url TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Step 2: Function to make a random short code
def generate_slug(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# Step 3: HTML form
form_html = """
<h2>URL Shortener</h2>
<form method="POST">
    <input type="url" name="url" placeholder="Enter long URL" required>
    <button type="submit">Shorten</button>
</form>
{% if short_url %}
<p>Short URL: <a href="{{ short_url }}">{{ short_url }}</a></p>
{% endif %}
"""

# Step 4: Home page (form)
@app.route("/", methods=["GET", "POST"])
def index():
    short_url = None
    if request.method == "POST":
        original_url = request.form["url"]
        slug = generate_slug()
        
        conn = sqlite3.connect("urls.db")
        c = conn.cursor()
        c.execute("INSERT INTO urls (slug, original_url) VALUES (?, ?)", (slug, original_url))
        conn.commit()
        conn.close()
        
        short_url = request.host_url + slug
    return render_template_string(form_html, short_url=short_url)

# Step 5: Redirect short code to long URL
@app.route("/<slug>")
def redirect_url(slug):
    conn = sqlite3.connect("urls.db")
    c = conn.cursor()
    c.execute("SELECT original_url FROM urls WHERE slug = ?", (slug,))
    row = c.fetchone()
    conn.close()
    if row:
        return redirect(row[0])
    return "URL not found", 404

if __name__ == "__main__":
    app.run(debug=True)
    
