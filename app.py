from modules.db import init_db, ensure_settings
from modules.auth import login_required
from modules.dashboard import render_dashboard


def main():
    init_db()
    ensure_settings()
    user = login_required()
    render_dashboard(user)


if __name__ == "__main__":
    main()
