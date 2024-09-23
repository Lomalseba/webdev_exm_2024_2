from flask import render_template, request, redirect, url_for, flash, session, Blueprint
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from uuid import uuid4
import hashlib
import os

from app import app, db
from query import queries
from .auth import checkRole
from .sanitaizer import sanitaizer_text

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/delete_bot/<int:bot_id>', methods=['GET', 'POST'])
@login_required
@checkRole("delete")
def delete_bot(bot_id):
    print(f"вы зашли на сраницу удалить бота {bot_id}")
    try:
        with db.connect().cursor(named_tuple=True) as cursor:
            cursor.execute("SELECT FileImageID FROM Bots WHERE BotID = %s", (bot_id,))
            file_id = cursor.fetchone()[0]

            cursor.execute(queries["SELECT_FILENAME"], (file_id, ))
            data = cursor.fetchone()

            expansion = data.FileName.split('.')[1]
            try:
                file_path = file_id + '.' + expansion
                print(file_path)
                file_path = app.config['UPLOAD_FOLDER'] + '\\' + file_path
                print(file_path)
                if os.path.exists(file_path):
                    # Удаляем файл
                    os.remove(file_path)
            except:
                print("такого файла не существует")

            query = queries["DELETE_BOT_IN_BOTS_TABLE"]
            cursor.execute(query, (file_id,))

            db.connect().commit()
            flash('Удаление успешно', 'success')
    except:
        db.connect().rollback()
        print("ошибка при удалении бота")

    return redirect(url_for('index'))


@bp.route('/create_bot', methods=['GET', 'POST'])
@login_required
@checkRole("create")
def create_bot():
    card = {}
    types = []
    # ------------------------------------------------------
    try:
        with db.connect().cursor(named_tuple=True) as cursor:
            query = queries["SELECT_TYPES"]
            cursor.execute(query, ())
            types = cursor.fetchall()
    except:
        print("Не удалось получить все типы для ботов")
    # ------------------------------------------------------

    if request.method == "POST":
        # получение данных
        UserID = current_user.id

        types_form = request.form.getlist('types')

        NameForWhat = request.form.get('NameForWhat')
        NameBot = request.form.get('NameBot')
        ShortDescription = request.form.get('ShortDescription')
        Description = request.form.get('Description')
        Developer = request.form.get('Developer')
        card["NameBot"] = NameBot
        card["ShortDescription"] = ShortDescription
        card["Description"] = Description
        card["Developer"] = Developer
        # -------------------------------------------------------------------------------
        try:
            with db.connect().cursor() as cursor:
                # тут сгенерировать md5 хэш найти есть ли такой же уже в таблице,
                # добавить новый если нет в таблице,
                # указать FileName если уже такой есть в таблице
                file = None
                file_id = None
                try:
                    # взятить файл из формы ошибка если файла нет, потом переделать
                    file = request.files['CoverImage']
                    md5_hash = hashlib.md5(file.read()).hexdigest()
                    file.seek(0)
                    query = "SELECT FileID FROM ImageFiles WHERE MD5Hash = %s"
                    cursor.execute(query, (md5_hash,))
                    data = cursor.fetchone()
                    print("data", data)
                    # создать запись если такой нет
                    if data == None:
                        print("создаю название файла")
                        file_name = secure_filename(file.filename)

                        file_id = str(uuid4())
                        expansion = file.filename.split('.')[1]

                        print(f"filename :{file.filename}")
                        print(f"expansion: {expansion}")

                        new_file_name = (file_id + '.' + expansion)

                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_file_name)
                        file.save(file_path)

                        mime_type = file.content_type
                        # FileID, FileName, MIMEType, MD5Hash
                        query = queries["INSERT_FILE"]
                        cursor.execute(query, (file_id, file_name, mime_type, md5_hash))
                        last_file_id = cursor.lastrowid
                        print(f"запись в таблице создана:\nfile_id: {file_id}\nfile_name: {file_name}\nmime_type: {mime_type}\nmd5_hash: {md5_hash}\n" + "_" * 100)
                    else:

                        file_id = data[0]
                        print(data)
                except:
                    print("фотография из формы не взята")

                print("начало добавления бота")
                print(f"file_id: {file_id}")
                # добавление бота должно быть после добавление/взяти обложки
                Description = sanitaizer_text(Description)
                ShortDescription = sanitaizer_text(ShortDescription)
                print(f"file_id: {file_id}, NameBot: {NameBot}, Description: {Description}, ShortDescription {ShortDescription}, NameForWhat {NameForWhat}, Developer {Developer}, UserID {UserID}")
                # FileImage, NameBot, Description, ShortDescription, NameForWhat, Developer, UserID
                query = queries["INSERT_BOT"]
                cursor.execute(query, (file_id, NameBot, Description, ShortDescription, NameForWhat, Developer, UserID))
                print("lfflf ",cursor.lastrowid)
                bot_id = cursor.lastrowid

                # ----------------------------------------------------------------------------------------------------------

                print("_" * 100)

                # Добавление записей в BotsType
                for type_name in types_form:
                    query = queries["SELECT_TYPEID"]
                    cursor.execute(query, (type_name,))
                    type_id = cursor.fetchone()[0]

                    query = queries["INSERT_IN_BOTSTYPES"]
                    cursor.execute(query, (bot_id, type_id))


                db.connect().commit()
                flash('Вы добавили бота', 'success')
                return redirect(url_for('index'))

        except Exception as e:
            db.connect().rollback()
            flash(f'Ошибка при добавлении бота: {str(e)}', 'danger')
            return render_template('create_bot.html', types=types, card=card)

    return render_template('create_bot.html', types=types, card=card)



