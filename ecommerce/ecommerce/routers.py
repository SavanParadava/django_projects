class Router:

    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'store':
            return 'store_db'
        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'store':
            return 'store_db'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        db_obj1 = 'store_db' if obj1._meta.app_label == 'store' else 'default'
        db_obj2 = 'store_db' if obj2._meta.app_label == 'store' else 'default'

        if db_obj1 == db_obj2:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'store':
            return db == 'store_db'
        
        if db == 'store_db':
            return False
        
        return db == 'default'