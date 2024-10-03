# make a seperate register page for service professional , rename column  add a new coloumn "SERVICE TYPE" 
# for eg "service name " = cleaning , "service description" = toilet cleaning

# in table PACKAGES : skill required is not nullable and will renamed to service name


# When you execute a SQLAlchemy query against a SQLite database, the return type depends on the type of query and the method used to execute it.

# For execute() method: When you use the execute() method, the return type is a CursorResult object. This object is an iterator that yields tuples, where each tuple represents a row in the result set.

# For scalar() method: If you use the scalar() method, the return type is a single value, which is the first element of the first row in the result set. If the result set is empty, None is returned.

# For fetchone() method: When you use the fetchone() method, the return type is a tuple representing the first row in the result set. If the result set is empty, None is returned.

# For fetchall() method: If you use the fetchall() method, the return type is a list of tuples, where each tuple represents a row in the result set.

