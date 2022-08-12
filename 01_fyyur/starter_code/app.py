#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from unicodedata import name
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import form
from config import SECRET_KEY
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
# app.config.from_object('config')
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:lanreawe7@localhost:5432/fyyur'
db = SQLAlchemy(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Show(db.Model):
    __tablename__ = 'shows'
    id=db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'),)
    artist_id = db.Column(db.Integer,db.ForeignKey('artists.id'))
    start_time = db.Column(db.DateTime)

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default= False)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    seeking_description = db.Column(db.String(1000))
    show =db.relationship('Show', backref =db.backref('venue', lazy=True))
    artist =db.relationship('Artist', secondary ='shows', backref = 'artist_venue')



class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description =db.Column(db.String(1000))
    show = db.relationship('Show', backref =db.backref('artist', lazy=True))
    venue =db.relationship('Venue', secondary='shows', backref = 'venue_artist')



  

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

  show_data=[]
  datas = Venue.query.all()

  for data in datas:
    show_venues = []
    venues = Venue.query.filter_by(city=data.city).filter_by(state = data.state).all()

    for venue in venues:
        show_venues.append({
          'id': venue.id,
          'name': venue.name,
          'num_upcoming_shows': len(db.session.query(Show).filter(Show.venue_id==venue.id).filter(Show.start_time> datetime.now()).all())
        })

    show_data.append({
        'state': data.state,
        'city': data.city,
        'venues': show_venues

        })

 
  return render_template('pages/venues.html', areas=show_data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term=request.form.get('search_term', '')

  search_result = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()
  count = len(search_result)

  response = {
    'count': count,
    'data': search_result
  }

  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.filter_by(id=venue_id).first()
  upcoming_shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show. start_time>datetime.now()).all()   
  upcoming_shows = []
  for show in upcoming_shows_query:
    upcoming_shows.append({
      'artist_id': show.id,
      'artist_name': show.name,
      'artist_image_link': show.image_link,
      'start_time': str(show.start_time),
    })

  past_shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.now()).all()   
  past_shows = []
  for show in past_shows_query:
    past_shows.append({
      'artist_id': show.id,
      'artist_name': show.name,
      'artist_image_link': show.image_link,
      'start_time': str(show.start_time),
    })

  data = {
    "id": venue.id,
    "name":venue.name,
    "genres":venue.genres,
    "address":venue.address,
    "city":venue.city,
    "state":venue.state,
    "phone":venue.phone,
    "facebook_link":venue.facebook_link,
    "seeking_talent":venue.seeking_talent,
    "image_link":venue.image_link,
    "past_shows":venue.past_shows,
    "upcoming_shows":venue.upcoming_shows,
    "past_shows_count":len(past_shows),
    "upcoming_shows_count":len(upcoming_shows)
  }  
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm()

 
  try:
      name = form.name.data
      city = form.city.data
      state = form.state.data
      address = form.address.data
      image_link = form.image_link.data
      phone = form.phone.data
      genres = form.genres.data
      facebook_link = form.facebook_link.data
      website_link = form.website_link.data
      seeking_talent = form.seeking_talent.data
      seeking_description = form.seeking_description.data

      venue = Venue(name=name, city=city, state=state,address=address,image_link=image_link,phone=phone,genres=genres,facebook_link=facebook_link,
      website_link=website_link, seeking_talent=seeking_talent, seeking_description=seeking_description)
    
      
      db.session.add(venue)
      db.session.commit()
  except:
      db.session.rollback()

  finally:
      db.session.close()
 
  if form.validate_on_submit():
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  else:
    for field, message in form.errors.items():
      flash(field + ' - ' + str(message), 'danger')
    return render_template('forms/new_venue.html', form=form)
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()

  except:
        db.session.rollback()
  finally:
        db.session.close()
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.all()
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():

  search_term=request.form.get('search_term', '')

  search_result = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all()
  count = len(search_result)

  response = {
    'count': count,
    'data': search_result
  }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.filter_by(id=artist_id).first()

  upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show. start_time>datetime.now()).all()   
  upcoming_shows = []
  for show in upcoming_shows_query:
    upcoming_shows.append({
      'venue_id': show.id,
      'venue_name': show.name,
      'venue_image_link': show.image_link,
      'start_time': str(show.start_time),
    })

  past_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time<datetime.now()).all()   
  past_shows = []
  for show in past_shows_query:
    past_shows.append({
      'venue_id': show.id,
      'venue_name': show.name,
      'venue_image_link': show.image_link,
      'start_time': str(show.start_time),
    })

  data = {
    "id": artist.id,
    "name":artist.name,
    "genres":artist.genres,
    "address":artist.address,
    "city":artist.city,
    "state":artist.state,
    "phone":artist.phone,
    "facebook_link":artist.facebook_link,
    "seeking_talent":artist.seeking_talent,
    "image_link":artist.image_link,
    "past_shows":artist.past_shows,
    "upcoming_shows":artist.upcoming_shows,
    "past_shows_count":len(past_shows),
    "upcoming_shows_count":len(upcoming_shows)
  }
  
  return render_template('pages/show_artist.html', artist=data )

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  data= Artist.query.filter_by(id=artist_id).all()
  return render_template('forms/edit_artist.html', form=form, artist=data[0])

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm()
  try:
    artist = Artist.query.get(artist_id)
    artist.name = form.name.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.image_link = form.image_link.data
    artist.phone = form.phone.data
    artist.genres = form.genres.data
    artist.facebook_link = form.facebook_link.data
    artist.website_link = form.website_link.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data

    db.session.commit()

  except:
    db.session.rollback()

  finally:
    db.session.close()


  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  data= Venue.query.filter_by(id=venue_id).all()
  return render_template('forms/edit_venue.html', form=form, venue=data[0])

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form=VenueForm()
  try:
    venue = Venue.query.get(venue_id)
    venue.name = form.name.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.image_link = form.image_link.data
    venue.phone = form.phone.data
    venue.genres = form.genres.data
    venue.facebook_link = form.facebook_link.data
    venue.website_link = form.website_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data

  except:
    db.session.rollback()

  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm()
  try:
      name = form.name.data
      city = form.city.data
      state = form.state.data
      image_link = form.image_link.data
      phone = form.phone.data
      genres = form.genres.data
      facebook_link = form.facebook_link.data
      website_link = form.website_link.data
      seeking_venue = form.seeking_venue.data
      seeking_description = form.seeking_description.data

      artist = Artist(name=name, city=city, state=state,image_link=image_link,phone=phone,genres=genres,facebook_link=facebook_link,
      website_link=website_link, seeking_venue=seeking_venue, seeking_description=seeking_description)
      db.session.add(artist)
      db.session.commit()

  except:
    db.session.rollback()

  finally:
    db.session.close()

  if form.validate_on_submit():
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  else:
    for field, message in form.errors.items():
      flash(field + ' - ' + str(message), 'danger')
    return render_template('forms/new_venue.html', form=form)
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

  shows_data = db.session.query(Venue.name,Artist.name,Artist.image_link,Show.venue_id,Show.artist_id,Show.start_time).filter(Venue.id == Show.venue_id, Artist.id == Show.artist_id).all()
  data = []
  for show in shows_data:
      data.append({
          'venue_name': show[0],
          'artist_name': show[1],
          'artist_image_link': show[2],
          'venue_id': show[3],
          'artist_id': show[4],
          'start_time': str(show[5])
        })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form =ShowForm()

  try:
    venue_id = form.venue_id.data
    artist_id = form.artist_id.data
    start_time = form.start_time.data

    show= Show(venue_id=venue_id,artist_id=artist_id,start_time=start_time)
    db.session.add(show)
    db.session.commit()
  except:
    db.session.rollback()

  finally:
    db.session.close()

  flash('Show was successfully listed!')
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
'''
