# -*- coding: utf-8 -*-

# Стандартные библиотеки Python
from datetime import datetime

# Библиотеки третьей стороны
from flask_login import UserMixin
from hashlib import md5
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

# Собственные модули
from app import db, login

# Таблица followers моделирует отношения "подписчик - подписан на" между пользователями.
# Она используется для отслеживания того, какие пользователи подписаны на каких других пользователей.
# Столбец 'follower_id' представляет пользователя, который подписывается на других пользователей,
# Столбец 'followed_id' представляет пользователя, на которого подписаны.
followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
                     )


class User(UserMixin, db.Model):
    """
    Модель пользователя для базы данных.
    """
    __tablename__ = 'user'
    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.String(64), index=True, unique=True)
    email: str = db.Column(db.String(120), index=True, unique=True)
    password_hash: str = db.Column(db.String(128))
    about_me: str = db.Column(db.String(140))
    last_seen: datetime = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    # Для отношений «один ко многим».
    # Аргумент backref определяет имя поля добавленное к объектам класса «много», для указания на объект «один».
    posts: relationship = db.relationship('Post', backref='author', lazy='dynamic')
    __allow_unmapped__ = True

    def __repr__(self) -> str:
        """
        Метод, возвращающий строковое представление объекта пользователя.
        """
        return f'<Пользователь {self.username}>'

    def set_password(self, password: str) -> None:
        """
        Установка хэша пароля пользователя.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """
        Проверка введенного пароля с хэшем пароля пользователя.
        """
        return check_password_hash(self.password_hash, password)

    def avatar(self, size: int) -> str:
        """
        Генерирует URL аватара пользователя на основе Gravatar.

        Args:
            size (int): Размер аватара в пикселях.

        Returns:
            str: URL аватара пользователя.

        Note:
            Для генерации аватара используется хеш от адреса электронной почты пользователя (email),
            который приводится к нижнему регистру, кодируется в формате UTF-8 и хешируется с помощью MD5.
            Полученный хеш используется в URL для получения аватара с сервиса Gravatar.
        """
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def is_following(self, user: 'User') -> bool:
        """
        Проверить, подписан ли текущий пользователь на указанного пользователя.

        Args:
            user (User): Пользователь, наличие подписки на которого нужно проверить.

        Returns:
            bool: True, если текущий пользователь подписан на указанного пользователя, в противном случае False.
        """
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def follow(self, user: 'User') -> None:
        """
        Начать подписку на указанного пользователя.

        Args:
            user (User): Пользователь, на которого нужно подписаться.
        """
        if not self.is_folloving(user):
            self.followed.append(user)

    def unfollow(self, user: 'User') -> None:
        """
        Прекратить подписку на указанного пользователя.

        Args:
            user (User): Пользователь, от которого нужно отписаться.
        """
        if not self.is_folloving(user):
            self.followed.remove(user)


class Post(db.Model):
    """
    Модель поста для базы данных.
    """
    id: int = db.Column(db.Integer, primary_key=True)
    body: str = db.Column(db.String(140))

    # Специально не включил () после utcnow,
    # поэтому передаю эту функцию, а не результат ее вызова.
    # SQLAlchemy установит для поля значение вызова этой функции.
    # Это позволяет работать с датами и временем UTC в серверном приложении.
    # То есть гарантирует, что используются единые временные метки независимо от того, где находятся пользователи
    timestamp: datetime = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id: int = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self) -> str:
        """
        Метод, возвращающий строковое представление объекта поста.
        """
        return f'Пост {self.body}'


@login.user_loader
def load_user(id: int) -> User | None:
    """
    Функция для загрузки пользователя по его идентификатору.

    Args:
        id (int): Идентификатор пользователя.

    Returns:
        User: Экземпляр пользователя, если найден, или None.
    """
    return User.query.get(int(id))
