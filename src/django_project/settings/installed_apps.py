INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 3rd party apps
    "dmr",
    # project apps
    "apps.companies.apps.CompaniesConfig",
    "apps.persons.apps.PersonsConfig",
    "apps.scans.apps.ScansConfig",
    "apps.sources.apps.SourcesConfig",
    "apps.users.apps.UsersConfig",
]
