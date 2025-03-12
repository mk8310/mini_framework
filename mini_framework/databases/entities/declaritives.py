from sqlalchemy.ext.declarative import declarative_base

BaseDBModel = declarative_base()


# 扩展BaseDBModel增加方to_dict

def db_model_to_dict(self):
    from mini_framework.databases.entities import to_dict
    return to_dict(self)


BaseDBModel.to_dict = db_model_to_dict
