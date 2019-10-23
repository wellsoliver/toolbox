"""
    toolbox.data
    ~~~~~~~
    Data-munging utilities
"""
import psycopg2
import psycopg2.extras

from io import StringIO

class database:
    """A little database wrapper"""
    def __init__(self, dsn=None, **kwargs):
        if dsn:
            self.connection = psycopg2.connect(dsn)
        else:
            self.connection = psycopg2.connect(**kwargs)
        self.cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    def commit(self):
        self.connection.commit()
    
    def close(self):
        self.connection.close()

    def copy(self, table, data, sep='|'):
        """Bulk copy of a list of dicts"""
        if len(data) == 0:
            return 0
        keys = data[0].keys()
        stringdata = []
        for row in data:
            rowstr = sep.join([unicode(row[key] or '\n') for key in keys])
            stringdata.append(rowstr)
        count = len(stringdata)
        self.cursor.copy_from(StringIO('\n'.join(stringdata)),
            table, sep=sep, columns=keys)
        return count

    def insert(self, table, value_dict):
        if type(value_dict) is set:
            value_dict = list(value_dict)
        markers = ['%s'] * len(value_dict)
        if type(value_dict) is list:
            q = """INSERT INTO %s
                VALUES (%s) RETURNING *""" % (table, ','.join(markers))
            self.cursor.execute(q, value_dict)
        else:
            keys = value_dict.keys()
            q = """INSERT INTO %s (%s)
                VALUES (%s) RETURNING *""" % (table, ','.join(keys), ','.join(markers))
            self.cursor.execute(q, value_dict.values())
        return self.cursor.fetchone()

    def update(self, table, value_dict, pk_dict):
        sets = ['%s = %s' % (key, '%s') for key in value_dict.keys()]
        pksets = ['%s = %s' % (key, '%s') for key in pk_dict.keys()]
        q = """UPDATE %s
            SET %s
            WHERE %s RETURNING *""" % (table, ','.join(sets), ' AND '.join(pksets))
        params = value_dict.values() + pk_dict.values()
        self.cursor.execute(q, params)
        return self.cursor.fetchone()

    def upsert(self, table, value_dict, pk_dict):
        row = self.select(table, value_dict=pk_dict, fetch_one=True)
        if row:
            return self.update(table, value_dict, pk_dict)
        else:
            return self.insert(table, value_dict)

    def select(self, table, value_dict=None, order_by=None, fetch_one=False):
        clauses = []
        params = []
        if value_dict:
            for key, value in value_dict.items():
                if type(value) is set:
                    value = list(value)
                if type(value) is list:
                    clauses.append('%s = ANY(%s)' % (key, '%s'))
                elif value is None:
                    clauses.append('%s IS NULL' % key)
                else:
                    clauses.append('%s = %s' % (key, '%s'))
                params.append(value)
        if len(clauses) > 0:
            query = """SELECT *
                FROM %s WHERE %s""" % (table, ' AND '.join(clauses))
        else:
            query = 'SELECT * FROM %s' % table
        if order_by:
            if type(order_by) is list:
                ordering = ['%s %s' % (x[0],x[1]) for x in order_by]
                query = query + ' ORDER BY %s' % ','.join(ordering)
            elif type(order_by) is tuple:
                query = query + ' ORDER BY %s' % ' '.join(order_by)
        self.cursor.execute(query, params)
        if fetch_one:
            return self.cursor.fetchone()
        return self.cursor.fetchall()

    def delete(self, table, pk_dict=None):
        clauses = []
        params = None
        if pk_dict:
            params = pk_dict.values()
            for key, value in pk_dict.items():
                if type(value) is list:
                    clauses.append('%s = ANY(%s)' % (key, '%s'))
                else:
                    clauses.append('%s = %s' % (key, '%s'))
        wherestr = ' WHERE %s' % ' AND '.join(clauses) if len(clauses) > 0 else ''
        query = 'DELETE FROM %s %s' % (table, wherestr)
        self.cursor.execute(query, params)
        return self.cursor.rowcount

    def fetchone(self, query, params=None):
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def fetchall(self, query, params=None):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()


def placeholders(params, holder='%s', as_string=True):
    """Returns list of query placeholders or comma-delimited
    string if as_string=True
    """
    l = [holder] * len(params)
    if as_string:
        return ','.join(l)
    return l


def rescale(value, old_min, old_max, new_min, new_max):
    """Linear re-scaling of a value from an old range to a new"""
    orange = (old_max -old_min)
    nrange = (new_max - new_min)
    return (((value - old_min) * nrange) / orange) + new_min

