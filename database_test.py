import sqlite3
con = sqlite3.connect('lindow.db')

cur = con.cursor()

#cur.execute('CREATE TABLE dictionary(word,def,type,user)')
#res = cur.execute('DELETE FROM dictionary WHERE word="yup"')
#con.commit()
res = cur.execute('SELECT DISTINCT word FROM dictionary WHERE word GLOB \'[Zz]*\' ORDER BY word COLLATE NOCASE ASC')
print(res.fetchall())
#cur.execute('DELETE FROM dictionary')
#con.commit()
con.close()

#data = [
#    ('fester','definition 1','noun'),
#    ('fester','definition 2','noun'),
#    ('eat','definition','verb')
#]
#res = cur.executemany('INSERT INTO dictionary VALUES(?,?,?)', data)
#con.commit()

#res = cur.execute('SELECT * FROM dictionary WHERE word="fester"')
#print(res.fetchall())
'''
res = cur.execute('SELECT name FROM sqlite_master')
print(res.fetchone())

res = cur.execute("SELECT name FROM sqlite_master WHERE name='spam'")
print(res.fetchone())

#res = cur.execute(''''''
#    INSERT INTO movie VALUES
#        ('Monty Python and the Holy Grail', 1975, 8.2),
#        ('And Now for Something Completely Different', 1971, 7.5)
#'''''')
#con.commit()

res = cur.execute('SELECT * FROM movie')
print(res.fetchall())
'''