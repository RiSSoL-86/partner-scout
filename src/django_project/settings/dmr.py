from dmr.settings import Settings

from django_project.authentication import AccessTokenAuth

DMR_SETTINGS: dict[Settings, tuple[AccessTokenAuth]] = {
    Settings.auth: (AccessTokenAuth(),),
}
