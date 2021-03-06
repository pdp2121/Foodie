
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, url_for
logged_in = False
uname = ""
uid = -1



tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@34.73.36.248/project1
#
# For example, if you had username zy2431 and password 123123, then the following line would be:
#
#     DATABASEURI = "postgresql://zy2431:123123@34.73.36.248/project1"
#
DATABASEURI = "postgresql://pdp2121:phusally@34.73.36.248/project1" # Modify this with your own credentials you received from Joseph!


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: https://flask.palletsprojects.com/en/1.1.x/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  #print(request.args)


  #
  # example of a database query
  #
  #cursor = g.conn.execute("SELECT * FROM restaurant")
  # names = []
  # for result in cursor:
  #   names.append(result['name'])  # can also be accessed using result[0]
  # cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  #context = dict(data = names)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  print("Logged in: " + str(logged_in))
  print("uid: " + str(uid))
  print("uname: " + str(uname))

  return render_template("index.html", logged_in = logged_in, uid = uid, uname = uname)

# test
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
@app.route('/reslist')
def reslist():
  resname = request.args.get('resname')
  country = request.args.get('country')
  city = request.args.get('city')
  state = request.args.get('state')
  keyword = request.args.get('keyword')
  if resname:
    resname = '%'+resname.lower()+'%'
    cursor = g.conn.execute('SELECT * FROM restaurant WHERE LOWER(name) LIKE %s', resname)
  if country:
    country = '%'+country.lower()+'%'
    cursor = g.conn.execute('SELECT * FROM restaurant r INNER JOIN cuisine c ON r.cuisine_id = c.cuisine_id AND LOWER(country) LIKE %s', country)
  if city:
    city = '%' + city.lower() + '%'
    cursor = g.conn.execute('SELECT * FROM restaurant WHERE LOWER(city) LIKE %s', city)
  if state:
    state = '%' + state.lower() + '%'
    cursor = g.conn.execute('SELECT * FROM restaurant WHERE LOWER(state) LIKE  %s', state)
  if keyword:
    keyword = '%' + keyword.lower() + '%'
    cursor = g.conn.execute('SELECT r.* FROM restaurant r INNER JOIN res_menu rm ON r.restaurant_id = rm.restaurant_id INNER JOIN menu m ON m.menu_id = rm.menu_id INNER JOIN menu_contain mc ON mc.menu_id = m.menu_id INNER JOIN food f ON f.food_id = mc.food_id WHERE LOWER(f.name) LIKE %s', keyword)

  res = []
  for result in cursor:
    res.append(result)
  cursor.close()
  context= dict(rdata = res)
  return render_template("reslist.html", **context)

@app.route('/menu/<rid>')
def getmenu(rid):
  cursor = g.conn.execute('SELECT * FROM menu m, res_menu r WHERE r.restaurant_id = %s and m.menu_id = r.menu_id ', rid)
  res = []
  for result in cursor:
    res.append(result)
  context= dict(rdata = res)
  cursor = g.conn.execute('SELECT name from restaurant where restaurant_id = %s',rid)
  res2 =[]
  for result in cursor:
    res2.append(result)

  context2 = dict(fdata= res2)
  cursor = g.conn.execute('SELECT country, region, price_range, vegetarian from cuisine, restaurant where restaurant.restaurant_id = %s and cuisine.cuisine_id = restaurant.cuisine_id',rid)
  res3 =[]
  for result in cursor:
    res3.append(result)
  cursor = g.conn.execute("""SELECT u.name, rv.*, t.content AS mcontent FROM write_review rw
  INNER JOIN users u ON rw.user_id = u.user_id AND rw.restaurant_id = %s
  INNER JOIN review rv ON rw.review_id = rv.review_id
  LEFT JOIN mention m ON m.source_id = rv.review_id
  LEFT JOIN (SELECT * FROM review) t
  ON m.dest_id = t.review_id""", rid)
  res4 = []
  for result in cursor:
    res4.append(result)
  context4 = dict(rvdata= res4)
  cursor.close()
  context3 = dict(sdata= res3)
  return render_template("menu.html", **context,**context2,**context3,**context4)
  
  
@app.route('/menu/type/<menuid>/<rid>')
def getfood(menuid,rid):
  cursor = g.conn.execute('SELECT * from menu_contain c, food f where c.menu_id = %s and f.food_id = c.food_id', menuid)
  res = []
  for result in cursor:
    res.append(result)
  context= dict(rdata = res)
  cursor = g.conn.execute('SELECT name from restaurant where restaurant_id = %s',rid)
  res2 =[]
  for result in cursor:
    res2.append(result)
  cursor.close()
  context2 = dict(fdata= res2)
  return render_template("food.html", **context,**context2)
  

# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)
  return redirect('/')

@app.route('/search', methods=['POST'])
def search_name():
  resname = request.form['resname']
  return redirect(url_for('reslist',rid="", resname = resname))

@app.route('/searchcountry', methods=['POST'])
def search_country():
  country = request.form['country']
  return redirect(url_for('reslist',rid="",country=country))

@app.route('/searchcity', methods=['POST'])
def search_city():
  city = request.form['city']
  return redirect(url_for('reslist',rid="",city=city))

@app.route('/searchstate', methods=['POST'])
def search_state():
  state = request.form['state']
  return redirect(url_for('reslist',rid="",state = state))

@app.route('/keyword', methods=['POST'])
def search_keyword():
  keyword = request.form['keyword']
  return redirect(url_for('reslist',rid="",keyword = keyword))


@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
      global uid
      uid = request.form['uid']
      cursor = g.conn.execute('SELECT COUNT (*) AS count, name FROM users WHERE user_id = %s GROUP BY name', uid)
      count = -1
      error = None
      global uname
      for result in cursor:
        count = result["count"]
        print("count: " + str(count))
        uname = result["name"]
      if count <= 0:
        error = "Invalid Credentials. Please try again."
      else:
        global logged_in
        logged_in = True
        print(logged_in)
        return redirect('/')
      return render_template('login.html', error=error)
    elif request.method == 'GET':
      return render_template("login.html")

@app.route('/userpage')
def userpage():
  global uid
  cursor = g.conn.execute("""SELECT u.status, u.email, r.restaurant_id, r.name FROM users u 
  INNER JOIN favorite f ON u.user_id = f.user_id AND u.user_id= %s
   INNER JOIN restaurant r ON f.restaurant_id = r.restaurant_id""", uid)
  res = []
  status = ""
  email = ""
  for result in cursor:
    res.append(result)
    status = result["status"]
    email = result["email"]
  cursor.close()
  context= dict(udata = res)
  return render_template("userpage.html", **context, uid = uid, uname = uname, status= status, email=email)

@app.route('/logout')
def logout():
  global logged_in, uid, uname
  logged_in = False
  uid = -1
  uname = ""
  return redirect('/')


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()
