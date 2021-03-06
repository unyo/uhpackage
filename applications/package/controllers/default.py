# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

@auth.requires_login()
def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html
    """
    # if student's UH id exists in the database, find all the packages related to their id
    # otherwise (uninitiated, no uh_id given to front desk)
    # what happens if there's no student id to begin with?
    #recent_packages= [{'id': 123, 'recieved_by': 'anon', 'recieved_date': '', 'delivered_date':'','delivered_by':''},{'id': 1123, 'recieved_by': 'anon', 'recieved_date': '', 'delivered_date':'','delivered_by':''}]
    if db(db.recipient.uh_id==auth.user.uh_id).select():
        user_record = db(db.recipient.uh_id==auth.user.uh_id).select().first()
        recent_packages = db(db.package.recipient==user_record.id).select(limitby=(0,30),orderby=~db.package.recieved_date)
        return dict(recent_packages=recent_packages)
    return dict()

@auth.requires_membership('Admin')    
def reset_data():
    form=FORM(LABEL('Please type "Yes, delete the entire database"',_id='confirm_label',_for='confirm'), INPUT(_name='confirm',_id='confirm',requires=IS_EQUAL_TO('Yes, delete the entire database',error_message='Confirmation sentence wrong')), INPUT(_type='submit',_value='KILL EVERYTHING'))
    if form.accepts(request.vars,session):
        for table_name in db.tables():
            db[table_name].truncate()
    return dict(form=form)
    
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()
