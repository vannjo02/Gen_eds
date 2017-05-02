from flask import Flask, render_template, request
import psycopg2
from flask_bootstrap import Bootstrap
import os

app = Flask(__name__)

Bootstrap(app)


#ssh -f vannjo02@knuth.luther.edu -L 2345:localhost:5432 -N

conn = psycopg2.connect(os.environ['DATABASE_URL'])


@app.route('/')
def index():
	reqlst = ["Human Expression—Primary Texts", "Intercultural", "Historical", "Natural World—Nonlab", "Religion", "Human Expression", "Skills", "Human Behavior", "Human Behavior—Social Science Methods", "Quantitative", "Natural World—Lab", "Biblical Studies", "Wellness"]
	
	cur=conn.cursor()
	cur.execute("select number, title, count(requirement.description) as count from course join course_requirement on (course.id = course_requirement.course) join requirement on (requirement.id = course_requirement.requirement) group by number, title order by count desc limit 5")
	res=cur.fetchall()
	print(res)
	return render_template('index.html', reqs=reqlst, res = res)


@app.route('/requirement/')
def requirement():
	reqs=tuple(request.args.getlist('option'))
	
	cur=conn.cursor()
	cur.execute("select number, title from course join course_requirement on (course.id = course_requirement.course) join requirement on (requirement.id = course_requirement.requirement) where requirement.description in %s group by number, title having count(requirement.description) >= %s", (reqs, len(reqs)))
	res=cur.fetchall()
	print(res)
	return render_template('requirement.html', courses=res, reqs = reqs)


@app.route('/course/<crs>')
def course(crs):

	cur = conn.cursor()
	cur.execute("select requirement.description from course join course_requirement on (course.id = course_requirement.course) join requirement on (requirement.id = course_requirement.requirement) where course.number = %s", (crs,))
	res = cur.fetchall()
	print(res)
	cur.execute("select title, course.description from course where course.number = %s", (crs,))
	info = cur.fetchall()[0]
	print(info)


	return render_template('course.html', course = res, info = info, crs = crs)


@app.route('/search/')
def search():
	query = tuple(request.args.getlist('input'))[0].title()
	search= "%" + query + "%"
	cur = conn.cursor()
	cur.execute("select number, title from course where course.title like %s", (search,))
	search = cur.fetchall()
	print("Results", search)
	fulfills = []
	for course in search:
		cur.execute("select requirement.description from course join course_requirement on (course.id = course_requirement.course) join requirement on (requirement.id = course_requirement.requirement) where course.number = %s", (course[0],))
		tmp = []		
		for req in cur.fetchall():
			tmp.append(req[0])
		fulfills.append(tmp)
	print("Reqs list", fulfills)

	return render_template('search.html', search = search, lst = fulfills, query = query)
							
app.run(debug='True', host="0.0.0.0", port=8001)
