# coding: utf-8
from flask import Blueprint, request, url_for, render_template, redirect
import json, os
from database import *
from functools import wraps

browser = Blueprint('browser', __name__)

@browser.route('/')
def index():
    return redirect(url_for('browser.home'))

@browser.route('/browser/')
def home():
    return render_template('home.html')

@browser.route('/browser/agency/')
def agencies():
    query = Agency.query

    try:
        search = request.args['search']
        if search != '':
            query = query.whoosh_search(search)
    except KeyError:
        pass

    try:
        level = request.args['level']
        if level != 'any':
            query = query.filter(Agency.level == level)
    except KeyError:
        pass

    return render_template(
        'search.html',
        results=query.all(),
        showlevel=True,
        title="Agencies",
        result_url='browser.agency',
        search_url='browser.agencies'
    )

@browser.route('/browser/agency/<int:id>')
def agency(id):
    a = Agency.get_by_id(id)
    if a is not None:
        return render_template(
            'item.html',
            item=a,
            showlevel=True,
            title="Agency",
            related=("children" if a.level == 1 else "parents"),
            related_title=("Children" if a.level == 1 else "Parents"),
            related_url='browser.agency'
        )
    else:
        return render_template('404.html'), 404

@browser.route('/browser/category/')
def categories():
    query = OutcomeCategory.query

    try:
        search = request.args['search']
        if search != '':
            query = query.whoosh_search(search)
    except KeyError:
        pass

    return render_template(
        'search.html',
        results=query.all(),
        showlevel=False,
        title="Categories",
        result_url='browser.category',
        search_url='browser.categories'
    )

@browser.route('/browser/category/<int:id>')
def category(id):
    c = OutcomeCategory.get_by_id(id)
    if c is not None:
        return render_template(
            'item.html',
            item=c,
            showlevel=False,
            title="Category",
            related="details",
            related_title="Subcategories",
            related_url='browser.subcategory'
        )
    else:
        return render_template('404.html'), 404

@browser.route('/browser/subcategory/')
def subcategories():
    query = OutcomeDetail.query

    try:
        search = request.args['search']
        if search != '':
            query = query.whoosh_search(search)
    except KeyError:
        pass

    return render_template(
        'search.html',
        results=query.all(),
        showlevel=False,
        title="Subcategories",
        result_url='browser.subcategory',
        search_url='browser.subcategories'
    )

@browser.route('/browser/subcategory/<int:id>')
def subcategory(id):
    c = OutcomeCategory.get_by_id(id)
    if c is not None:
        return render_template(
            'item.html',
            item=c,
            showlevel=False,
            title="Subcategory",
            related="categories",
            related_title="Parent Categories",
            related_url='browser.category'
        )
    else:
        return render_template('404.html'), 404

@browser.route('/browser/unit/')
def units():
    query = Unit.query

    try:
        search = request.args['search']
        if search != '':
            query = query.whoosh_search(search)
    except KeyError:
        pass

    return render_template(
        'search.html',
        results=query.all(),
        showlevel=False,
        title="Units",
        result_url='browser.unit',
        search_url='browser.units'
    )

@browser.route('/browser/unit/<int:id>')
def unit(id):
    u = Unit.get_by_id(id)
    if u is not None:
        return render_template(
            'item.html',
            item=u,
            showlevel=False,
            title="Unit",
            related=False
        )
    else:
        return render_template('404.html'), 404

@browser.route('/browser/entry/')
def entries():
    query = Entry.query

    try:
        search = request.args['search']
        if search != '':
            query = query.whoosh_search(search)
    except KeyError:
        pass

    return render_template(
        'search.html',
        results=query.all(),
        showlevel=False,
        title="Entries",
        result_url='browser.entry',
        search_url='browser.entries'
    )

@browser.route('/browser/entry/<int:id>')
def entry(id):
    e = Entry.get_by_id(id)
    if e is not None:
        return render_template('entry.html', entry=e, round=round)
    else:
        return render_template('404.html'), 404

@browser.route('/browser/gdp')
def gdp():
    GDPs = {gdp.year: gdp.decimal_modifier for gdp in GDP.query.all()}

    def get_modifier(start, end):
        total = 100

        if start <= end:
            for x in xrange(start+1, end+1):
                total = total * GDPs[x]
        else:
            for x in xrange(end+1, start+1):
                total = total / GDPs[x]

        return round(total, 2)

    table = {start: {end: get_modifier(start, end) for end in xrange(1989, 2018)} for start in xrange(1989, 2018)}

    return render_template('gdp.html', table=table)
