from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Course, CourseItem

#engine = create_engine('sqlite:///catalog.db')
engine = create_engine('postgresql://catalog:catalogpass@localhost/catalog')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


user = User(name="AbdulRahman Alothaim", email="ar.alothaim@gmail.com")
session.add(user)
session.commit()


course1 = Course(name="Entree")
session.add(course1)
session.commit()

course11 = CourseItem(name="Kabocha Squash Gnocchi",
                      description="Switch out potatoes with kabocha squash " +
                                  "for a healthier gnocchi that's still " +
                                  "packed with creamy, savory deliciousness.",
                      course_id="1",
                      user_id="1")
session.add(course11)
session.commit()

course12 = CourseItem(name="Egg Yolk Ravioli",
                      description="Stuffed with cheesy spinach " +
                                  "and a runny egg yolk, this freshly " +
                                  "made ravioli is perfect for brunch.",
                      course_id="1",
                      user_id="1")
session.add(course12)
session.commit()

course13 = CourseItem(name="Oprah Pasta",
                      description="For International Women's Day, " +
                                  "Jax is throwing together a stunning " +
                                  "pasta dish inspired by Oprah.",
                      course_id="1",
                      user_id="1")
session.add(course13)
session.commit()


course2 = Course(name="Main Dishes")
session.add(course2)
session.commit()

course21 = CourseItem(name="BOMBAY SLOPPY JOES",
                      description="A popular street food in " +
                                  "India- Kheema Pav is ground meat " +
                                  "(lamb or beef) cooked in a sauce of " +
                                  "tomatoes, ginger-garlic, onions and " +
                                  "fragrant ground spices, served with " +
                                  "lightly toasted and buttered buns. It's " +
                                  "Bombay's (Mumbai's) version of the " +
                                  "Sloppy Joe!",
                      course_id="2",
                      user_id="1")
session.add(course21)
session.commit()

course22 = CourseItem(name="SWEET & SOUR SALMON IN FOIL PACKETS",
                      description="Sweet and Sour Salmon is foil " +
                      "packets: Easy and packed full of flavor with " +
                      "sweet pineapple and bright peppers",
                      course_id="2",
                      user_id="1")
session.add(course22)
session.commit()

course23 = CourseItem(name="LEMON HERB COUSCOUS WITH ALMONDS",
                      description="This light and lemony couscous " +
                      "is the perfect side dish alternative when " +
                      "you are bored of rice or pasta!",
                      course_id="2",
                      user_id="1")
session.add(course23)
session.commit()


course3 = Course(name="Desert")
session.add(course3)
session.commit()

course31 = CourseItem(name="Ferrero Rocher Cheesecake Slice",
                      description="Say no to drugs. Say yes " +
                                  "to this Ferrero Rocher cheesecake.",
                      course_id="3",
                      user_id="1")
session.add(course31)
session.commit()

course32 = CourseItem(name="Coffee, Nuts and Caramel Cake",
                      description="Life moto: Always save room for dessert.",
                      course_id="3",
                      user_id="1")
session.add(course32)
session.commit()

course33 = CourseItem(name="Cinnamon Roll S'Mores",
                      description="Love s'mores, but " +
                                  "hate the outdoors? Problem, meet solution.",
                      course_id="3",
                      user_id="1")
session.add(course33)
session.commit()


print "Data has been inserted into Catalog.db"
