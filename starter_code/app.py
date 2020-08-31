#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate
from forms import *
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/proj1db'
# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    genres = db.Column("genres", db.ARRAY(db.String()), nullable=False)
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(250))
    seeking_talent = db.Column(db.Boolean, default=True)
    description = db.Column(db.String(250))
    shows = db.relationship('Show', backref='venue', lazy=True)

    def __init__(self, name, genres, address, city, state, phone, website, facebook_link, image_link,
                 seeking_talent=False, description=""):
        self.name = name
        self.genres = genres
        self.city = city
        self.state = state
        self.address = address
        self.phone = phone
        self.image_link = image_link
        self.facebook_link = facebook_link
        self.website = website
        self.seeking_talent = seeking_talent
        self.description = description

    def detailed_description(self):
        return {
          'id': self.id,
          'name': self.name,
          'genres': self.genres,
          'address': self.address,
          'city': self.city,
          'state': self.state,
          'phone': self.phone,
          'website': self.website,
          'facebook_link': self.facebook_link,
          'seeking_talent': self.seeking_talent,
          'description': self.description,
          'image-link': self.image_link
        }

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

    def __repr__(self):
        return f'<Venue {self.id} {self.name} {self.genres} {self.city} {self.state} {self.address} {self.phone} {self.image_link}' \
               f'{self.facebook_link}>'


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column("genres", db.ARRAY(db.String()), nullable=False)
    seeking_venue = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String(250))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows = db.relationship('Show', backref='artist', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

    def __init__(self, name, genres, city, state, phone, image_link, facebook_link,
                 seeking_venue=False, seeking_description=""):
        self.name = name
        self.genres = genres
        self.city = city
        self.state = state
        self.phone = phone
        self.facebook_link = facebook_link
        self.seeking_venue = seeking_venue
        self.seeking_description = seeking_description
        self.image_link = image_link

    def __repr__(self):
        return f'<Artist {self.id} {self.name} {self.city} {self.state} {self.phone} {self.genres} {self.image_link}' \
                   f'{self.facebook_link}>'

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, venue_id, artist_id, start_time):
        self.venue_id = venue_id
        self.artist_id = artist_id
        self.start_time = start_time

    def __repr__(self):
        return f'<Show {self.venue_id} {self.artist_id} {self.start_time}>'

    def artist_details(self):

        artist = db.session.query(Artist.name, Artist.image_link).filter(Artist.id == self.artist_id).one()
        show_add = {
                "artist_id": self.artist_id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": self.start_time.strftime('%m/%d/%Y')
        }

        return show_add

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format="EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format="EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    data = []

    venues_list = Venue.query.all()
    venues_unique = set()
    current_time = datetime.now().strftime('%Y-%m-%d %H:%S:%M')

    for venue in venues_list:
        venues_unique.add((venue.city, venue.state))

    for venue in venues_unique:
        data.append({
          "city": venue[0],
          "state": venue[1],
          "venues": []
        })

    for venue in venues_list:
        upcoming_shows = Show.query.filter(Show.venue_id == venue.id).filter(
            Show.start_time > current_time).all()

        for venue_location in data:
            if venue.state == venue_location['state'] and venue.city == venue_location['city']:
                venue_location['venues'].append({
                  "id": venue.id,
                  "name": venue.name,
                  "num_upcoming_shows": len(upcoming_shows)
                })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # search for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form['search_term']
    result = Venue.query.filter(Venue.name.ilike(f'%{search_term}%'))

    response = {
      "count": result.count(),
      "data": result
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    error = False
    new_show, past_show = [], []
    body = {}
    try:
        venue_query = db.session.query(Venue).filter(Venue.id == venue_id).one()
        venue_details = Venue.detailed_description(venue_query)
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new_shows = db.session.query(Show).filter(Show.venue_id == venue_id).filter(
            Show.start_time > current_time).all()

        for show in new_shows:
            new_show.append(show.artist_details())

        body = venue_details
        body["upcoming_shows"] = new_show
        body["upcoming_shows_count"] = len(new_show)
        past_shows = db.session.query(Show).filter(Show.venue_id == venue_id).filter(
            Show.start_time <= current_time).all()
        print(past_shows)
        for show in past_shows:
            past_show.append(show.artist_details())
        body["past_shows"] = past_show
        body["past_shows_count"] = len(past_show)
    except:
        error = True
        print(sys.exc_info())
    if error:
        abort(400)
    else:
        return render_template('pages/show_venue.html', venue=body)
    return render_template('errors/404.html')


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
    error = False
    form = VenueForm(request.form)
    try:
        new_venue = Venue(
          name = form.name.data,
          genres = form.genres.data,
          address = form.address.data,
          city = form.city.data,
          state = form.state.data,
          phone = form.phone.data,
          website = "",
          facebook_link = form.facebook_link.data,
          seeking_talent = False,
          description = "",
          image_link = ""
          )
        db.session.add(new_venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()
    if error:
        abort(400)
    else:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    error = False
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(400)
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    # query all artists in the database
    data = Artist.query.all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # search for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    results = Artist.query.filter(Artist.name.ilike('%' + request.form['search_term'] + '%'))
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data = []
    for result in results:
        data.append({
          "id": result.id,
          "name": result.name,
          "num_upcoming_shows": len(
            db.session.query(Show).filter(Show.artist_id == result.id).filter(Show.start_time > current_time).all()),
        })
    response = {
      "count": results.count(),
      "data": data
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    artist_query = db.session.query(Artist).get(artist_id)
    shows_artist = Show.query.filter_by(artist_id=artist_id).all()
    past_shows = []
    upcoming_shows = []
    current_time = datetime.now()

    for show in shows_artist:
        venue = db.session.query(Venue.name, Venue.image_link).filter(Venue.id == show.venue_id).one()
        data = {
              "venue_id": show.venue_id,
              "venue_name": venue.name,
              "venue_image_link": venue.image_link,
              "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
            }
        if show.start_time > current_time:
            upcoming_shows.append(data)
        else:
            past_shows.append(data)
    print(data["start_time"])
    data = {
      "id": artist_query.id,
      "name": artist_query.name,
      "genres": artist_query.genres,
      "city": artist_query.city,
      "state": artist_query.state,
      "phone": artist_query.phone,
      "facebook_link": artist_query.facebook_link,
      "image_link": artist_query.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows)
    }

    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)

    if artist:
        form.name.data = artist.name
        form.city.data = artist.city
        form.state.data = artist.state
        form.phone.data = artist.phone
        form.genres.data = artist.genres
        form.facebook_link.data = artist.facebook_link

    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    error = False
    form = ArtistForm()
    artist = Artist.query.get(artist_id)

    try:
        artist.name = form.name.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.genres = form.genres.data
        artist.facebook_link = form.facebook_link.data
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error has occurred!')
    else:
        flash('The Artist information have been successfully updated!')

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)

    if venue:
        form.name.data = venue.name
        form.city.data = venue.city
        form.state.data = venue.state
        form.phone.data = venue.phone
        form.address.data = venue.address
        form.genres.data = venue.genres
        form.facebook_link.data = venue.facebook_link
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    error = False
    form = VenueForm()
    venue = Venue.query.get(venue_id)

    try:
        venue.name = form.name.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.address = form.address.data
        venue.phone = form.phone.data
        venue.genres = form.genres.data
        venue.facebook_link = form.facebook_link.data
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error has occurred!')
    else:
        flash('The information about the Venue have been successfully updated!')
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
    error = False
    form = ArtistForm(request.form)
    try:
        name = form.name.data
        city = form.city.data
        state = form.state.data
        phone = form.phone.data
        genres = form.genres.data
        facebook_link = form.facebook_link.data
        image_link = form.image_link.data
        seeking_venue = False
        seeking_description = ""

        artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link,
                        image_link=image_link, seeking_venue=seeking_venue,
                        seeking_description=seeking_description)
        db.session.add(artist)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error has occurred! Artist ' + request.form['name'] + ' could not be listed.')
    else:
        # on successful db insert, flash success
        flash('The Artist ' + request.form['name'] + ' has been successfully listed!')

    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    shows_query = db.session.query(Show).join(Artist).join(Venue).all()

    data = []
    for show in shows_query:
        data.append({
          "venue_id": show.venue_id,
          "venue_name": show.venue.name,
          "artist_id": show.artist_id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
        })
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    error = False
    try:
        artist_id = request.form['artist_id']
        venue_id = request.form['venue_id']
        start_time = request.form['start_time']

        show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
        db.session.add(show)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error has occurred. The Show could not be added.')
    else:
        # on successful db insert, flash success
        flash('The Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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


# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
