#SciVerse\routes.py
import os
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from werkzeug.utils import secure_filename
from flask_login import login_user, logout_user, login_required, current_user
from SciVerse.ext import db, bcrypt, login_manager
from SciVerse.utils import allowed_file
from SciVerse.models import User, Book, Comment, Cart, Order, OrderItem, Like
from SciVerse.forms import RegisterForm, LoginForm, BookForm, CommentForm, AddressForm

bp = Blueprint('routes', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#@bp.before_app_first_request
#def create_main_user():
 #   if not User.query.filter_by(username='mainuser').first():
 #       hashed_pw = bcrypt.generate_password_hash('mainuserpass').decode('utf-8')
 #       admin = User(username='mainuser', email='mainuserann@book.com', password=hashed_pw, is_admin=True)
  #      db.session.add(admin)
 #       db.session.commit()

@bp.route('/')
def index():
    books = Book.query.all()
    return render_template('index.html', books=books)



@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        filename = 'default.png'

        if form.profile_pic.data and allowed_file(form.profile_pic.data.filename):
            filename = secure_filename(form.profile_pic.data.filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']
            
            # ✅ Create folder if it doesn't exist
            os.makedirs(upload_folder, exist_ok=True)

            # ✅ Save the file
            form.profile_pic.data.save(os.path.join(upload_folder, filename))

        user = User(
            username=form.username.data,
            email=form.email.data,
            phone=form.phone.data,
            profile_pic=filename,
            password=hashed_pw
        )
        db.session.add(user)
        db.session.commit()
        flash('Account created. You can now log in.', 'success')
        return redirect(url_for('routes.login'))

    return render_template('register.html', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Login successful', 'success')
            return redirect(url_for('routes.index'))
        else:
            flash('Login failed. Check email and password.', 'danger')
    return render_template('login.html', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('routes.index'))

@bp.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    if not current_user.is_admin:
        flash("You don't have permission.", 'danger')
        return redirect(url_for('routes.index'))
    form = BookForm()
    if form.validate_on_submit():
        filename = 'default_book.jpg'
        if form.image_file.data:
            filename = secure_filename(form.image_file.data.filename)
            upload_folder = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])
            os.makedirs(upload_folder, exist_ok=True)
            form.image_file.data.save(os.path.join(upload_folder, filename))

        book = Book(title=form.title.data, description=form.description.data, image_file=filename)
        db.session.add(book)
        db.session.commit()
        flash('Book added.', 'success')
        return redirect(url_for('routes.index'))
    return render_template('add_book.html', form=form)

@bp.route('/book/<int:book_id>', methods=['GET', 'POST'])
def view_book(book_id):
    book = Book.query.get_or_404(book_id)
    form = CommentForm()
    if form.validate_on_submit() and current_user.is_authenticated:
        comment = Comment(content=form.content.data, author=current_user, book=book)
        db.session.add(comment)
        db.session.commit()
        flash('Comment added.', 'success')
        return redirect(url_for('routes.view_book', book_id=book_id))
    return render_template('book_detail.html', book=book, form=form)

@bp.route('/delete_comment/<int:comment_id>')
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.author != current_user and not current_user.is_admin:
        flash("You can only delete your own comments.", 'danger')
        return redirect(url_for('routes.index'))
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted.', 'info')
    return redirect(request.referrer)

@bp.route('/cart')
@login_required
def cart():
    if not current_user.address:
        flash('Please set your address first.', 'warning')
        return redirect(url_for('routes.set_address'))
    items = Cart.query.filter_by(user_id=current_user.id).all()
    return render_template('cart.html', items=items)

@bp.route('/add_to_cart/<int:book_id>', methods=['POST'])
@login_required
def add_to_cart(book_id):
    if not current_user.address:
        flash('Add your address before placing orders.', 'warning')
        return redirect(url_for('routes.set_address'))

    existing_item = Cart.query.filter_by(user_id=current_user.id, book_id=book_id).first()
    if existing_item:
        flash('This book is already in your cart.', 'info')
    else:
        cart_item = Cart(user_id=current_user.id, book_id=book_id)
        db.session.add(cart_item)
        db.session.commit()
        flash('Book added to cart.', 'success')

    return redirect(url_for('routes.cart'))

@bp.route('/delete_from_cart/<int:item_id>')
@login_required
def delete_from_cart(item_id):
    item = Cart.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        flash('Not allowed.', 'danger')
        return redirect(url_for('routes.cart'))
    db.session.delete(item)
    db.session.commit()
    flash('Item removed from cart.', 'info')
    return redirect(url_for('routes.cart'))

@bp.route('/set_address', methods=['GET', 'POST'])
@login_required
def set_address():
    form = AddressForm()
    if form.validate_on_submit():
        current_user.address = form.address.data
        db.session.commit()
        flash('Address saved.', 'success')
        return redirect(url_for('routes.cart'))
    return render_template('set_address.html', form=form)

@bp.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('routes.index'))
    recent_comments = Comment.query.order_by(Comment.timestamp.desc()).limit(10).all()
    return render_template('admin_dashboard.html', comments=recent_comments)

@bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    if not current_user.address:
        flash('Please provide an address before checkout.', 'warning')
        return redirect(url_for('routes.set_address'))
    if not cart_items:
        flash('Cart is empty.', 'info')
        return redirect(url_for('routes.cart'))
    order = Order(user_id=current_user.id)
    db.session.add(order)
    db.session.flush()
    for item in cart_items:
        order_item = OrderItem(order_id=order.id, book_id=item.book_id)
        db.session.add(order_item)
        db.session.delete(item)
    db.session.commit()
    flash('Order placed successfully!', 'success')
    return redirect(url_for('routes.index'))

@bp.route('/like_comment/<int:comment_id>')
@login_required
def like_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.liked_by_user(current_user):
        flash("Already liked.", "info")
    else:
        like = Like(user_id=current_user.id, comment_id=comment.id)
        db.session.add(like)
        db.session.commit()
    return redirect(request.referrer or url_for('routes.index'))

@bp.route('/unlike_comment/<int:comment_id>')
@login_required
def unlike_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    like = Like.query.filter_by(user_id=current_user.id, comment_id=comment.id).first()
    if like:
        db.session.delete(like)
        db.session.commit()
    return redirect(request.referrer or url_for('routes.index'))

@bp.route('/orders')
@login_required
def orders():
    user_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.timestamp.desc()).all()
    return render_template('orders.html', orders=user_orders)

@bp.route('/search')
def search():
    query = request.args.get('q', '')
    if query:
        books = Book.query.filter(Book.title.ilike(f'%{query}%')).all()
    else:
        books = []
    return render_template('search.html', books=books, query=query)

@bp.route('/books')
@bp.route('/books/page/<int:page>')
def paginated_books(page=1):
    per_page = 6
    pagination = Book.query.paginate(page=page, per_page=per_page)
    return render_template('paginated_books.html', pagination=pagination)
