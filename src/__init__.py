from src.config import config
from src.db.user_controller import UserController, User
from src.hashes import SHA256Hasher

controller = UserController(config['db_path'])
if controller.find_user('admin') is None:
    controller.create_user(User(username='admin', password=SHA256Hasher(config['salt']).hexdigest(config['admin_password']), is_admin=True))
