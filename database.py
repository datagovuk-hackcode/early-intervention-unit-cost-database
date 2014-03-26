# coding: utf-8
from flask.ext.sqlalchemy import SQLAlchemy
import flask.ext.whooshalchemy as whooshalchemy
import cdecimal, datetime

from app import app

db = SQLAlchemy(app)

cumulative_modifier_lookup = {}

outcome_category_detail_link = db.Table(
    'outcome_category_detail_link',
    db.Model.metadata,
    db.Column('category_id',
        db.Integer,
        db.ForeignKey('outcome_category.id')
    ),
    db.Column('detail_id',
        db.Integer,
        db.ForeignKey('outcome_detail.id')
    )
)

class OutcomeCategory(db.Model):
    __tablename__ = 'outcome_category'
    __searchable__ = ['name']

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(30))
    details = db.relationship(
        'OutcomeDetail',
        secondary=outcome_category_detail_link,
        backref=db.backref(
            'categories',
            lazy='dynamic'
        ),
        lazy='dynamic'
    )

    def __repr__(self):
        return '<OutcomeCategory {0}: {1}>'.format(
            self.id,
            self.name
        )

    def __init__(self, name):
        self.name = name

    def toDict(self):
        return {
            'id': self.id,
            'name': self.name
        }

    @staticmethod
    def get_by_name(name):
        return OutcomeCategory.query.filter(OutcomeCategory.name == name).first()

    @staticmethod
    def get_by_id(id):
        return OutcomeCategory.query.filter(OutcomeCategory.id == id).first()

class OutcomeDetail(db.Model):
    __tablename__ = 'outcome_detail'
    __searchable__ = ['name']

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(50))

    def __repr__(self):
        return '<OutcomeDetail {0}: {1}>'.format(
            self.id,
            self.name
        )

    def __init__(self, name):
        self.name = name

    def toDict(self):
        return {
            'id': self.id,
            'name': self.name
        }

    @staticmethod
    def get_by_name(name):
        return OutcomeDetail.query.filter(OutcomeDetail.name == name).first()

    @staticmethod
    def get_by_id(id):
        return OutcomeDetail.query.filter(OutcomeDetail.id == id).first()

agency_link = db.Table(
    'agency_link',
    db.Model.metadata,
    db.Column('parent_id',
        db.Integer,
        db.ForeignKey('agency.id')
    ),
    db.Column('child_id',
        db.Integer,
        db.ForeignKey('agency.id')
    )
)

class Agency(db.Model):
    __tablename__ = 'agency'
    __searchable__ = ['name']

    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.Integer)
    name = db.Column(db.Unicode(50))
    children = db.relationship(
        'Agency',
        secondary=agency_link,
        backref=db.backref(
            'parents',
            lazy='dynamic'
        ),
        primaryjoin=id==agency_link.c.parent_id,
        secondaryjoin=id==agency_link.c.child_id,
        lazy='dynamic'
    )

    def __getattr__(self, name):
        if name == 'entries':
            if self.level == 1:
                return self.level_1_entries
            else:
                return self.level_2_entries
        else:
            raise AttributeError(
                "Agency instance has no attribute '{0}'".format(name)
            )

    def __repr__(self):
        return '<Level {0} Agency {1}: {2}>'.format(
            self.level,
            self.id,
            self.name
        )

    def __init__(self, name, level):
        self.name = name
        self.level = level

    def toDict(self):
        return {
            'id': self.id,
            'name': self.name,
            'level': self.level
        }

    @staticmethod
    def get_by_name(name):
        return Agency.query.filter(Agency.name == name).first()

    @staticmethod
    def get_by_id(id):
        return Agency.query.filter(Agency.id == id).first()

class Unit(db.Model):
    __tablename__ = 'unit'
    __searchable__ = ['name']

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(50))

    def __repr__(self):
        return '<Unit {0}: {1}>'.format(
            self.id,
            self.name
        )

    def __init__(self, name):
        self.name = name

    def toDict(self):
        return {
            'id': self.id,
            'name': self.name
        }

    @staticmethod
    def get_by_name(name):
        return Unit.query.filter(Unit.name == name).first()

    @staticmethod
    def get_by_id(id):
        return Unit.query.filter(Unit.id == id).first()

class GDP(db.Model):
    __tablename__ = 'gdp'

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer)
    perc_change = db.Column(db.Float)
    decimal_change = db.column_property(perc_change / 100)
    decimal_modifier = db.column_property(1 + (perc_change / 100))

    def __repr__(self):
        return '<GDP {0}/{1}: {2.2f}% change>'.format(
            self.year,
            str(self.year+1)[-2::],
            self.perc_change
        )

    def __init__(self, year, perc_change):
        self.year = year
        self.perc_change = perc_change

    def toDict(self):
        return {
            'id': self.id,
            'year': self.year,
            'perc_change': self.perc_change,
            'decimal_change': self.decimal_change,
            'decimal_modifier': self.decimal_modifier
        }

    @staticmethod
    def get_by_year(year):
        return GDP.query.filter(GDP.year == year).first()

    @staticmethod
    def get_cumulative_modifier(startyear, endyear):
        try:
            return cumulative_modifier_lookup[startyear][endyear]
        except KeyError:
            start = min(startyear, endyear)
            end = max(startyear, endyear)

            entries = GDP.query.filter(GDP.year > start).filter(GDP.year <= end).all()

            total = 1

            for entry in entries:
                total = total * entry.decimal_modifier

            if endyear < startyear:
                total = 1 / total

            try:
                cumulative_modifier_lookup[startyear][endyear] = total
            except KeyError:
                cumulative_modifier_lookup[startyear] = {}
                cumulative_modifier_lookup[startyear][endyear] = total

            return total

