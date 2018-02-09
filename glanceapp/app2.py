import sys
# sys.path.append('D:/glanceapp/glanceapp/')

from PySide import QtGui
from PySide import QtCore
import urllib2
import MaxPlus
import json
import base64


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


    def thumb_widget(self, image_name):
        url = Config().storage_url + image_name

        data = urllib2.urlopen(url).read()
        image = QtGui.QImage()
        image.loadFromData(data)

        lbl = QtGui.QLabel()
        lbl.setPixmap(QtGui.QPixmap(image))
        lbl2 = QtGui.QLabel()
        lbl2.setText('View | Download')

        self.context.addWidget(lbl)
        self.context.addWidget(lbl2)


class example(QtGui.QWidget):
    def __init__(self, parent=None):
        super(example, self).__init__()
        self.setFixedWidth(500)
        self.setFixedHeight(800)

        self.query_text = QtGui.QLineEdit()

        grid = QtGui.QGridLayout()
        self.widget = QtGui.QWidget()
        self.layout = QtGui.QGridLayout(self.widget)

        self.layout.addWidget(self.query_text)

        btn = QtGui.QPushButton("Search...")
        self.layout.addWidget(btn)
        btn.clicked.connect(self.buttonClicked)

        self.scroll = QtGui.QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.scroll.setWidget(self.widget)

        grid.addWidget(self.scroll, 3, 0)

        self.setLayout(grid)


    def buttonClicked(self):
        all_items = GlanceLib(self.layout).query(self.query_text.text())

        count = 0

        for item in all_items:
            if count < 10:
                GlanceLib(self.layout).thumb_widget(item['item_thumb'])
                count += 1


if __name__ == '__main__':
    app = QtGui.QApplication.instance()
    dialog = example()
    dialog.show()

    sys.exit(app.exec_())