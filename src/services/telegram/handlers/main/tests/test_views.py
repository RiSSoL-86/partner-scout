from services.telegram.handlers.main.views import MainView

MARKUP = object()


def test_menu_message_renders_running_banner() -> None:
    """Render the main menu banner with the keyboard."""
    content = MainView.build_menu_message(keyboard=MARKUP)

    assert "Partner Scout bot is running" in content["text"]
    assert content["reply_markup"] is MARKUP
