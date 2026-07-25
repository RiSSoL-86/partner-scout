from services.telegram.handlers.main.keyboards import MainKeyboard


def test_menu_keyboard_lists_sections() -> None:
    """Offer the companies, persons and exit entries in the main menu."""
    markup = MainKeyboard.build_menu_keyboard()

    labels = [button.text for row in markup.inline_keyboard for button in row]
    assert labels == ["Companies 📊", "Persons 👥", "Exit ❌"]
