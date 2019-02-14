from PyQt5.QtNetwork import QNetworkAccessManager

foo = list()
for a in range(100000):
    foo.append(QNetworkAccessManager())
