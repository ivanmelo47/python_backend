from app.db.base import Base
from app.db.session import engine
from app.modules.roles.models import role_model as roles_models  # noqa: F401
from app.modules.products.models import product_model as products_models  # noqa: F401
from app.modules.users.models import user_model as users_models  # noqa: F401


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
