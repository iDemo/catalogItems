#!/usr/bin/env python

import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)


class Course(Base):

    __tablename__ = 'course'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)

    @property
    def serialize(self):

        return {
            'id': self.id,
            'name': self.name
        }


class CourseItem(Base):

    __tablename__ = 'course_item'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(1000))
    course_id = Column(Integer, ForeignKey('course.id'))
    course = relationship("Course")
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User")

    @property
    def serialize(self):

        return {
            'Course': self.course.name,
            'name': self.name,
            'description': self.description,
            'id': self.id
        }


#engine = create_engine("sqlite:///catalog.db")
engine = create_engine('postgresql://catalog:catalogpass@localhost/catalog')
Base.metadata.create_all(engine)
