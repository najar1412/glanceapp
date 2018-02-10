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


class Config():
    username = 'admin'
    password = 'admin'
    entry_point = 'http://34.236.238.212:5050/glance/v2/items'
    storage_url = 'https://s3.amazonaws.com/vhdevglancestore/'


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


    def thumb_widget(self, image_name, column=0):
        url = Config().storage_url + image_name

        data = urllib2.urlopen(url).read()
        image = QtGui.QImage()
        image.loadFromData(data)

        lbl = QtWidgets.QLabel()
        lbl.setPixmap(QtGui.QPixmap(image))
        
        if column == 0:
            self.context.addWidget(lbl)
            
        else:
            self.context.addWidget(lbl, 0, 1)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.construct_ui()


    def construct_ui(self):
        self.setWindowTitle('glanceapp')

        # main widget
        main_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(main_widget)

        # layout initialize
        self.g_layout = QtWidgets.QVBoxLayout()
        self.layout_query = QtWidgets.QVBoxLayout()
        self.layout = QtWidgets.QGridLayout()
        main_widget.setLayout(self.g_layout)

        # Add Widgets
        self.query_input = QtWidgets.QLineEdit()
        self.layout_query.addWidget(self.query_input)
        
        btn = QtWidgets.QPushButton("Search...")
        self.layout_query.addWidget(btn)
        btn.clicked.connect(self.buttonClicked)
        
        self.build_columns()

        # global layout setting
        self.g_layout.addLayout(self.layout_query)
        self.g_layout.addLayout(self.layout)


    def build_columns(self, items=None, amount=10):
        if items:
            count = 0
            for item in items:
                if count < amount:
                    if count % 2 == 0:
                        GlanceLib(self.layout).thumb_widget(item['item_thumb'])

                    else:
                        GlanceLib(self.layout).thumb_widget(item['item_thumb'], column=1)
                    
                    count += 1
        
        else:
            for index, _ in enumerate(range(8)):
                if index % 2 == 0:
                    GlanceLib(self.layout).thumb_widget('001_ftp1sQ_thumbnail.jpg')
                    
                else:
                    GlanceLib(self.layout).thumb_widget('001_ftp1sQ_thumbnail.jpg', column=1)


    def buttonClicked(self):
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().setParent(None)
        self.layout = QtWidgets.QGridLayout()
        self.g_layout.addLayout(self.layout)

        all_items = GlanceLib(self.layout).query(self.query_input.text())
        self.build_columns(items=all_items)
        
        
if __name__ == '__main__':
    app = QtWidgets.qApp
    GUI = MainWindow()
    GUI.show()

    sys.exit(app.exec_())