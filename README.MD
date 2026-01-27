## Verslag logica (overzicht) ##

## 1. Architectuur ##
- Routing en app-logica: `Webtechnologie/app.py`
- Database-laag (herbruikbare functies): `Webtechnologie/database.py`
- Modellen (User/Post): `Webtechnologie/models/user.py`, `Webtechnologie/models/post.py`
- Templates (UI): `Webtechnologie/templates/`
- Static assets (CSS, images): `Webtechnologie/static/`

## 2. Data en database ##
- Database: SQLite (`Webtechnologie/app.db`)
- Tabellen: `users`, `posts`, `post_likes`
- Init: `Webtechnologie/init_db.py` maakt schema aan en seedt test users

## 3. User flow (van database tot weergave) ##
- Login:
  - `app.py` haalt user via `database.get_user_by_email(...)`
  - `User.from_row(...)` zet de DB-row om naar een User object
  - User data komt in de session en wordt gebruikt in templates
- Profiel:
  - `app.py` haalt user via `get_db()` met directe queries
  - User object wordt als `profile_user` aan `profile/profile.html` gegeven
  - Template toont velden met `profile_user.username`, `profile_user.profile_photo`

## 4. Post flow (van database tot weergave) ##
- Feed:
  - `database.get_feed_posts(...)` haalt posts + like info
  - `Post.from_row(...)` zet rows om naar Post objecten
  - `feed/feed.html` gebruikt `post.username`, `post.media_path`, `post.like_count`
- Eigen posts:
  - `database.get_posts_by_user_id(...)` haalt posts op
  - `profile/profile.html` toont posts met `post.media_type`, `post.title`

## 5. CRUD acties ##
- Create post: `/posts/create` slaat upload + post data op
- Edit post: `/posts/<id>/edit` update titel/caption
- Delete post: `/posts/<id>/delete` verwijdert post en likes + file
- Likes: `/posts/<id>/like` togglet like en geeft nieuwe count terug

## 6. Templates en UI ##
- Templates gebruiken Jinja (`{{ }}`) om data te tonen
- Includes: `templates/includes/header.html` en `footer.html`
- CSS: centrale styles in `static/css/base.css` + pagina-specifiek

## 7. Belangrijkste routes ##
- `/` landing
- `/register`, `/login`, `/logout`
- `/profile`, `/profile/edit`
- `/feed`
- `/posts/new`, `/posts/create`, `/posts/<id>/edit`, `/posts/<id>/delete`
- `/posts/<id>/like`
- `/about`, `/help`, `/contact`
