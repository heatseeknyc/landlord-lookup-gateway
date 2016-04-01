#
# An egregiously simple interface to our Pg database, until we think
# of something better.
#
import psycopg2
import psycopg2.extras

def dbstring(**kwargs):
    # XXX Should really do some basic arg validation here.
    return "dbname=%(dbname)s user=%(user)s password=%(password)s" % kwargs

# An extremely simple wrapper for our Pg connection object, which abstracts
# some of the boilerplate (and paranoid error checkng / logging) around the
# extremely simple use cases specific to this project.  If you want anything
# more flexible, try using a real ORM.
class AgentBase(object):
    conn = None
    def __init__(self,**kwargs):
        s = dbstring(**kwargs) 
        self.conn = psycopg2.connect(s)

    def dict_cursor(self): 
        return self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # A convenience method which retuns a flat rowset (always of type dict)
    # based on a single argument (always presumed to be integer), abstracting
    # the boilerplate of checking the argument type, packing it into the query,
    # and paranoidly logging around these steps.
    #
    # Not particularly flexible -- but it makes our code a bit simpler, and 
    # importantly, projects against SQL injection.
    def fetch_recs(self,query,num):
        # print("::: arg = %s" % num);
        assert type(num) is int, "placeholder argument must be an integer"
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        # print("::: execute ..");
        cur.execute(query % num)
        # print("::: return ..");
        return [dict(r) for r in cur.fetchall()]

    # XXX Not safe against injection; needs validation on the arg.
    def count_table(self,path):
        cur = self.conn.cursor()
        cur.execute("select count(*) from %s" % path) 
        return cur.fetchone()[0]