class Entry(db.Model):
    __tablename__ = 'entry'
    __searchable__ = ['details', 'source', 'comment']

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Unicode(15), nullable=False)
    details = db.Column(db.UnicodeText, nullable=False)
    cost = db.Column(db.Numeric(9,2), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    source = db.Column(db.UnicodeText, nullable=False)
    source_url = db.Column(db.UnicodeText)
    confidence = db.Column(db.Enum('High', 'Medium', 'Low'), nullable=False)
    comment = db.Column(db.UnicodeText)

    outcome_category_id = db.Column(
        db.Integer,
        db.ForeignKey('outcome_category.id'),
        nullable=False
    )
    outcome_category = db.relationship(
        'OutcomeCategory',
        backref=db.backref(
            'entries',
            lazy='dynamic'
        )
    )

    outcome_detail_id = db.Column(
        db.Integer,
        db.ForeignKey('outcome_detail.id'),
        nullable=False
    )
    outcome_detail = db.relationship(
        'OutcomeDetail',
        backref=db.backref(
            'entries',
            lazy='dynamic'
        )
    )

    level_1_agency_id = db.Column(
        db.Integer,
        db.ForeignKey('agency.id'),
        nullable=False
    )
    level_1_agency = db.relationship(
        'Agency',
        backref=db.backref(
            'level_1_entries',
            lazy='dynamic'
        ),
        foreign_keys=[level_1_agency_id]
    )

    level_2_agency_id = db.Column(
        db.Integer,
        db.ForeignKey('agency.id')
    )
    level_2_agency = db.relationship(
        'Agency',
        backref=db.backref(
            'level_2_entries',
            lazy='dynamic'
        ),
        foreign_keys=[level_2_agency_id]
    )

    unit_id = db.Column(
        db.Integer,
        db.ForeignKey('unit.id'),
        nullable=False
    )
    unit = db.relationship(
        'Unit',
        backref=db.backref(
            'entries',
            lazy='dynamic'
        )
    )

    parent_id = db.Column(
        db.Integer,
        db.ForeignKey('entry.id')
    )
    parent = db.relationship(
        'Entry',
        backref=db.backref(
            'children',
            lazy='dynamic'
        ),
        remote_side=[id]
    )

    def __getattr__(self, name):
        if name == 'current_cost':
            return (
                self.cost *
                cdecimal.Decimal(
                    GDP.get_cumulative_modifier(
                        self.year,
                        datetime.datetime.now().year
                    )
                )
            )
        elif name == 'name':
            return self.details
        else:
            raise AttributeError(
                "Entry instance has no attribute '{0}'".format(name)
            )

    def __repr__(self):
        return '<Entry {0}: {1} - {2}>'.format(
            self.id,
            self.code,
            self.details
        )

    def __init__(
        self,
        outcome_category,
        outcome_detail,
        code,
        details,
        level_1_agency,
        level_2_agency,
        unit,
        cost,
        year,
        source,
        source_url,
        confidence,
        comment,
        parent
    ):
        self.outcome_category = outcome_category
        self.outcome_detail = outcome_detail
        self.code = code
        self.details = details
        self.level_1_agency = level_1_agency
        self.level_2_agency = level_2_agency
        self.unit = unit
        self.cost = cost
        self.year = year
        self.source = source
        self.source_url = source_url
        self.confidence = confidence
        self.comment = comment
        self.parent = parent

    def toDict(self):
        return {
            'id': self.id,
            'outcome_category': self.outcome_category,
            'outcome_detail': self.outcome_detail,
            'code': self.code,
            'details': self.details,
            'level_1_agency': self.level_1_agency,
            'level_2_agency': self.level_2_agency,
            'unit': self.unit,
            'cost': self.cost,
            'year': self.year,
            'source': self.source,
            'source_url': self.source_url,
            'confidence': self.confidence,
            'comment': self.comment,
            'current_cost': self.current_cost,
            'parent_id': self.parent_id,
            'children_ids': [child.id for child in self.children]
        }

    @staticmethod
    def get_by_id(id):
        return Entry.query.filter(Entry.id == id).first()

whooshalchemy.whoosh_index(app, OutcomeCategory)
whooshalchemy.whoosh_index(app, OutcomeDetail)
whooshalchemy.whoosh_index(app, Agency)
whooshalchemy.whoosh_index(app, Unit)
whooshalchemy.whoosh_index(app, Entry)
