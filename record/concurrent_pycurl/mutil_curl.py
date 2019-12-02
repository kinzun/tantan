import threading
import pycurl


class Test(threading.Thread):
    def __init__(self, url, target_file, progress):
        threading.Thread.__init__(self)
        self.target_file = target_file
        self.progress = progress
        self.curl = pycurl.Curl()
        self.curl.setopt(pycurl.URL, url)
        self.curl.setopt(pycurl.WRITEDATA, self.target_file)
        self.curl.setopt(pycurl.FOLLOWLOCATION, 1)
        self.curl.setopt(pycurl.NOPROGRESS, 0)
        self.curl.setopt(pycurl.PROGRESSFUNCTION, self.progress)
        self.curl.setopt(pycurl.MAXREDIRS, 5)
        self.curl.setopt(pycurl.NOSIGNAL, 1)

    def run(self):

        self.curl.perform()
        self.curl.close()
        self.target_file.close()
        self.progress(1.0, 1.0, 0, 0)

