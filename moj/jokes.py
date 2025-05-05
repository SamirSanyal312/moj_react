from flask import Blueprint, render_template, request, redirect, url_for, flash, g, abort
from moj.db import get_db
from moj.auth import login_required
from moj.roles import role_required
from moj import log_function

bp = Blueprint('jokes', __name__, url_prefix='/joke')


@bp.route('/')
@login_required
@role_required("user","moderator")
def index():
    db = get_db()
    jokes = db.execute(
        '''
        SELECT j.id, title, body, created, nickname
        FROM joke j
        JOIN user u ON j.author_id = u.id
        WHERE j.author_id = ?
        ORDER BY created DESC
        ''',
        (g.user['id'],)
    ).fetchall()
    return render_template('jokes/index.html', jokes=jokes)


@bp.route('/leave', methods=('GET', 'POST'))
@login_required
@role_required("user")
def leave():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        db = get_db()
        error = None

        if not title:
            error = 'Title is required.'
        elif len(title.split()) > 10:
            error = 'Title must be no more than 10 words.'
        elif db.execute(
            'SELECT id FROM joke WHERE title = ? AND author_id = ?', (
                title, g.user['id'])
        ).fetchone():
            error = 'You already used this title.'

        if error is None:
            db.execute(
                'INSERT INTO joke (title, body, author_id) VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.execute(
                'UPDATE user SET joke_balance = joke_balance + 1 WHERE id = ?',
                (g.user['id'],)
            )
            db.commit()
            flash('Joke added successfully!')
            return redirect(url_for('jokes.index'))

        flash(error)

    return render_template('jokes/leave.html')


@bp.route('/take', methods=('GET', 'POST'))
@login_required
@role_required("user")
def take_joke():
    db = get_db()

    jokes = db.execute(
        '''
        SELECT j.id, j.title, u.nickname, 
            COALESCE(AVG(r.score), 0) AS avg_rating,
            CASE WHEN tj.joke_id IS NOT NULL THEN 1 ELSE 0 END AS is_taken
        FROM joke j
        JOIN user u ON j.author_id = u.id
        LEFT JOIN rating r ON j.id = r.joke_id
        LEFT JOIN taken_jokes tj ON j.id = tj.joke_id AND tj.user_id = ?
        WHERE j.author_id != ?
        GROUP BY j.id, j.title, u.nickname        
        ORDER BY avg_rating DESC
        ''',
        (g.user['id'], g.user['id'])
    ).fetchall()

    if request.method == 'POST':
        joke_id = request.form['joke_id']
        db = get_db()

        if g.user['joke_balance'] <= 0:
            flash('You need to leave a joke first!')
            return redirect(url_for('jokes.index'))

        taken_joke = db.execute(
            'SELECT 1 FROM taken_jokes WHERE user_id = ? AND joke_id = ?',
            (g.user['id'], joke_id)
        ).fetchone()

        if taken_joke:
            flash('You have already taken this joke!')
        else:
            db.execute(
                'INSERT INTO taken_jokes (user_id, joke_id) VALUES (?, ?)',
                (g.user['id'], joke_id)
            )
            db.execute(
                'UPDATE user SET joke_balance = joke_balance - 1 WHERE id = ?',
                (g.user['id'],)
            )
            db.commit()
            flash('You have successfully taken this joke!')

        return redirect(url_for('jokes.index'))

    return render_template('jokes/take.html', jokes=jokes)


