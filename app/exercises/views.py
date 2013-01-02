# third party imports
from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for, json, jsonify
from sqlalchemy.sql import func, extract, desc

# local application imports
from app import db
from app.exercises.forms import TotalOnWeekByMonthForm
from app.exercises.models import Exercise
from app.exercises.helpers import DateHelper
from app.users.constants import SESSION_NAME_USER_ID
from app.users.models import User
from app.users.requests import app_before_request
from app.users.decorators import requires_login


mod = Blueprint('exercises', __name__, url_prefix='/exercises')


@mod.before_request
def before_request():
	app_before_request()


@mod.route('/')
@mod.route('/i_did', methods=['GET'])
@requires_login
def index():
	return render_template('exercises/i_did.html')


@mod.route('/i_did', methods=['POST'])
@requires_login
def idid():
	# get the date of yesterday and the current user id
	yesterday = DateHelper.get_yesterday()
	user_id = session[SESSION_NAME_USER_ID]
	
	# create a new object to exercise
	exercise = Exercise(yesterday, user_id)

	user = User(user_id)
	if user.alreadyDidExerciseYesterday():
		flash('You already did exercise yesterday')
		return render_template('exercises/i_did.html')

	# insert the record in our db and commit it
	db.session.add(exercise)
	db.session.commit()

	# display a message to the user
	flash('Keep fitness and do it again tomorrow')

	# redirect user to the 'index' method of the user module
	return redirect(url_for('users.index'))

@mod.route('/general/')
def general():
	# get the total of exercises every user have done since the begin
	results = db.session.query(User.name, func.count(User.name).label('total'))\
						.group_by(User.name)\
						.filter(Exercise.user_id == User.id)\
						.all()

	# convert list to dictonary
	data = {name: str(total) for (name, total) in results}

	return render_template('exercises/general.html', data=data)


@mod.route('/total_on_week_by_month/', methods=['GET','POST'])
@requires_login
def total_on_week_by_month():
	# get all months a user have done exercises
	all_months = db.session.query(Exercise.date)\
						.group_by(extract('year', Exercise.date), extract('month', Exercise.date))\
						.order_by(desc(Exercise.date))\
						.filter(Exercise.user_id == g.user.id)\
						.all()

	form = TotalOnWeekByMonthForm(request.form)
	# set all months as options of SELECT element on the form
	form.months.choices = [(DateHelper.generate_id_by_month_year(item.date), 
							DateHelper.date_to_year_month_string(item.date)) 
							for item in all_months]

	# when is a POST action
	if form.validate_on_submit():
		date_selected = DateHelper.generated_id_by_month_year_to_date(form.months.data)

		# get the total exercises a user have done per week on a selected month
		results = db.session.query(func.strftime('%W', Exercise.date).label('week'), func.count(Exercise.date).label('total'))\
						.group_by(func.strftime('%W', Exercise.date))\
						.filter(extract('month', Exercise.date) == date_selected.month)\
						.filter(extract('year', Exercise.date) == date_selected.year)\
						.filter(Exercise.user_id == g.user.id)\
						.all()

		# convert list to dictonary
		data = {('Week %s on year' % (week)): str(total) for (week, total) in results}

		return render_template('exercises/total_on_week_by_month.html', form=form, data=data)
	return render_template('exercises/total_on_week_by_month.html', form=form)