@bp.route('/edit_bot/<bot_id>', methods=['GET', 'POST'])
@login_required
@checkRole("edit")
def edit_bot(bot_id):
    card = {}
    types = []
    try:
        with db.connect().cursor(named_tuple=True) as cursor:
            query = queries["SELECT_TYPES"]
            cursor.execute(query, ())
            types = cursor.fetchall()
    except:
        print("не удалось получиь все типы для ботов")

    if request.method == "POST":
        UserID = current_user.id

        types_form = request.form.getlist('types')

        NameForWhat = request.form.get('NameForWhat')
        NameBot = request.form.get('NameBot')
        ShortDescription = request.form.get('ShortDescription')
        Description = request.form.get('Description')
        Developer = request.form.get('Developer')

        card["NameBot"] = NameBot
        card["ShortDescription"] = ShortDescription
        card["Description"] = Description
        card["Developer"] = Developer

        try:
            with db.connect().cursor(named_tuple=True) as cursor:
                #UPDATE users SET NameBot=%s, NameForWhat=%s Description=%s, ShortDescription=%s, Developer=%s where BotID=%s;
                query = queries["UPDATE_Bot"]
                cursor.execute(query,(NameBot, NameForWhat, Description, ShortDescription, Developer, bot_id))
                db.connect().commit()
                flash("вы обновили данные о боте", 'success')
                return redirect(url_for('index'))
        except:
            db.connect().rollback()
            flash("вам не удалось обновить данные о боте", 'danger')

    return  render_template('edit_bot.html', card=card)


@bp.route('/moderation', methods=['GET', 'POST'])
@login_required
@checkRole("moderation")
def moderation_reviews():
    try:
        with db.connect().cursor(named_tuple=True) as cursor:
            query = queries["SELECT_ALL_REVIEWS_FOR_MODERATOR"]
            cursor.execute(query, )
            reviews_moder = cursor.fetchall()
            print(reviews_moder)

    except:
        db.connect().rollback()
        flash("вам не удалось обновить данные о боте", 'danger')
    return render_template("moder_reviews.html", reviews_moder=reviews_moder)

@bp.route('/show_reviews/<int:id_review>', methods=['GET', 'POST'])
@login_required
@checkRole("moderation")
def show_reviews(id_review):
    review = {}
    if request.method == "GET":
        try:
            with db.connect().cursor(named_tuple=True) as cursor:
                query = queries["SELECT_ALL_REVIEW_FOR_MODERATOR"]
                cursor.execute(query, (id_review,))
                review = cursor.fetchone()
                print("review", review)

        except:
            db.connect().rollback()
            print("ошибка при отображении запроса")
            flash("вам не удалось обновить данные о боте", 'danger')

    return render_template("show_reviews.html", review=review)


@bp.route('/approval/<int:id_review>', methods=['POST'])
@login_required
@checkRole("moderation")
def approval(id_review):
    try:
        with db.connect().cursor(named_tuple=True) as cursor:
            query = queries["UPDATE_STATUS"]
            cursor.execute(query, (2, id_review))
            db.connect().commit()
            flash("вы одобрили отзыв", 'success')

    except:
        db.connect().rollback()
        print("ошибка при обновление статуса бота")
        flash("вам не удалось обновить статус бота", 'danger')

    return moderation_reviews()


@bp.route('/reject/<int:id_review>', methods=['POST'])
@login_required
@checkRole("moderation")
def reject(id_review):
    try:
        with db.connect().cursor(named_tuple=True) as cursor:
            query = queries["UPDATE_STATUS"]
            cursor.execute(query, (3, id_review))
            db.connect().commit()
            flash("вы отклонили отзыв", 'danger')

    except:
        db.connect().rollback()
        print("ошибка при обноваление статуса бота")
        flash("вам не удалось обновить статус бота", 'danger')

    return moderation_reviews()