@bp.route('/view/<int:joke_id>', methods=('GET', 'POST'))
@login_required
@role_required("user","moderator")
def view_joke(joke_id):
    db = get_db()

    # Fetch the joke with avg rating
    log_function(f"Joke viewed: {id}")
    joke = db.execute(
        '''
        SELECT j.id, j.title, j.body, j.created, u.nickname, j.author_id,
               COALESCE(ROUND(AVG(r.score), 2), 0) AS avg_rating
        FROM joke j
        JOIN user u ON j.author_id = u.id
        LEFT JOIN rating r ON j.id = r.joke_id
        WHERE j.id = ?
        GROUP BY j.id, j.title, j.body, j.created, u.nickname
        ''',
        (joke_id,)
    ).fetchone()

    if joke is None:
        flash('Joke not found.')
        return redirect(url_for('jokes.index'))

    #is_author = g.user['id'] == joke['author_id']
    user_role = g.user['role']
    is_author = g.user['id'] == joke['author_id']
    is_moderator = user_role == 'moderator'

    # Handle all form submissions
    if request.method == 'POST':
        action = request.form.get('action')

        if is_author or is_moderator:
            if action == 'update':
                new_body = request.form['body']
                db.execute('UPDATE joke SET body = ? WHERE id = ?',
                           (new_body, joke_id))
                db.commit()
                flash('Joke updated successfully!')
                return redirect(url_for('jokes.view_joke', joke_id=joke_id))

            elif action == 'delete':
                db.execute('DELETE FROM joke WHERE id = ?', (joke_id,))
                db.commit()
                flash('Joke deleted.')
                # return redirect(url_for('jokes.my_jokes'))
                # ✅ correct, since you used endpoint='my'
                return redirect(url_for('jokes.my'))

        elif action == 'rate' and 'rating' in request.form:
            score = int(request.form['rating'])
            existing_rating = db.execute(
                'SELECT id FROM rating WHERE joke_id = ? AND user_id = ?',
                (joke_id, g.user['id'])
            ).fetchone()

            if existing_rating:
                db.execute('UPDATE rating SET score = ? WHERE id = ?',
                           (score, existing_rating['id']))
                flash('Your rating has been updated!')
            else:
                db.execute('INSERT INTO rating (joke_id, user_id, score) VALUES (?, ?, ?)',
                           (joke_id, g.user['id'], score))
                flash('Your rating has been submitted!')
            db.commit()

            # Refresh joke
            joke = db.execute(
                '''
                SELECT j.id, j.title, j.body, j.created, u.nickname, j.author_id,
                       COALESCE(ROUND(AVG(r.score), 2), 0) AS avg_rating
                FROM joke j
                JOIN user u ON j.author_id = u.id
                LEFT JOIN rating r ON j.id = r.joke_id
                WHERE j.id = ?
                GROUP BY j.id, j.title, j.body, j.created, u.nickname
                ''',
                (joke_id,)
            ).fetchone()

    # First-time viewer joke balance logic
    if not is_author:
        already_viewed = db.execute(
            'SELECT 1 FROM taken_jokes WHERE user_id = ? AND joke_id = ?',
            (g.user['id'], joke_id)
        ).fetchone()

        if not already_viewed:
            if g.user['joke_balance'] > 0:
                db.execute(
                    'INSERT INTO taken_jokes (user_id, joke_id) VALUES (?, ?)', (g.user['id'], joke_id))
                db.execute(
                    'UPDATE user SET joke_balance = joke_balance - 1 WHERE id = ?', (g.user['id'],))
                db.commit()
            else:
                flash('Not enough joke balance to view this joke!')
                return redirect(url_for('jokes.my'))

    return render_template('jokes/view.html', joke=joke, is_author=is_author, avg_rating=joke['avg_rating'])


@bp.route('/my', endpoint='my')
@login_required
@role_required("user", "moderator")
def my_jokes():
    db = get_db()
    jokes = db.execute(
        '''
        SELECT j.id, j.title, j.body, j.created,
               COALESCE(ROUND(AVG(r.score), 2), 0) AS avg_rating
        FROM joke j
        LEFT JOIN rating r ON j.id = r.joke_id
        WHERE j.author_id = ?
        GROUP BY j.id
        ORDER BY j.created DESC
        ''',
        (g.user['id'],)
    ).fetchall()
    return render_template('jokes/my.html', jokes=jokes)


@bp.route('/all')
@login_required
def all_jokes():
    db = get_db()
    jokes = db.execute(
        '''
        SELECT j.id, j.title, u.nickname,
        COALESCE(ROUND(AVG(r.score), 2), 'N/A') AS avg_rating
        FROM joke j
        JOIN user u ON j.author_id = u.id
        LEFT JOIN rating r ON j.id = r.joke_id
        WHERE j.author_id != ?
        GROUP BY j.id, j.title, u.nickname
        ORDER BY j.created DESC
        ''',
        (g.user['id'],)
    ).fetchall()
    return render_template('jokes/all.html', jokes=jokes)

@bp.route('/rbac-check')
@role_required('user')
def rbac_check():
    return "✅ You have the 'user' role!"


