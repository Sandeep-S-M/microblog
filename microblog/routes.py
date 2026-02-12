from flask import render_template,flash,redirect,url_for,request,current_app,g,jsonify
from datetime import datetime,timezone
from microblog import app,db
from microblog.error_handlers import bp
import sqlalchemy as sa
from microblog.models import User,Post
from microblog.email_utils import send_password_reset_email
from microblog.forms import LoginForm,RegisterForm ,EditProfileForm,EmptyForm,PostForm,ResetPasswordRequestForm,ResetPasswordForm,SearchForm,MessageForm
from urllib.parse import urlsplit
from flask_login import current_user,login_user,logout_user,login_required
from microblog.models import Message,Notification



@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
@login_required
def home_page():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('home_page'))

    posts = db.session.scalars(current_user.following_posts()).all()
    page = request.args.get('page', 1, type=int)
    posts = db.paginate(current_user.following_posts(), page=page,per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('home_page', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('home_page', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('home.html', title='Home', form=form,posts=posts.items, next_url=next_url,prev_url=prev_url)

@app.before_request
def before_request():
  if current_user.is_authenticated:
    current_user.last_seen = datetime.now(timezone.utc)
    db.session.commit()
    g.search_form = SearchForm()
    
@app.route('/register',methods = ['GET','POST'])
def register_page():
  if current_user.is_authenticated:
    return redirect(url_for('home_page'))
    
  form = RegisterForm()
  if form.validate_on_submit():
    user = User(username = form.username.data ,email = form.email.data)
    user.set_password(form.password.data)
    db.session.add(user)
    db.session.commit()
    flash('Congratulations ! you are successfully registered')
    return redirect(url_for('login_page'))
  return render_template('register.html',form = form)
    

@app.route('/login' ,methods = ['GET','POST'])
def login_page():
  form = LoginForm()
  if current_user.is_authenticated:
    return redirect(url_for('home_page'))
  if form.validate_on_submit():
    user = db.session.scalar(sa.select(User).where(User.username == form.username.data))
    if user is None or not user.check_password(form.password.data):
      flash("Invalid Username or Password")
      return redirect(url_for('login_page'))
    login_user(user,remember= form.remember_me.data)
    next_page = request.args.get('next')
    if not next_page or urlsplit(next_page).netloc != '':
      next_page = url_for('home_page')
    flash('you logged in Successfully as {}'.format(form.username.data))
    return redirect(next_page )
  return render_template('login.html',form = form )

@app.route('/logout')
def logout():
  logout_user()
  return redirect(url_for('home_page'))

@app.route('/user/<username>')
@login_required
def profile_page(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    page = request.args.get('page', 1, type=int)
    query = user.posts.select().order_by(Post.timestamp.desc())
    posts = db.paginate(query, page=page,
                        per_page=app.config['POSTS_PER_PAGE'],
                        error_out=False)
    next_url = url_for('profile_page', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('profile_page', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    form = EmptyForm()
    return render_template('profile.html', user=user, posts=posts.items, next_url=next_url, prev_url=prev_url, form=form)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('editprofile.html', 
                           form=form)
@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username))
        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('home_page'))
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('profile_page', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(f'You are following {username}!')
        return redirect(url_for('profile_page', username=username))
    else:
        return redirect(url_for('home_page'))
    


@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username))
        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('home_page'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('profile_page', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(f'You are not following {username}.')
        return redirect(url_for('profile_page', username=username))
    else:
        return redirect(url_for('home_page'))
      
@app.route('/explore')
@login_required
def explore_page():
    query = sa.select(Post).order_by(Post.timestamp.desc())
    posts = db.session.scalars(query).all()
    page = request.args.get('page', 1, type=int)
    query = sa.select(Post).order_by(Post.timestamp.desc())
    posts = db.paginate(query, page=page,
                        per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('explore_page', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore_page', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template("explore.html", posts=posts.items,next_url=next_url, prev_url=prev_url)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('home_page'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.email == form.email.data))
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login_page'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('home_page'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('home_page'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login_page'))
    return render_template('reset_password.html', form=form)

@app.route('/search')
@login_required
def search():
    if not current_app.elasticsearch:
        flash('Search is temporarily unavailable. Try Explore page instead.')
        return redirect(url_for('explore_page'))
    
    page = request.args.get('page', 1, type=int)
    
    # FIX 1: Create form FIRST
    form = SearchForm()
    
    # FIX 2: Use request.args['q'] instead of g.search_form
    q = request.args.get('q', '').strip()
    if not q:
        flash('Enter a search term')
        return redirect(url_for('explore_page'))
    
    posts, total = Post.search(q, page, current_app.config['POSTS_PER_PAGE'])
    
    next_url = url_for('search', q=q, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('search', q=q, page=page - 1) \
        if page > 1 else None
    
    return render_template('search.html', 
                         title='Search', 
                         posts=posts,
                         next_url=next_url, 
                         prev_url=prev_url)

@app.route('/api/chat_updates/<username>')
@login_required
def chat_updates(username):
    recipient = db.first_or_404(sa.select(User).where(User.username == username))
    last_timestamp = request.args.get('timestamp', 0.0, type=float)
    
    # Fetch messages sent AFTER the last timestamp
    query = sa.select(Message).where(
        sa.or_(
            sa.and_(Message.sender_id == current_user.id, Message.recipient_id == recipient.id),
            sa.and_(Message.sender_id == recipient.id, Message.recipient_id == current_user.id)
        ),
        Message.timestamp > datetime.fromtimestamp(last_timestamp, timezone.utc)
    ).order_by(Message.timestamp.asc())
    
    messages = db.session.scalars(query).all()
    
    updates = []
    for msg in messages:
        # ✅ FIXED: Include UNIQUE message ID to prevent duplicates
        updates.append({
            'id': msg.id,  # ← CRITICAL: Unique message ID for frontend dedup
            'html': render_template('_message.html', msg=msg),
            'timestamp': msg.timestamp.replace(tzinfo=timezone.utc).timestamp()
        })
    
    return jsonify({'updates': updates})  # ← jsonify() for proper JSON response


@app.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
    user = db.first_or_404(sa.select(User).where(User.username == recipient))
    form = MessageForm()
    
    if form.validate_on_submit():
        msg = Message(author=current_user, recipient=user,
                      body=form.message.data)
        user.add_notification('unread_message_count',
                              user.unread_message_count())
        db.session.add(msg)
        db.session.commit()
        # Scroll to bottom after sending
        return redirect(url_for('send_message', recipient=recipient, _anchor='bottom'))
    
    # Fetch conversation history: (Me -> Them) OR (Them -> Me)
    query = sa.select(Message).where(
        sa.or_(
            sa.and_(Message.sender_id == current_user.id, Message.recipient_id == user.id),
            sa.and_(Message.sender_id == user.id, Message.recipient_id == current_user.id)
        )
    ).distinct().order_by(Message.timestamp.asc())
    
    messages = db.session.scalars(query).all()
    
    # Mark messages from them as read
    current_user.last_message_read_time = datetime.now(timezone.utc)
    current_user.add_notification('unread_message_count', 0)
    db.session.commit()

    return render_template('chat.html', title=f'Chat with {recipient}', form=form, recipient=user, messages=messages)
    
@app.route('/messages')
@login_required
def messages():
    current_user.last_message_read_time = datetime.now(timezone.utc)
    current_user.add_notification('unread_message_count', 0)
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    # GROUP BY sender_id to show only the latest message from each user
    subquery = sa.select(
        Message.sender_id,
        sa.func.max(Message.timestamp).label('last_message_time')
    ).where(Message.recipient_id == current_user.id).group_by(Message.sender_id).subquery()

    query = sa.select(Message).join(
        subquery,
        sa.and_(
            Message.sender_id == subquery.c.sender_id,
            Message.timestamp == subquery.c.last_message_time
        )
    ).order_by(Message.timestamp.desc())

    messages = db.paginate(query, page=page,
                           per_page=current_app.config['POSTS_PER_PAGE'],
                           error_out=False)
    next_url = url_for('messages', page=messages.next_num) \
        if messages.has_next else None
    prev_url = url_for('messages', page=messages.prev_num) \
        if messages.has_prev else None
    return render_template('messages.html', messages=messages, next_url=next_url, prev_url=prev_url)

@app.route('/notifications')
@login_required
def notifications():
    since = request.args.get('since', 0.0, type=float)
    query = current_user.notifications.select().where(
        Notification.timestamp > since).order_by(Notification.timestamp.asc())
    notifications = db.session.scalars(query)
    return [{
        'name': n.name,
        'data': n.get_data(),
        'timestamp': n.timestamp
    } for n in notifications]