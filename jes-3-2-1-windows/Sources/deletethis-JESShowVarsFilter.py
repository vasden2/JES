# this stuff has to be done last
# HACK ALERT - this is cool!!
# I need a list of all of the variables that are
# defined
v = vars()
for key in v.keys():
    __varsToFilter__[ key ] = 1

del v
del key

print __varsToFilter__
