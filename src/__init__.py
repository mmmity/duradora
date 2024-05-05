from src import config
from src.db.user_controller import UserController, User
from src.hashes import SHA256Hasher

controller = UserController(config.DB_PATH)
if controller.find_user('admin') is None:
    controller.create_user(User(username='admin', password=SHA256Hasher(config.SALT).hexdigest(config.ADMIN_PASSWORD), is_admin=True))
