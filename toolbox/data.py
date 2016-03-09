import psycopg2
import psycopg2.extras

class database:
    """
    A little database wrapper
    """
    def __init__(self, host, dbname, user=None, password=None):
        args = {'dbname': dbname, 'host': host}
        self.connection = psycopg2.connect(**args)
        self.cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    def commit(self):
        self.connection.commit()

    def insert(self, table, dict):
        self.cursor.execute('INSERT INTO %s (%s) VALUES (%s) RETURNING *' % (table, ','.join(dict.keys()), ','.join(['%s'] * len(dict))), dict.values())
        return self.cursor.fetchone()

    def update(self, table, value_dict, pk_dict):
        sets = ['%s = %s' % (key, '%s') for key in value_dict.keys()]
        pksets = ['%s = %s' % (key, '%s') for key in pk_dict.keys()]
        q = 'UPDATE %s SET %s WHERE %s RETURNING *' % (table, ','.join(sets), ' AND '.join(pksets))
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
            for key, value in value_dict.iteritems():
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
            query = 'SELECT * FROM %s WHERE %s' % (table, ' AND '.join(clauses))
        else:
            query = 'SELECT * FROM %s' % table
        if order_by:
            if type(order_by) is list:
                query = query + ' ORDER BY %s' % ','.join(['%s %s' % (x[0],x[1]) for x in order_by])
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
            for key, value in pk_dict.iteritems():
                if type(value) is list:
                    clauses.append('%s = ANY(%s)' % (key, '%s'))
                else:
                    clauses.append('%s = %s' % (key, '%s'))
        wherestr = ' WHERE %s' % ' AND '.join(clauses) if len(clauses) > 0 else ''
        query = 'DELETE FROM %s %s' % (table, wherestr)
        self.cursor.execute(query, params)
        return self.cursor.rowcount

    def fetch_one(self, query, params=None):
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def fetch_all(self, query, params=None):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()