import aiomysql
import asyncio
import logging;logging.basicConfig(level=logging.INFO)
# from orm import Model,StringField,Integerfield


def log(sql, args=()):

    logging.info('SQL: %s' % sql)

class Field(object):
    def __init__(self,name,colmuns_type,primary_key):
        self.name=name
        self.colmuns_type=colmuns_type
        self.primary_key=primary_key

    def __str__(self):
        return '<%s:%s>' %(self.name,self.colmuns_type)

class StringField(Field):
    def __init__(self,name,primary_key=False):
        super(StringField,self).__init__(name,'varchar(20)',primary_key)


class IntegerField(Field):
    def __init__(self,name,primary_key=False):
        super(IntegerField,self).__init__(name,'bigint',primary_key)


class MetaModel(type):
    def __new__(cls, name, bases, attrs):
        mapping = {}
        if name == 'Model':
            return type.__new__(cls, name, bases, attrs)
        for k, v in attrs.items():
            if isinstance(v, Field):
                if v.primary_key:
                    primaryKey=v.name
                mapping[k] = v

        for k in mapping.keys():
            attrs.pop(k)

        attrs['__mapping__'] = mapping
        attrs['__primarykey__']=primaryKey
        attrs['__select__']='select ? from %s'%name
        attrs['__']

        return type.__new__(cls, name, bases, attrs)

class Model(dict,metaclass=MetaModel):
    def __init__(self,**kw):
        super(Model,self).__init__(**kw)
    def __getattribute__(self,key):
        return self[key]
    
    def __setattr__(self,key,values):
        self[key]=values
        print('stell eine Nue value %s in %s'%(values,key))

class user(Model):
    id=IntegerField('ID',primary_key=True)
    name=StringField('name')
    score=IntegerField('Score')




#建立一个连接池，以后不论下选择、修改，都可以直接从这里取链接
async def create_pool(loop,**kw):
    logging.info('create connect pool')
    global __pool
    __pool = await aiomysql.create_pool(
        host=kw.get('host', 'localhost'),
        port=kw.get('port', 3306),
        user=kw['user'],
        password=kw['password'],
        db=kw['db'],
        charset=kw.get('charset', 'utf8'),
        autocommit=kw.get('autocommit', True),
        maxsize=kw.get('maxsize', 10),
        minsize=kw.get('minsize', 1),
        loop=loop
    )

#从连接池中取出一个链接，用with，可以省去close。
#建立cursor方便选取。
#sql 代表了sql操作语句利于 select....
async def select(sql,args,size=0):
    log(sql,args)
    global __pool
    #异步建立连接
    async with __pool as conn:
        #异步建立cursor
        cur=await conn.cursor(aiomysql.DictCursor)
        await cur.execute(sql.replace('?','%s'),args or ())
        if size:
            rs= await cur.fetchmany(size)
        else:
            rs=await cur.fetchall()
        await cur.close()
    return rs
    logging.info('rows return %s' %len(re))

#删除插入修改：
async def execute(sql,args):
    log(sql,args)
    async with create_pool() as conn:
        cur=await conn.cursor(aiomysql.DictCursor)
    try:
        await cur.execute(sql.replace('?','%s'),args)
        affected=cur.rowcount
        await cur.close()
    except BaseException as e:
        raise
    return affected

# class user(Model):
#     __table__='user'

#     id=Integerfield(primary_key=True)
#     name=StringField()

