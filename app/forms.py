# -*- coding: utf-8 -*-

# Библиотеки третьей стороны
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

# Собственные модули
from app.models import User


class LoginForm(FlaskForm):
    """
    Класс формы для входа пользователя.

    Attributes:
        username (StringField): Поле для ввода имени пользователя.
        password (PasswordField): Поле для ввода пароля.
        remember_me (BooleanField): Флажок "Запомнить меня".
        submit (SubmitField): Кнопка "Войти".
    """
    username: StringField = StringField('Имя пользователя', validators=[DataRequired()])
    password: PasswordField = PasswordField('Пароль', validators=[DataRequired()])
    remember_me: BooleanField = BooleanField('Запомни меня')
    submit: SubmitField = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    """
    Класс формы регистрации пользователя.

    Attributes:
        username (StringField): Поле для ввода имени пользователя.
        email (StringField): Поле для ввода почты.
        password (PasswordField): Поле для ввода пароля.
        password2 (PasswordField): Поле для повторного ввода пароля.
        submit (SubmitField): Кнопка "Регистрация".
    """
    username: StringField = StringField('Имя пользователя', validators=[DataRequired()])
    email: StringField = StringField('Почта', validators=[DataRequired(), Email()])
    password: PasswordField = PasswordField('Пароль', validators=[DataRequired()])
    password2: PasswordField = PasswordField(
        'Повтор пароля', validators=[DataRequired(), EqualTo('password')])
    submit: SubmitField = SubmitField('Регистрация')

    def validate_username(self, username):
        """
        Проверяет уникальность имени пользователя.

        Args:
            username (StringField): Поле имени пользователя.

        Raises:
            ValidationError: Если имя пользователя уже занято.
        """
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Используйте другое имя.')

    def validate_email(self, email):
        """
        Проверяет уникальность почты.

        Args:
            email (StringField): Поле почты.

        Raises:
            ValidationError: Если почта уже используется другим пользователем.
        """
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Используйте другую почту.')


class EditProfileForm(FlaskForm):
    """
    Класс формы редактирования профиля.

    Attributes:
        username (StringField): Поле для изменения имени пользователя.
        about_me (TextAreaField): Поле для изменения описания информации о пользователе.
        submit (SubmitField): Кнопка для отправки данных формы
    """
    username: StringField = StringField('Имя пользователя', validators=[DataRequired()])
    about_me: TextAreaField = TextAreaField('Обо мне', validators=[Length(min=0, max=140)])
    submit: SubmitField = SubmitField('Принять изменения')
