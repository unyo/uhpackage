# coding: utf8
# try something like
@auth.requires_membership('Admin')
def index(): 
    form = SQLFORM.factory(
        Field('user',requires=IS_IN_DB(db, 'auth_user.id', '%(uh_id)s - %(first_name)s %(last_name)s')),
        Field('group',requires=IS_IN_DB(db, 'auth_group.id', '%(role)s'))
        )
    if form.accepts(request.vars, session):
        membership = db.auth_membership.insert(user_id=request.vars.user,group_id=request.vars.group)
        response.flash = 'Added '+db.auth_user[request.vars.user].uh_id+' to '+db.auth_group[request.vars.group].role+' ('+str(membership)+')'
    permission_list = []
    for row in db(db.auth_membership.id>0).select():
        permission_list+=[{'id': row.id, 'name': '%(first_name)s %(last_name)s' % db.auth_user[row.user_id],'group': '%(role)s' % db.auth_group[row.group_id]}]
    return dict(form=form,permission_list=permission_list)

@auth.requires_membership('Admin')
def delete_membership():
    form=crud.delete(db.auth_membership,request.args(0),next=URL('index'))
    return dict(form=form)
