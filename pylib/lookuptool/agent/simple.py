import psycopg2.extras
from nychpd.agent.base import AgentBase

class SimpleAgent(AgentBase):
    '''
    A simple test agent which simply returns a list of registration recs 
    corresponding to a given BBL (which in general are many-to-one).
    '''
    def get_contacts(self,bbl):
        assert type(bbl) is int, "BBL argument must be an integer"
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("select * from hard.registrations where bbl = %d;" % bbl);
        recs = [dict(r) for r in cur.fetchall()]
        return recs



