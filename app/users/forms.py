from flask.ext.wtf import Form, TextField, PasswordField, BooleanField
from flask.ext.wtf import Required, Email, EqualTo

class LoginForm(Form):
	email = TextField('Email address', [Required(), Email()])
	password = PasswordField('Password', [Required()])


class RegisterForm(Form):
	name = TextField('NickName', [Required()])
	email = TextField('Email address', [Required()])
	password = PasswordField('Password', [Required()])
	confirm = PasswordField('Repeat Password', [
		Required(),
		EqualTo('confirm', message='Passwords must match')
		])