# coding: utf8
# try something like
@auth.requires_membership('Desk Worker')
def index():
    """
    Displays the Add Package form, which AJAX queries the recipient database for names and prefills
    the address should it already exist. If the whole combination (name + building + room) is not 
    found in the database, it'll add the recipient and the package, otherwise the package will be
    added and attributed to the recipient in the database (which will have their UH ID assigned on
    first pickup using deliver()
    """
    # Get the buildings
    building=['']
    for row in db(db.building.id>0).select():
        building += [OPTION(row.name,_value=row.name)]
    # Form
    form=FORM(LABEL('Name:',_id='name_label',_for='name'),INPUT(_name='name',_id='name',_value='',_placeholder='First Last'), LABEL('Building:',_id='building_label',_for='building'),SELECT(building,_name='building',_id='building',requires=IS_IN_DB(db,'building.name')), LABEL('Room:',_id='room_label',_for='room'),INPUT(_name='room',_id='room',_value='',_placeholder='420'), INPUT(_type='checkbox',_checked='unchecked',_name='new_record',_id='new_record'), LABEL('New record',_id='new_record_label',_for='new_record'), INPUT(_type='hidden',_name='recipient_id',_id='recipient_id',_value=''), INPUT(_type='submit'),_id='package')
    # Form processing - add and display.
    if form.accepts(request.vars, session):
        first_name=request.vars.name.split()[0].capitalize()
        last_name=request.vars.name.split()[-1].capitalize()
        building=db(db.building.name==request.vars.building).select().first()
        room=request.vars.room
        existing_recipient=db((db.recipient.first_name==first_name) & (db.recipient.last_name==last_name)).select().first()
        # If an existing recipient record exists, add a package with a reference to the record (and therefore the UH ID)
        if existing_recipient and not request.vars.new_record:
            if not (existing_recipient.building==building.id) or not (existing_recipient['room']==room):
                db.recipient[existing_recipient.id]=dict(building=building.id,room=room)
            package_id=db.package.insert(recipient=existing_recipient.id, recieved_date=request.now, recieved_by=auth.user.id)
        else:
            new_recipient=db.recipient.insert(first_name=first_name.capitalize(), last_name=last_name.capitalize(), building=building, room=room)
            package_id=db.package.insert(recipient=new_recipient, recieved_date=request.now, recieved_by=auth.user.id)
        response.flash = 'Package Added: '+str(package_id)
    recieved_results=[]
    recent_recieved = db(db.package.recieved_by==auth.user.id).select(orderby=~db.package.recieved_date,limitby=(0,10))
    for record in recent_recieved:
        recent_recipient=db.recipient[record.recipient]
        building=db.building[recent_recipient.building]
        recieved_results+=[{'id': record.id, 'first_name': recent_recipient.first_name, 'last_name': recent_recipient.last_name, 'building': building.name, 'room': recent_recipient.room}]
    return dict(form=form,recents=recieved_results)

@auth.requires_membership('Desk Worker')  
def recipient_search():
    """
    Searches the database for any first or last name starting with the request 'name' variable, returning dictonary 'results'
    """
    results = []
    if 'name' in request.vars:
        first_name=request.vars.name.split()[0]
        last_name=request.vars.name.split()[-1]
        if first_name==last_name or last_name=='':
            first_match = db(db.recipient.last_name==first_name.capitalize()).select(orderby=db.recipient.last_name).as_list()
            last_match = db(db.recipient.first_name==first_name.capitalize()).select(orderby=db.recipient.last_name).as_list()
            match=first_match+last_match
        else:
            match = db((db.recipient.last_name==last_name.capitalize()) & (db.recipient.first_name==first_name.capitalize())).select(orderby=db.recipient.last_name).as_list()
        for row in match:
            building = db.building[row['building']]
            results += [{'recipient_id': row['id'] , 'value': "%(first_name)s %(last_name)s" % row, 'building': building.name, 'room': row['room'], 'forwarding': row['forwarding_address']}]
    return dict(results=results)

@auth.requires_membership('Desk Worker')
def deliver():
    undelivered = db(db.package.delivered_date==None)
    if request.args(0):
        package_id = request.args(0)
    else:
        package_id = ''
    form = SQLFORM.factory(
        Field('package_id', requires=[IS_NOT_EMPTY(),IS_IN_DB(undelivered, 'package.id')], default=package_id),
        Field('uh_id', default='', requires=IS_NOT_EMPTY()),
        labels=dict(package_id="Package ID",uh_id="Student's UH ID"))
    if form.accepts(request.vars, session):
        if not db.recipient[db.package[request.vars.package_id].recipient].uh_id:
            db.recipient[db.package[request.vars.package_id].recipient] = dict(uh_id=request.vars.uh_id)
        if db.recipient[db.package[request.vars.package_id].recipient].uh_id==request.vars.uh_id:
            db.package[request.vars.package_id] = dict(delivered_by=auth.user.id,delivered_date=request.now)
            response.flash='Package '+request.vars.package_id+' delivered to student'
            undelivered = db(db.package.delivered_date==None)
        else:
            response.flash='UH ID was incorrect'
    return dict(form=form,undelivered=undelivered.select(orderby=db.package.id).as_list())

@auth.requires_membership('Desk Worker')
def check_id():
    package_id = request.vars.package_id
    recipient = db.package[package_id].recipient
    if not db.recipient[recipient].uh_id:
        db.recipient[recipient] = dict(uh_id=package_id)
    if db.recipient[recipient].uh_id!=package_id:
        response.flash='UH ID Incorrect'
        return dict()
    return dict()
