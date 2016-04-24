#
# An egregiously simple interface to our Pg database, until we think
# of something better.
#
import psycopg2
import psycopg2.extras

def dbstring(**kwargs):
    # XXX Arg validation needed here. 
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

    def fetch_recs(self,query,*args):
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(query % args)
        return [dict(r) for r in cur.fetchall()]

    def fetchone(self,query,*args):
        recs = self.fetch_recs(query,*args)
        if len(recs) == 0: return None
        if len(recs) == 1: return recs[0] 
        raise ValueError("too many matches")

    # A simple accessor that allows us to test the above.
    def count_table(self,path):
        cur = self.conn.cursor()
        cur.execute("select count(*) from %s", path) 
        return cur.fetchone()[0]

