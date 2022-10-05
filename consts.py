REMEMBER_ME_FILE_PATH = './env/user.pkl'

START_ICON_PATH = './assets/play_icon_16.png'
PAUSE_ICON_PATH = './assets/pause_icon_16.png'

HIDDEN_EYE_ICON_PATH = './assets/unhidden_eye.png'
UNHIDDEN_EYE_ICON_PATH = './assets/hidden_eye.png'

OUTPUT_DIR = './run'

PROJECTS_LISTWIDGET_STYLESHEET = """
    QListWidget {
        background: palette(window);
        border: none;
        color: black;
        align-items: center;
        align: center;
        padding: 3px;
    }
    QListWidget::item {
        border-style: solid;
        border-width: 1px;
        border-color: black;
        border-radius: 5px;
        margin-right: 3px;
        color: black;
        align-items: center;
        align: center;
        padding: 3px;
    }
    QListWidget::item:hover {
        border-color: green;
}"""
