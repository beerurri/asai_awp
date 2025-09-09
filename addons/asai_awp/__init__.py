from . import models
from . import controllers

def delete_from_awp_tasks_taken_by_users_rel(env):
    '''
    В проде этого быть не должно, иначе есть риск его (частично) уронить :)
    '''
    env.cr.execute('DROP TABLE IF EXISTS awp_tasks_taken_users_rel')