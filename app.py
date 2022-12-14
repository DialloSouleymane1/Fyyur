#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from sqlalchemy import func
from ast import dump
from email.policy import default
from unittest import result
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from .config import CustomConfig
from .forms import *
from flask_migrate import Migrate
from .models import Show, Venue, db, Artist
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
db.init_app(app)
app.config.from_object(CustomConfig)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)

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
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    
  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]
  #my_query = Show.query.with_entities(Venue.city, Venue.state).group_by(Venue.city, Venue.state)
  #print(my_query)
  data=[{
    "city": "San Francisco",
    "state": "CA",
    "venues": Venue.query.all()
  }]
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term','')

  venues = Venue.query.filter(Venue.name.ilike("%" + search_term + "%")).all()
  
  response={
    "count": Venue.query.filter(Venue.name.ilike("%" + search_term + "%")).count(),
    "data": venues
  }

  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  past_shows = []
  upcoming_shows = []
  past_shows_count = 0
  upcoming_shows_count = 0
  for show in venue.shows:
    if(datetime.now() > show.start_time):
      past_shows = Show.query.join(Venue,Artist).with_entities(
      Artist.image_link,
      Artist.name,
      Show.start_time,
      Show.artist_id).filter(Venue.id == show.venue_id,Show.start_time<datetime.now())
      # past_shows.append(show)
      past_shows_count = past_shows_count+1
    if (datetime.now() <= show.start_time):
      upcoming_shows = Show.query.join(Venue,Artist).with_entities(
      Artist.image_link,
      Artist.name,
      Show.start_time,
      Show.artist_id).filter(Venue.id == show.venue_id,Show.start_time>=datetime.now())
      upcoming_shows_count = upcoming_shows_count+1
  # print("Venue object", venue)
  # print("Venue attrs keys", venue.__mapper__.attrs.keys())
  # print("venuess show", venue.shows)
  data={
    "venue":venue,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": past_shows_count,
    "past_shows": past_shows,
    "upcoming_shows_count": upcoming_shows_count,
  }
  # print(data)
 
  return render_template('pages/show_venue.html', result=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # looking_for_talent = request.form.get('seeking_talent')
  # print(looking_for_talent)
  try:
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')
    phone = request.form.get('phone')
    image_link = request.form.get('image_link')
    facebook_link = request.form.get('facebook_link')
    genres = request.form.getlist('genres')
    website_link = request.form.get('website_link')
    looking_for_talent = True if request.form.get('seeking_talent') == 'y' else False
    seeking_description = request.form.get('seeking_description','')
    venue = Venue(name=name,city=city,state=state,address=address,phone=phone,genres=genres,image_link=image_link,website_link=website_link,facebook_link=facebook_link,looking_for_talent=looking_for_talent,seeking_description=seeking_description)
    # print(venue)
    # if phone number must be unique
    my_venue = Venue.query.filter(Venue.phone == phone).first()
    if my_venue:
      flash('This phone number '+phone+' has already be taken')
      return render_template('pages/home.html')
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + name + ' was successfully listed!')
  except:
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('Venue ' + name + ' could not be listed.')
  finally:
    db.session.close()
  
  
  return render_template('pages/home.html')

@app.route('/venues/delete', methods=['POST'])
def delete_venue():
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue_id = request.form.get('venue_id')
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    flash('Successful deletion ','success')
  except:
    db.session.rollback()
    flash('We cannot delete this venue, because it has one or more associations','error')
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = Artist.query.order_by("id").all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term','')

  artists = Artist.query.filter(Artist.name.ilike("%" + search_term + "%")).all()

  response={
    "count": Artist.query.filter(Artist.name.ilike("%" + search_term + "%")).count(),
    "data": artists
  }
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)
  past_shows = []
  upcoming_shows = []
  past_shows_count = 0
  upcoming_shows_count = 0
  for show in artist.shows:
    if(datetime.now() > show.start_time):
      past_shows = Show.query.join(Venue,Artist).with_entities(
      Venue.image_link,
      Venue.name,
      Show.start_time,
      Show.venue_id).filter(Artist.id == show.artist_id,Show.start_time<datetime.now())
      past_shows_count = past_shows_count+1
    if (datetime.now() <= show.start_time):
      upcoming_shows = Show.query.join(Venue,Artist).with_entities(
      Venue.image_link,
      Venue.name,
      Show.start_time,
      Show.venue_id).filter(Venue.id == show.venue_id,Show.start_time>=datetime.now())
      upcoming_shows_count = upcoming_shows_count+1
  # print("Artist attrs keys", artist.__mapper__.attrs.keys())
  data={
    "artist":artist,
    "upcoming_shows": upcoming_shows,
    "past_shows": past_shows,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
  }
  return render_template('pages/show_artist.html', result=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.get(artist_id)
  artist.name = request.form.get('name')
  artist.city = request.form.get('city')
  artist.state = request.form.get('state')
  artist.phone = request.form.get('phone')
  artist.genres = request.form.getlist('genres')
  artist.image_link = request.form.get('image_link')
  artist.website_link = request.form.get('website_link')
  artist.facebook_link = request.form.get('facebook_link')
  artist.looking_for_venue = True if request.form.get('seeking_venue') == 'y' else False
  artist.seeking_description = request.form.get('seeking_description')
  
  db.session.commit()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # TODO: populate form with values from venue with ID <venue_id>
  venue = Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get(venue_id)
  venue.name = request.form.get('name')
  venue.city = request.form.get('city')
  venue.state = request.form.get('state')
  venue.address = request.form.get('address')
  venue.phone = request.form.get('phone')
  venue.genres = request.form.getlist('genres')
  venue.image_link = request.form.get('image_link')
  venue.website_link = request.form.get('website_link')
  venue.facebook_link = request.form.get('facebook_link')
  venue.looking_for_talent = True if request.form.get('seeking_talent') == 'y' else False
  venue.seeking_description = request.form.get('seeking_description')
  
  db.session.commit()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  
  try:
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    genres = request.form.getlist('genres')
    image_link = request.form.get('image_link')
    website_link = request.form.get('website_link')
    facebook_link = request.form.get('facebook_link')
    looking_for_venue = True if request.form.get('seeking_venue') == 'y' else False
    seeking_description = request.form.get('seeking_description','')
    my_artist = Artist.query.filter(Artist.phone == phone).first()
    if my_artist:
      flash('This phone number '+phone+' has already be taken')
      return render_template('pages/home.html')
    artist = Artist(name=name,city=city,state=state,phone=phone,genres=genres,image_link=image_link,website_link=website_link,facebook_link=facebook_link,looking_for_venue=looking_for_venue,seeking_description=seeking_description)
    # print(artist)
    db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + name + ' could not be listed.')
  finally:
    db.session.close()
  
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  # data = db.session.query(Show,Venue,Artist).all()
  data = Show.query.join(Venue,Artist).with_entities(
    Venue.name.label('venue_name'), 
    Artist.name.label('artist_name'), 
    Artist.image_link,
    Show.start_time,
    Show.venue_id,Show.artist_id).all()

  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }]
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  # I wanted to retrieve the information of the artists 
  # and venues to load them into the view but as it is mentioned 'do not touch'.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    venue_id = request.form.get('venue_id')
    artist_id = request.form.get('artist_id')
    start_time = request.form.get('start_time')
    
    show = Show(venue_id=venue_id,artist_id=artist_id,start_time=start_time)
    db.session.add(show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  
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
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
