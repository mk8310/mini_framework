from sqlalchemy.orm import Session


class MiniSession(Session):
    def commit(self):
        super(MiniSession, self).commit()

    def flush(self, objects=None):
        super(MiniSession, self).flush(objects)
