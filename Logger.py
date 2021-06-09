import os
from datetime import datetime


class Logger:

    def __init__(self, path, list_of_strings=[]):
        self.list_of_strings = list_of_strings
        self.path = path

    def log(self, string):
        self.list_of_strings.append("{}\n".format(string))

    def log_now(self, string):
        self.list_of_strings.append(string + "{}\n".format(datetime.now().strftime("%Y %b %d Time: %H:%M:%S")))

    def flush(self):
        directories = os.listdir(self.path)
        directories.sort()
        if len(directories) > 5:
            os.remove(self.path+directories[-1])
        now = datetime.now()

        with open(self.path+"log_{}.txt".format(now.strftime("%y%m%d_%H%M%S")), "w") as writer:
            writer.writelines(self.list_of_strings)
