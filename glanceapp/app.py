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


# TODO: needs a more responsive display.
# scrollarea for query results
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


class WidgetBuilder():
    def __init__(self, context):
        self.context = context


    def thumbnail(self, image_name, column=0):
        url = Config().storage_url + image_name

        data = urllib2.urlopen(url).read()
        image = QtGui.QImage()
        image.loadFromData(data)

        # thumbnail_widget = QtWidgets.QWidget()
        
        lbl = QtWidgets.QLabel()
        lbl.setPixmap(QtGui.QPixmap(image))
        
        self.context.addWidget(lbl)

        if column == 0:
            self.context.addWidget(lbl)
            self.context

        else:
            self.context.addWidget(lbl, 0, 1)


class GlanceLib():
    def __init__(self, context):
        self.context = context


    def query(self, string_query):
        build_url_with_params = Config().entry_point + '?'+ 'query=' + string_query
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
            self.config_invalid_window()


    def _window_globals(self):
        self.setWindowTitle('glanceapp 0.01')
        self.setFixedWidth(450)


    def config_invalid_window(self):
        """config checker window"""
        # Window Components
        self._window_globals()
        self._window_component_menubar()
        widget_root = QtWidgets.QWidget(self)
        
        self.setCentralWidget(widget_root)

        # Layout Components
        self.layout_container = QtWidgets.QVBoxLayout()
        self.layout_component_query = QtWidgets.QGridLayout()
        self.layout_component_query_results = QtWidgets.QGridLayout()
        
        self.layout_container.addLayout(self.layout_component_query)
        self.layout_container.addLayout(self.layout_component_query_results)
        widget_root.setLayout(self.layout_container)
        
        query_input = QtWidgets.QLabel()
        query_input.setText('Invalid config.')
        self.layout_component_query_results.addWidget(query_input)


    def init_window(self):
        """First time run window"""
        # Window Components
        self._window_globals()
        self._window_component_menubar()
        widget_root = QtWidgets.QWidget(self)

        self.setCentralWidget(widget_root)

        # Layout Components
        self.layout_container = QtWidgets.QVBoxLayout()
        self.layout_component_query = QtWidgets.QGridLayout()
        self.layout_component_query_results = QtWidgets.QVBoxLayout()
        self.layout_component_query_results.addWidget(QueryResults())

        self.layout_container.addLayout(self.layout_component_query)
        self.layout_container.addLayout(self.layout_component_query_results)
        widget_root.setLayout(self.layout_container)

        # layout content
        self._widget_group_query(self.layout_component_query)
        # self._widget_group_query_results()


    def _window_component_menubar(self):
        # menuBar Actions
        extractAction = QtWidgets.QAction("&Login", self)
        extractAction.setShortcut("Ctrl+L")
        extractAction.setStatusTip('Login')
        # extractAction.triggered.connect(self.close_application)

        menu_item_config = QtWidgets.QAction("&Config", self)
        menu_item_config.setStatusTip('Config')
        # menu_item_config.triggered.connect(self.close_application)

        self.statusBar()

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&Settings')
        fileMenu.addAction(extractAction)
        fileMenu.addAction(menu_item_config)


    def _widget_group_query(self, layout):
        self.query_input = QtWidgets.QLineEdit()
        layout.addWidget(self.query_input, 1, 0)
        
        btn_query = QtWidgets.QPushButton("Search...")
        layout.addWidget(btn_query, 1, 1)
        btn_query.clicked.connect(self.btn_click_widget_group_query)


    def _widget_group_query_results(self, items=None, amount=10):
        if items:
            count = 0
            for item in items:
                if count < amount:
                    if count % 2 == 0:
                        WidgetBuilder(self.layout_component_query_results).thumbnail(item['item_thumb'])

                    else:
                        WidgetBuilder(self.layout_component_query_results).thumbnail(item['item_thumb'], column=0)

                    count += 1

        else:
            for index, _ in enumerate(range(8)):
                if index % 2 == 0:
                    WidgetBuilder(self.layout_component_query_results).thumbnail('001_ftp1sQ_thumbnail.jpg')

                else:
                    WidgetBuilder(self.layout_component_query_results).thumbnail('001_ftp1sQ_thumbnail.jpg', column=0)


    def btn_click_widget_group_query(self):
        # reset layout

        for i in reversed(range(self.layout_component_query_results.count())): 
            self.layout_component_query_results.itemAt(i).widget().setParent(None)
        self.layout_container.addLayout(self.layout_component_query_results)

        
        all_items = GlanceLib(self.layout_component_query_results).query(self.query_input.text())
        self._widget_group_query_results(items=all_items)
        QueryResults()._widget_group_query_results(items=all_items)


class QueryResults(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(QueryResults, self).__init__()

        grid = QtWidgets.QGridLayout()

        self.widget = QtWidgets.QWidget()

        # set the widget as parent of its own layout
        self.layout = QtWidgets.QGridLayout(self.widget)

        self._widget_group_query_results(layout=self.layout)

        self.scroll = QtWidgets.QScrollArea()
        # need this so that scrollarea handles resizing
        self.scroll.setWidgetResizable(True)

        self.scroll.setWidget(self.widget)

        grid.addWidget(self.scroll, 3, 0)
        self.setLayout(grid)


    def _widget_group_query_results(self, items=None, layout=None, amount=10):
        if layout == None:
            layout = self.layout
        else:
            layout = self.layout

        if items:
            count = 0
            for item in items:
                if count < amount:
                    if count % 2 == 0:
                        WidgetBuilder(layout).thumbnail(item['item_thumb'])

                    else:
                        WidgetBuilder(layout).thumbnail(item['item_thumb'], column=0)
                    
                    count += 1

        else:
            for index, _ in enumerate(range(8)):
                if index % 2 == 0:
                    WidgetBuilder(layout).thumbnail('001_ftp1sQ_thumbnail.jpg')

                else:
                    WidgetBuilder(layout).thumbnail('001_ftp1sQ_thumbnail.jpg', column=0)


    def btn_click_widget_group_query(self):
        # reset layout
        """
        for i in reversed(range(self.layout_component_query_results.count())): 
            self.layout_component_query_results.itemAt(i).widget().setParent(None)
        self.layout_container.addLayout(self.layout_component_query_results)
        """
        
        all_items = GlanceLib(self.layout_component_query_results).query(self.query_input.text())
        self._widget_group_query_results(items=all_items)
        # self._widget_group_query_results(items=all_items)


if __name__ == '__main__':
    app = QtWidgets.qApp
    GUI = MainWindow()
    GUI.show()

    sys.exit(app.exec_())

