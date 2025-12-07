### Gourmet Wiki — MVP Status Review and Roadmap

Last updated: 2025-12-07 03:16

#### What you have today (observed status)

- Core stack
  - Django 5.2, Django Allauth (email + Google), DRF, Crispy/DaisyUI, HTMX usage patterns in templates, Django-Vite, Debug Toolbar, Reversion (versioning), Formtools Wizard.
  - i18n enabled with `LocaleMiddleware` and German translations present (`app/locale/de`).
  - Deployed infra hints: `docker-compose*.yml`, `fly.toml`, `nginx/default.conf` — suggests containerized deploy with Nginx reverse proxy.

- Domain apps and capabilities
  - recipes
    - Models: `Recipe`, `RecipeIngredient`, `RecipePreparationStep` (with section headers), `RecipeImage`, `RecipeRating`.
    - Features: create/edit via multi-step wizard (formsets for ingredients, steps, images), rating, favorites, scaling ingredients by portions, cost calculation service, list/detail views, published flag.
    - Templates for partials and detail view present; HTMX endpoints for dynamically adding form rows.
  - ingredients
    - `Ingredient` model with slug; categories/nutrients scaffolding commented out (future nutrition ambitions).
  - menus
    - Menu app exists with URLs and views to collect recipes into courses; templates show a simple recipe slider and filtering.
  - users
    - Allauth integrated; custom middleware `HTMXLoginRedirectMiddleware`; user deletion confirm template; basic profile likely.
  - wiki
    - Basic wiki app with seed articles and templates. Potential for knowledge base around techniques.
  - pages/core
    - Site pages and enums (`CourseTypeChoice`, `SkillLevelChoice`, `UnitChoice`).

- UI/Frontend
  - DaisyUI theme through Crispy; Vite config in `app/vite.config.mjs`; HTMX partials for dynamic UX.

- Localization
  - German `.po` is extensive (auth, account, recipes copy). Language switching is enabled; a custom “ForceGerman” middleware is disabled to allow switching.

- Known issues/TODOs (from README and code comments)
  - README:
    - "Step Formset Order prerendering"
    - "Sometimes all Ingredients and / or Steps are removed (figure out why)"
    - "finish redesigning in recipe form" and elsewhere
  - Code hints:
    - Wizard debug prints and manual delete handling for formsets.
    - Nutrient and category models commented out — nutrition features incomplete.
    - Images currently optional; thumbnails exist but uploader in form is commented.
    - `dotenv` import in settings implies env setup; ensure `.env` is in place for SECRET_KEY/DEBUG etc.

#### MVP gaps and risks

- Reliability
  - Formset deletion/ordering bugs can cause data loss for ingredients/steps.
  - Lack of server-side validation around step sections vs steps may allow malformed sequences if bypassing form.

- UX
  - Wizard redesign unfinished; image upload is disabled in `RecipeForm` widgets.
  - Ingredient selection UX: likely free-text with on-the-fly Ingredient creation; needs autocomplete to deduplicate.

- Content/search/SEO
  - No full-text search or filters beyond basics; no sitemap or meta tags; no OpenGraph/Share images.

- Nutrition and costs
  - Nutrient model incomplete; cost calculation exists but depends on service inputs — cost sources unclear.

- Quality
  - Test coverage unclear; repository lacks explicit tests in listed paths.

- Security/abuse
  - Rate limiting middleware is commented out; public endpoints may be spammed.
  - Media validation for images (size/type) not visible in forms currently.

- Analytics/feedback
  - No analytics or basic event tracking noted.

#### Quick wins (1–2 days)

- Fix formset reliability
  - Reproduce and fix "Sometimes all Ingredients/Steps are removed" when editing wizard steps.
  - Ensure `can_delete` vs explicit delete checkbox handling is consistent; write a regression test.
  - Persist order client-side and validate unique, sequential order server-side.

- Unlock image uploads
  - Re-enable `thumbnail_image` widget; add basic server-side validation and automatic thumbnailing.

- Improve ingredient entry UX
  - Add autocomplete/typeahead for existing ingredients with debounced search endpoint.
  - Normalize ingredient name capitalization; prevent dupes by unique constraint + cleaning.

- Basic search & filters
  - Add keyword search and filters (course type, time, skill, is_published) to `RecipeListView`.

- Harden deployment basics
  - Document `.env` requirements; ensure SECRET_KEY set in prod; verify `ALLOWED_HOSTS` is not wildcard in prod.
  - Turn off Debug Toolbar in prod; add `SECURE_*` headers via Nginx and Django.

#### Prioritized roadmap (MVP → MLP)

P0 — Stabilize and polish MVP (this week)

