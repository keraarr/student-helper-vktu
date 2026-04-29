from ..src.db import init_db, save_user_group, get_user_group

init_db()

save_user_group(123456, "13455", "23-ИСК-2")

user_group = get_user_group(123456)
print(user_group)
