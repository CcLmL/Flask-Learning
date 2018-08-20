from flask import Flask, request, render_template, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

#  设置数据库连接地址
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:mysql@127.0.0.1:3306/flask01"

#  是否设置追踪数据库修改（会占用一定的内存，不建议开启）
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

#  是否打印底层执行的SQL语句
app.config["SQLALCHEMY_ECHO"] = True


#  创建数据库连接对象
db = SQLAlchemy(app)


class Author(db.Model):
    __tablename__ = "authors"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    books = db.relationship("Book", backref="author")


class Book(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    author_id = db.Column(db.Integer, db.ForeignKey("authors.id"))


#  主逻辑
@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "GET":
        authors = Author.query.all()
        return render_template("book_test.html",authors=authors)

    author_name = request.form.get("author_name")
    book_name = request.form.get("book_name")

    if not all([author_name,book_name]):
        flash("数据不完整")
        return redirect(url_for("index"))

    author = Author.query.filter_by(name=author_name).first()

    if author:
        book = Book.query.filter_by(name=book_name, author_id=author.id).first()
        if book in author.books:
            flash("该书籍已经存在")
            return redirect(url_for("index"))
        else:
            new_book = Book(name=book_name)
            author.books.append(new_book)
            try:
                db.session.add(new_book)
                db.session.commit()
            except Exception as e:
                flash("数据库查询失败 %s" % e)
                return redirect(url_for("index"))
    else:
        new_book = Book(name=book_name)
        new_author = Author(name=author_name)
        new_author.books.append(new_book)
        db.session.add_all([new_book,new_author])
        db.session.commit()

    return redirect(url_for("index"))


@app.route('/delete_book/<int:book_id>')
def delete_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        flash("该书籍不存在")
        return redirect(url_for("index"))

    db.session.delete(book)
    db.session.commit()
    return redirect(url_for("index"))


@app.route('/delete_author/<int:author_id>')
def delete_author(author_id):
    author = Author.query.get(author_id)
    if not author:
        flash("该作者不存在")
        return redirect(url_for("index"))

    # 先删除多的，在删除少的
    Book.query.filter_by(author_id=author.id).delete()
    db.session.delete(author)
    db.session.commit()

    return redirect(url_for("index"))


if __name__ == '__main__':
    db.drop_all()
    db.create_all()

    # 生成数据
    au1 = Author(name='老王')
    au2 = Author(name='老尹')
    au3 = Author(name='老刘')
    # 把数据提交给用户会话
    db.session.add_all([au1, au2, au3])
    # 提交会话
    db.session.commit()
    bk1 = Book(name='老王回忆录', author_id=au1.id)
    bk2 = Book(name='我读书少，你别骗我', author_id=au1.id)
    bk3 = Book(name='如何才能让自己更骚', author_id=au2.id)
    bk4 = Book(name='怎样征服美丽少女', author_id=au3.id)
    bk5 = Book(name='如何征服英俊少男', author_id=au3.id)
    # 把数据提交给用户会话
    db.session.add_all([bk1, bk2, bk3, bk4, bk5])
    # 提交会话
    db.session.commit()

    app.run(debug=True)

    # 哈哈哈哈哈哈啊啊啊啊啊啊啊啊
