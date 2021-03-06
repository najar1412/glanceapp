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
    def query(self, string_query=None, filter=None):
        if filter:
            build_url_with_params = Config().entry_point + '?'+ 'filter=' + filter
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
        file_menu_settings_action_login = QtWidgets.QAction("&Login", self)
        file_menu_settings_action_login.setShortcut("Ctrl+L")
        file_menu_settings_action_login.setStatusTip('Login')
        # file_menu_settings_action_login.triggered.connect(self.close_application)

        file_menu_settings_action_config = QtWidgets.QAction("&Config", self)
        file_menu_settings_action_config.setStatusTip('Config')
        # file_menu_settings_action_config.triggered.connect(self.close_application)
        
        file_menu_collections_action_all = QtWidgets.QAction("&All", self)
        file_menu_collections_action_all.setStatusTip('Returns all Collections')
        file_menu_collections_action_all.triggered.connect(self.file_menu_collections_all)

        self.statusBar()

        mainMenu = self.menuBar()
        file_menu_settings = mainMenu.addMenu('&Settings')
        file_menu_settings.addAction(file_menu_settings_action_login)
        file_menu_settings.addAction(file_menu_settings_action_config)
        
        file_menu_collections = mainMenu.addMenu('&Collections')
        file_menu_collections.addAction(file_menu_collections_action_all)


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


    def file_menu_collections_all(self):
        """Menu Action: Collection: All"""
        self.remove_widgets(self.layout_component_query_results)

        self.layout_component_query_results.addWidget(QueryResults().query_result(filter='collection'))


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


    def query_result(self, query=None, layout=None, filter=None):
        """processes api results"""
        if layout == None:
            layout = self.layout

        # do query here
        if query:
            response = GlanceLib().query(query)

            for item in response:
                # print item
                Thumbnail(layout, item)
        
        if filter:
            response = GlanceLib().query(filter=filter)

            for item in response:
                # print item
                Thumbnail(layout, item)


        return self


class Thumbnail(QtWidgets.QWidget):
    """thumbnail widget"""
    def __init__(self, context, item_data):
        super(Thumbnail, self).__init__()
        self.context = context
        self.item_data = item_data

        self.context.addWidget(self.image())


    def image(self):
        container = QtWidgets.QWidget()
        container.setFixedSize(200, 200)

        url = Config().storage_url + self.item_data['item_thumb']
        # print(self.item_data)
        data = urllib2.urlopen(url).read()

        image = QtGui.QImage()
        image.loadFromData(data)
        
        if self.item_data['item_type'] == 'collection':
            painter = QtGui.QPainter()
            painter.begin(image)
            painter.fillRect(0, 0, 200, 40, QtGui.QColor(0, 0, 0, 160))
            painter.end()

            lbl = QtWidgets.QLabel()
            lbl.setPixmap(QtGui.QPixmap(image))
            
            lbl.setParent(container)
            
            phoneLabel = QtWidgets.QLabel(self.item_data['name'], self)
            phoneLabel.setMargin(5)
            phoneLabel.setWordWrap(True)
            phoneLabel.setParent(container)
            
        else:
            painter = QtGui.QPainter()
            painter.begin(image)
            painter.fillRect(0, 175, 200, 25, QtGui.QColor(0, 0, 0, 160))
            painter.end()

            lbl = QtWidgets.QLabel()
            lbl.setPixmap(QtGui.QPixmap(image))
            
            lbl.setParent(container)
            
            
            phoneLabel = QtWidgets.QLabel('Import | Proxy', self)
            phoneLabel.move(0, 175)
            phoneLabel.setMargin(5)
            # phoneLabel.setWordWrap(True)
            phoneLabel.setParent(container)


        return container



if __name__ == '__main__':
    app = QtWidgets.qApp
    GUI = MainWindow()
    GUI.show()

    sys.exit(app.exec_())
