from flask import redirect, render_template, request, session
from app import app
from werkzeug.security import check_password_hash, generate_password_hash
import users
import messages
import boards
import threads


@app.route('/')
def hello_world():
    return redirect("/boards")


@app.route('/register', methods=["GET"])
def register_form():
    return render_template("register.html")


@app.route('/register', methods=["POST"])
def do_register():
    username = request.form["username"]
    password_hash = generate_password_hash(request.form["password"])
    result = users.create(username, password_hash)
    session["uid"] = result["uid"]
    session["username"] = username
    return redirect("/boards")


@app.route('/login', methods=["GET"])
def index():
    return render_template("login.html")


@app.route('/login', methods=["POST"])
def do_login():
    username = request.form["username"]
    user = users.get_by_username(username)
    if user is not None and check_password_hash(user.password, request.form["password"]):
        uid = user.id
        session["uid"] = uid
        session["username"] = username
        return redirect("/boards")
    else:
        return redirect("/login")


@app.route('/boards', methods=["GET"])
def show_boards():
    if "uid" not in session:
        return redirect("/login")
    return render_template("boards.html", boards=boards.all(), users=users.all())


@app.route('/boards', methods=["POST"])
def create_board():
    board_id = boards.create(
        request.form["board_name"],
        request.form["is-secret"] is not None,
        request.form.getlist('secret-board-user'))
    return redirect("/boards/" + str(board_id))


@app.route('/boards/<int:board_id>', methods=["GET"])
def show_board(board_id):
    return render_template("board.html", board=boards.get(board_id))


@app.route('/boards/<int:board_id>/delete', methods=["GET"])
def delete_board(board_id):
    boards.delete(board_id)
    return redirect("/boards")


@app.route('/boards/<int:board_id>/threads', methods=["POST"])
def create_thread(board_id):
    thread_id = threads.create(request.form["name"], request.form["content"], board_id, session["uid"])
    return redirect("/threads/" + str(thread_id))


@app.route('/threads/<int:thread_id>', methods=["GET"])
def show_thread(thread_id):
    thread = threads.get(thread_id)
    created_by_me = session["uid"] == thread["created_by"]
    return render_template("thread.html", thread=thread, created_by_me=created_by_me)


@app.route('/threads/<int:thread_id>', methods=["POST"])
def post_message(thread_id):
    messages.create(request.form["content"], thread_id, session["uid"])
    return redirect("/threads/" + str(thread_id))


@app.route('/threads/<int:thread_id>/name', methods=["POST"])
def edit_thread_name(thread_id):
    threads.rename(thread_id, request.form["name"])
    return redirect("/threads/" + str(thread_id))


@app.route('/threads/<int:thread_id>/delete', methods=["POST"])
def delete_thread(thread_id):
    board_id = threads.delete(thread_id)
    return redirect("/boards/" + str(board_id))


@app.route('/messages/<int:message_id>/delete', methods=["POST"])
def delete_message(message_id):
    thread_id = messages.delete(message_id)
    return redirect("/threads/" + thread_id)


@app.route('/messages/<int:message_id>/content', methods=["POST"])
def update_message(message_id):
    thread_id = messages.update(message_id, request.form["content"])
    return redirect("/threads/" + str(thread_id))


@app.route('/search', methods=["GET"])
def search():
    search_term = request.args.get("term")
    return render_template("search_results.html", search_term=search_term, messages=messages.search(search_term))


@app.route("/logout")
def logout():
    if "username" in session:
        del session["username"]
    if "uid" in session:
        del session["uid"]
    return redirect("/login")
