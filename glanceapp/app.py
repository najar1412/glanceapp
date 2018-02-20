"""
glanceapp
3dsmax 2018
Contains allthe code
"""

import sys
import json
import base64
import urllib2

import MaxPlus
from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2 import QtCore


# TODO: separate 
# TODO: each widget returned by query results should
# have download buttons etc.
# TODO: figure out how to refactor classes to other modules.
# importing custom modules seems to be a problem?

class Config():
    def __init__(self):
        self.username = None
        self.password = None
        self.entry_point = None
        self.storage_url = None

    def validate(self):
        if self.username:
            return True

        else:
            return False


class GlanceLib():
    def query(self, string_query, filter=None):
        if filter:
            build_url_with_params = Config().entry_point + '?'+ 'query=' + string_query + '&' + 'filter=' + filter
        else:
            build_url_with_params = Config().entry_point + '?'+ 'query=' + string_query  + '&' + 'filter=geometry'

        request = urllib2.Request(build_url_with_params)
        base64string = base64.b64encode('{}:{}'.format(Config().username, Config().password))
        request.add_header("Authorization", "Basic {}".format(base64string))

        response = json.loads(urllib2.urlopen(request).read())

        if 'status' in response and response['status'] == 'success':
            return response['data']

        else:
            return []


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        if Config().validate():
            self.init_window()
        else:
            pass


    def _window_globals(self):
        self.setWindowTitle('glanceapp 0.01')
        self.setFixedWidth(450)


    def init_window(self):
        """Init window"""
        self._window_globals()
        widget_root = QtWidgets.QWidget(self)
        self.setCentralWidget(widget_root)

        # Window Components
        self.ui_comp_menubar()

        # Layout Components
        self.layout_container = QtWidgets.QVBoxLayout()
        self.layout_component_query_results = QtWidgets.QVBoxLayout()
        self.layout_component_query_results.addWidget(QueryResults())

        self.layout_container.addLayout(self.ui_comp_query())
        self.layout_container.addLayout(self.layout_component_query_results)
        widget_root.setLayout(self.layout_container)


    def ui_comp_menubar(self):
        """Window component - menubar"""
        # menuBar Actions
        file_name_settings_action_login = QtWidgets.QAction("&Login", self)
        file_name_settings_action_login.setShortcut("Ctrl+L")
        file_name_settings_action_login.setStatusTip('Login')
        # file_name_settings_action_login.triggered.connect(self.close_application)

        file_name_settings_action_config = QtWidgets.QAction("&Config", self)
        file_name_settings_action_config.setStatusTip('Config')
        # file_name_settings_action_config.triggered.connect(self.close_application)

        self.statusBar()

        mainMenu = self.menuBar()
        file_menu_settings = mainMenu.addMenu('&Settings')
        file_menu_settings.addAction(file_name_settings_action_login)
        file_menu_settings.addAction(file_name_settings_action_config)
        
        file_menu_collections = mainMenu.addMenu('&Collections')

    def ui_comp_query(self):
        """Window component - query box"""
        layout = QtWidgets.QGridLayout()
        
        self.query_input = QtWidgets.QLineEdit()
        self.query_input.returnPressed.connect(self.btn_action_query)
        layout.addWidget(self.query_input, 1, 0)
        
        btn_query = QtWidgets.QPushButton("Search")
        layout.addWidget(btn_query, 1, 1)
        btn_query.clicked.connect(self.btn_action_query)
        btn_query.setAutoDefault(True)


        return layout


    def remove_widgets(self, layout):
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().setParent(None)

    def btn_action_query(self):
        """Button Action: Query button"""
        self.remove_widgets(self.layout_component_query_results)
        
        self.layout_component_query_results.addWidget(QueryResults().query_result(query=self.query_input.text()))


class QueryResults(QtWidgets.QWidget):
    """query result widget"""
    def __init__(self, parent=None):
        super(QueryResults, self).__init__()

        self.grid = QtWidgets.QGridLayout()
        self.widget = QtWidgets.QWidget()
        self.layout = QtWidgets.QGridLayout(self.widget)

        # scroller
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)
        self.grid.addWidget(self.scroll, 3, 0)
        self.setLayout(self.grid)


    def query_result(self, items=None, query=None, layout=None, amount=8):
        """processes api results"""
        if layout == None:
            layout = self.layout

        # do query here
        if query:
            response = GlanceLib().query(query)

            for item in response:
                # print item
                Thumbnail(layout, item['item_thumb'])


        return self


class Thumbnail(QtWidgets.QWidget):
    """thumbnail widget"""
    def __init__(self, context, image_name):
        super(Thumbnail, self).__init__()
        self.context = context
        self.image_name = image_name

        self.context.addWidget(self.image())


    def image(self):
        url = Config().storage_url + self.image_name
        data = urllib2.urlopen(url).read()

        image = QtGui.QImage()
        image.loadFromData(data)

        lbl = QtWidgets.QLabel()
        lbl.setPixmap(QtGui.QPixmap(image))
        
        return lbl


    def overlay(self):
        pass


if __name__ == '__main__':
    app = QtWidgets.qApp
    GUI = MainWindow()
    GUI.show()

    sys.exit(app.exec_())