- Form wizard reliability and UX
  - [ ] Resolve deletion bug that wipes ingredients/steps when saving between steps
  - [ ] Enforce step order; add drag-and-drop ordering with hidden order inputs
  - [ ] Re-enable image upload; show preview
  - [ ] Make "section header" rows visually distinct and validated server-side

- Search and discovery
  - [ ] Add search box with `q` across name, description, ingredients
  - [ ] Add filters: course type, skill, max total time, published only

- Publishing workflow
  - [ ] Only allow `is_published=True` if minimum fields populated (>=1 ingredient, >=1 step)
  - [ ] Add soft publish check in form clean

- Security/abuse protection
  - [ ] Enable simple global rate limit middleware for anon POSTs
  - [ ] CSRF and session settings review; set secure cookies in prod

- Basic analytics
  - [ ] Add privacy-friendly pageview events (e.g., Plausible/Umami) for recipe views and creates

P1 — Feature completeness (next 2–3 weeks)

- Menus
  - [ ] Finish course-based menus; allow printing/sharing menus
  - [ ] Scale menus by portions and aggregate ingredient shopping list export (CSV/PDF)

- Ingredient management
  - [ ] Ingredient merge tool for duplicates
  - [ ] Optional categories; prepare for future nutrition mapping

- Ratings and favorites
  - [ ] Prevent multiple ratings per user; show histogram; allow edit of rating
  - [ ] Favorite list page per user

- Media
  - [ ] Multiple images per recipe with primary flag; responsive srcsets; basic CDN caching headers

- Internationalization
  - [ ] Expose language switcher in navbar; audit templates for `trans` usage gaps
  - [ ] Translate ingredient and category names or decide on source-of-truth language

- Wiki integration
  - [ ] Link preparation steps keywords to wiki articles (hover cards)
  - [ ] Populate seed articles on basic techniques and equipment

P2 — Differentiators (next 1–2 months)

- Nutrition and costs
  - [ ] Implement `Nutrient`, `IngredientNutrient` models and minimal nutrition per recipe
  - [ ] Optional integration with USDA FDC or local dataset; nightly sync job
  - [ ] Cost calculation per ingredient with regional price tables; display cost per portion

- AI assistance (opt-in)
  - [ ] Convert free-text steps into structured actions/timers; propose section headers automatically
  - [ ] Suggest ingredient substitutions; auto-generate shopping list categories

- Collaboration and content quality
  - [ ] Draft → Publish workflow with private sharing links
  - [ ] Version history surfacing via `reversion`; show diffs between edits

#### Testing and quality

- Minimum test plan (start now)
  - [ ] Unit tests: models (ordering, average rating, scaling), form clean logic (sections vs steps)
  - [ ] Integration tests: wizard create/edit path including add/remove forms and image upload
  - [ ] View tests: list filters/search; toggle favorite; rate recipe
  - [ ] Security tests: anonymous cannot edit others’ recipes; publish guardrails

#### Performance and operations

- Caching and DB
  - [ ] Add `select_related/prefetch_related` on detail/list views to avoid N+1 (ingredients, steps, images)
  - [ ] Cache rendered recipe detail partials for anon users; invalidate on update

- Static/media
  - [ ] Use hashed static assets via Vite build in prod; verify Nginx caching and compression
  - [ ] Image resizing pipeline to limit original upload sizes

- Monitoring
  - [ ] Basic error tracking (Sentry or similar) and uptime checks

#### SEO and growth

- [ ] Add canonical URLs, OpenGraph/Twitter meta, and JSON-LD for recipes
- [ ] Sitemap.xml and robots.txt
- [ ] Social share buttons on recipe pages

#### Security checklist (prod)

- [ ] Configure `ALLOWED_HOSTS` narrowly for prod
- [ ] Set `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`
- [ ] Enable simple rate limiting middleware; Nginx rate limiting as a backstop
- [ ] Validate image MIME and size; sanitize HTML if enabling rich text later

#### Developer ergonomics

- [ ] Makefile or task scripts for: runserver, build assets, collectstatic, compilemessages, tests
- [ ] Sample `.env.example` with required variables (SECRET_KEY, DEBUG, DB, ALLOWED_HOSTS)

#### Dependencies and config

- Ensure `.env` usage: `python-dotenv` is imported in settings; verify dependency listed and `.env` present.
- Turn off `Debug Toolbar` and verbose Allauth logging in production.

---

If you want, I can convert this roadmap into GitHub issues with labels and milestones, or create a tracked checklist in this repo. Priority suggestion: start with P0 items to stabilize data entry, then P1 menus and shopping list to reach a compelling MVP for real-world use.
