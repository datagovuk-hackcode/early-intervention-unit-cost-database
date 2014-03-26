# coding: utf-8
from flask import Blueprint, request, Response, url_for, send_file
import json, os
from database import *
from functools import wraps

api = Blueprint('api', __name__)

def get_dict(obj):
    if isinstance(obj, db.Model):
        return obj.toDict()
    elif isinstance(obj, cdecimal.Decimal):
        return round(float(obj), 2)
    else:
        return obj.__repr__()

def return_json(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        r = f(*args, **kwargs)
        return Response(json.dumps(r, default = (lambda x: get_dict(x)), sort_keys=True), content_type='text/json; charset=utf-8')
    return decorated_function

def error(error_type, message):
    return {
        'status': 'error',
        'error': error_type,
        'message': message
    }

def success(result):
    return {
        'status': 'success',
        'data': result
    }

@api.route('/api/agency/')
@return_json
def agencies():
    query = Agency.query

    try:
        search = request.args['search']
        query = query.whoosh_search(search)
    except KeyError:
        pass

    try:
        level = request.args['level']
        query = query.filter(Agency.level == level)
    except KeyError:
        pass

    return success(query.all())

@api.route('/api/agency/<int:id>')
@return_json
def agency(id):
    a = Agency.get_by_id(id)
    if a is not None:
        return success([a])
    else:
        return error('No Results', 'Agency with id {0} not found'.format(id))

@api.route('/api/agency/<int:id>/children')
@return_json
def agency_children(id):
    a = Agency.get_by_id(id)
    if a is not None:
        return success(a.children.all())
    else:
        return error('No Results', 'Agency with id {0} not found'.format(id))

@api.route('/api/agency/<int:id>/entries')
@return_json
def agency_entries(id):
    a = Agency.get_by_id(id)
    if a is not None:
        return success(a.entries.all())
    else:
        return error('No Results', 'Agency with id {0} not found'.format(id))

@api.route('/api/category/')
@return_json
def categories():
    query = OutcomeCategory.query

    try:
        search = request.args['search']
        query = query.whoosh_search(search)
    except KeyError:
        pass

    return success(query.all())

@api.route('/api/category/<int:id>')
@return_json
def category(id):
    c = OutcomeCategory.get_by_id(id)
    if c is not None:
        return success([c])
    else:
        return error('No Results', 'Category with id {0} not found'.format(id))

@api.route('/api/category/<int:id>/subcategories')
@return_json
def category_children(id):
    c = OutcomeCategory.get_by_id(id)
    if c is not None:
        return success(c.details.all())
    else:
        return error('No Results', 'Category with id {0} not found'.format(id))

@api.route('/api/category/<int:id>/entries')
@return_json
def category_entries(id):
    c = OutcomeCategory.get_by_id(id)
    if c is not None:
        return success(c.entries.all())
    else:
        return error('No Results', 'Category with id {0} not found'.format(id))

@api.route('/api/subcategory/')
@return_json
def subcategories():
    query = OutcomeDetail.query

    try:
        search = request.args['search']
        query = query.whoosh_search(search)
    except KeyError:
        pass

    return success(query.all())

@api.route('/api/subcategory/<int:id>')
@return_json
def subcategory(id):
    c = OutcomeCategory.get_by_id(id)
    if c is not None:
        return success([c])
    else:
        return error('No Results', 'Subcategory with id {0} not found'.format(id))

@api.route('/api/subcategory/<int:id>/parents')
@return_json
def subcategory_children(id):
    c = OutcomeCategory.get_by_id(id)
    if c is not None:
        return success(c.categories.all())
    else:
        return error('No Results', 'Subcategory with id {0} not found'.format(id))

@api.route('/api/subcategory/<int:id>/entries')
@return_json
def subcategory_entries(id):
    c = OutcomeDetail.get_by_id(id)
    if c is not None:
        return success(c.entries.all())
    else:
        return error('No Results', 'Subcategory with id {0} not found'.format(id))

@api.route('/api/unit/')
@return_json
def units():
    query = Unit.query

    try:
        search = request.args['search']
        query = query.whoosh_search(search)
    except KeyError:
        pass

    return success(query.all())

@api.route('/api/unit/<int:id>')
@return_json
def unit(id):
    c = Unit.get_by_id(id)
    if c is not None:
        return success([c])
    else:
        return error('No Results', 'Unit with id {0} not found'.format(id))

@api.route('/api/unit/<int:id>/entries')
@return_json
def unit_entries(id):
    c = Unit.get_by_id(id)
    if c is not None:
        return success(c.entries.all())
    else:
        return error('No Results', 'Unit with id {0} not found'.format(id))

@api.route('/api/entry/')
@return_json
def entries():
    query = Entry.query

    try:
        search = request.args['search']
        query = query.whoosh_search(search)
    except KeyError:
        pass

    return success(query.all())

@api.route('/api/entry/<int:id>')
@return_json
def entry(id):
    c = Entry.get_by_id(id)
    if c is not None:
        return success([c])
    else:
        return error('No Results', 'Entry with id {0} not found'.format(id))

@api.route('/api/gdp/')
@return_json
def gdps():
    return success(GDP.query.all())

@api.route('/api/gdp/year/<int:year>/')
@return_json
def gdp(year):
    return success([GDP.get_by_year(year)])

@api.route('/api/gdp/cumulative/start/<int:startyear>/end/<int:endyear>/')
@return_json
def gdp_cumulative(startyear, endyear):
    return success([GDP.get_cumulative_modifier(startyear, endyear)])

@api.route('/api/gdp/cumulative/start/<int:startyear>/')
@return_json
def gdp_cumulative_start(startyear):
    return success([{'year': year, 'modifer': GDP.get_cumulative_modifier(startyear, year)} for year in xrange(1989, 2019)])

@api.route('/api/gdp/cumulative/end/<int:endyear>/')
@return_json
def gdp_cumulative_end(endyear):
    return success([{'year': year, 'modifer': GDP.get_cumulative_modifier(year, endyear)} for year in xrange(1989, 2019)])

@api.route('/api/documentation')
def documentation():
    return send_file(
        os.path.join(os.path.dirname(__file__), 'documentation.txt'),
        'text/plain'
    )
