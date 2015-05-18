# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
#########################################################################

if request.env.web2py_runtime_gae:            # if running on Google App Engine
    from gluon.contrib.gae_memcache import MemcacheClient
    from gluon.contrib.memdb import MEMDB
    cache.memcache = MemcacheClient(request)
    cache.ram = cache.disk = cache.memcache
    db = DAL('gae')                           # connect to Google BigTable
                                              # optional DAL('gae://namespace')
    session.connect(request,response,MEMDB(cache.memcache))
    #session.connect(request, response, db = db) # and store sessions and tickets there
    ### or use the following lines to store sessions in Memcache
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))
else:                                         # else use a normal relational database
    db = DAL('sqlite://storage.sqlite')       # if not, use SQLite or other DB
## if no need for session
# session.forget()

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import *
mail = Mail()                                  # mailer
auth = Auth(globals(),db)                      # authentication/authorization
crud = Crud(globals(),db)                      # for CRUD helpers using auth
service = Service(globals())                   # for json, xml, jsonrpc, xmlrpc, amfrpc
plugins = PluginManager()

mail.settings.server = 'gae' or 'smtp.gmail.com:587'  # your SMTP server
mail.settings.sender = 'you@gmail.com'         # your email
mail.settings.login = 'username:password'      # your credentials or None

auth.settings.hmac_key = 'sha512:0521de3c-f670-4897-9994-a6e8937aa3ae'   # before define_tables()

db.define_table(
    auth.settings.table_user_name,
    Field('first_name',writable=False),
    Field('last_name',writable=False),
    Field('uh_id', unique=True, readable=False, writable=False),
    Field('username', unique=True, writable=False),
    Field('email', unique=True),
    Field('forwarding_address'),
    Field('password', 'password', readable=False),
    Field('registration_key', writable=False, readable=False),
    Field('reset_password_key', writable=False, readable=False),
    Field('registration_id', writable=False, readable=False), format="%(first_name)s %(last_name)s")

custom_auth_table = db[auth.settings.table_user_name] # get the custom_auth_table
custom_auth_table.first_name.requires = IS_NOT_EMPTY(error_message=auth.messages.is_empty)
custom_auth_table.last_name.requires = IS_NOT_EMPTY(error_message=auth.messages.is_empty)
custom_auth_table.password.requires = [IS_STRONG(), CRYPT()]
custom_auth_table.email.requires = [
  IS_EMAIL(error_message=auth.messages.invalid_email),
  IS_NOT_IN_DB(db, custom_auth_table.email)]
custom_auth_table.username.requires = IS_NOT_IN_DB(db, custom_auth_table.username)
custom_auth_table.uh_id.requires = IS_NOT_IN_DB(db, custom_auth_table.uh_id)

auth.settings.table_user = custom_auth_table # tell auth to use custom_auth_table

from applications.package.modules.cas_auth import CasAuth
auth.define_tables(username=True)                                           
auth.settings.login_form=CasAuth(                                           
   globals(),                                                              
   urlbase = "https://login.its.hawaii.edu/cas",                                 
   actions=['login','validate','logout'])

auth.settings.actions_disabled = ['register','verify_email','retrieve_username','request_reset_password','change_password']
auth.settings.mailer = mail                    # for user email verification
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.messages.verify_email = 'Click on the link http://'+request.env.http_host+URL('default','user',args=['verify_email'])+'/%(key)s to verify your email'
auth.settings.reset_password_requires_verification = True
auth.messages.reset_password = 'Click on the link http://'+request.env.http_host+URL('default','user',args=['reset_password'])+'/%(key)s to reset your password'
auth.settings.create_user_groups = False

#########################################################################
## If you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, uncomment and customize following
# from gluon.contrib.login_methods.rpx_account import RPXAccount
# auth.settings.actions_disabled=['register','change_password','request_reset_password']
# auth.settings.login_form = RPXAccount(request, api_key='...',domain='...',
#    url = "http://localhost:8000/%s/default/user/login" % request.application)
## other login methods are in gluon/contrib/login_methods
#########################################################################

crud.settings.auth = None                      # =auth to enforce authorization on crud

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

db.define_table('building',
    Field('name'),
    Field('street'),
    Field('city_state_zip'), format="%(name)s")

if not db(db.building.id > 0).select():
    db.building.bulk_insert([
        {'name': 'Frear Hall','street': '2569 Dole St','city_state_zip': 'Honolulu, HI 96822'}
    ])

db.define_table('recipient',
    Field('uh_id', unique=True, readable=False),
    Field('first_name'),
    Field('last_name'),
    Field('building','reference building'),
    Field('room'),
    Field('forwarding_address'), format="%(first_name)s %(last_name)s")

db.recipient.uh_id.requires = IS_NOT_IN_DB(db, 'recipient.uh_id')

db.define_table('package',
    Field('recipient','reference recipient'),
    Field('recieved_date','datetime',default=request.now),
    Field('delivered_date','datetime'),
    Field('recieved_by','reference auth_user'),
    Field('delivered_by','reference auth_user',requires=IS_NULL_OR(IS_IN_DB(db,'user_auth.id','%(first_name)s %(last_name)s'))))

if not db(db.auth_group.role=='Admin').select() and auth.user:
    admin_group = auth.add_group('Admin','System administrators which can add other administrators and desk workers')
    desk_group = auth.add_group('Desk Worker','People authorized to deliver and recieve packages')
    auth.add_membership(admin_group,auth.user.id)
    auth.add_membership(desk_group,auth.user.id)

# If there is a recipient without an ID and their name matches yours, associate the two accounts
if auth.user and not db(db.recipient.uh_id==auth.user.uh_id).select():
    test_new_user = db((db.recipient.uh_id==None) & (db.recipient.first_name==auth.user.first_name) & (db.recipient.last_name==auth.user.last_name)).select().first()
    if test_new_user:
        db.recipient[test_new_user.id] = dict(uh_id=auth.user.uh_id)
    del test_new_user

if auth.user and db(db.recipient.uh_id==auth.user.uh_id).select() and db(db.recipient.uh_id==auth.user.uh_id).select().first().forwarding_address!=auth.user.forwarding_address:
    db(db.recipient.uh_id==auth.user.uh_id).update(forwarding_address=auth.user.forwarding_address)
