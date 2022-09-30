import sys

from PyQt5.QtWidgets import QApplication

from views import MainApp


def main(args):
    app = QApplication(args)
    ex = MainApp(
        title='ActivityWatchTimeTracker',
        left=100,
        top=100,
        height=500,
    )
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main(sys.argv)