#
# A trivial service used to test the uwsg+nginx configuration. 
#
from flask import Flask  
app = Flask(__name__) 

@app.route('/foobar')
def foobar():  
    return 'Woof!'

# This branch is only needed as a fallback, when running 
# the script from the shell (for troubleshooting purposes);  
# it won't be triggered when running under a WSGI. 
if __name__ == '__main__':  
    app.run()

