from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__       = 'venues'

    id                  = db.Column(db.Integer, primary_key=True)
    name                = db.Column(db.String)
    city                = db.Column(db.String(120))
    state               = db.Column(db.String(120))
    address             = db.Column(db.String(120))
    phone               = db.Column(db.String(120))
    image_link          = db.Column(db.String(500))
    facebook_link       = db.Column(db.String(120))
    #missing fields
    genres              = db.Column(db.String(120))
    website_link        = db.Column(db.String(120))
    looking_for_talent  = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(256))
    shows = db.relationship("Show",backref="show", lazy=True)




    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artists'

    id                  = db.Column(db.Integer, primary_key=True)
    name                = db.Column(db.String)
    city                = db.Column(db.String(120))
    state               = db.Column(db.String(120))
    phone               = db.Column(db.String(120))
    genres              = db.Column(db.String(120))
    image_link          = db.Column(db.String(500))
    facebook_link       = db.Column(db.String(120))
    # missing fields
    website_link        = db.Column(db.String(120))
    looking_for_venue   = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(256))
    shows = db.relationship("Show",backref="artist_show", lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = 'shows'

  id            = db.Column(db.Integer,primary_key=True)
  venue_id      = db.Column(db.Integer, db.ForeignKey("venues.id"), nullable=False)
  artist_id     = db.Column(db.Integer, db.ForeignKey("artists.id"), nullable=False)
  start_time    = db.Column(db.DateTime, nullable=False)
