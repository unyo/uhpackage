# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.title = request.application
response.subtitle = T('Is it here yet?')

#http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Cody Moniz'
response.meta.description = 'Helps students track front desk packages for the University of Hawaii dormitories'
response.meta.keywords = 'uh, manoa, packages, front desk'
response.meta.generator = 'Web2py Enterprise Framework'
response.meta.copyright = 'Copyright 2007-2010'


##########################################
## this is the main application menu
## add/remove items as required
##########################################

response.menu = [
    ('Home', False, URL('default','index'))
    ]

if auth.has_membership('Desk Worker'):
    response.menu += [
        ('Desk Worker', False, URL('desk','index'), [
            ('Add Package', False, URL('desk','index')),
            ('Deliver Package', False, URL('desk','deliver'))
        ])
    ]

if auth.has_membership('Admin'):
    response.menu += [
        ('Admin', False, URL('admin','index'), [
            ('Manage Staff', False, URL('admin','index')),
            ('Reset DB', False, URL('default','reset_data'))
        ])
    ]
##########################################
## this is here to provide shortcuts
## during development. remove in production
##
## mind that plugins may also affect menu
##########################################

#########################################
## Make your own menus
##########################################
if auth.has_membership('Admin') and not request.env.web2py_runtime_gae:
    response.menu+=[
        (T('This App'), False, URL('admin', 'default', 'design/%s' % request.application),
         [
                (T('Controller'), False,
                 URL('admin', 'default', 'edit/%s/controllers/%s.py' \
                         % (request.application,request.controller=='appadmin' and
                            'default' or request.controller))),
                (T('View'), False,
                 URL('admin', 'default', 'edit/%s/views/%s' \
                         % (request.application,response.view))),
                (T('Layout'), False,
                 URL('admin', 'default', 'edit/%s/views/layout.html' \
                         % request.application)),
                (T('Stylesheet'), False,
                 URL('admin', 'default', 'edit/%s/static/base.css' \
                         % request.application)),
                (T('DB Model'), False,
                 URL('admin', 'default', 'edit/%s/models/db.py' \
                         % request.application)),
                (T('Menu Model'), False,
                 URL('admin', 'default', 'edit/%s/models/menu.py' \
                         % request.application)),
                (T('Database'), False,
                 URL(request.application, 'appadmin', 'index')),

                (T('Errors'), False,
                 URL('admin', 'default', 'errors/%s' \
                         % request.application)),

                (T('About'), False,
                 URL('admin', 'default', 'about/%s' \
                         % request.application)),

                ]
       )]
