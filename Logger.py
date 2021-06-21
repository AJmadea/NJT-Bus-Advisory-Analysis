import os
from datetime import datetime


class Logger:

    def __init__(self, path, max_files=10, list_of_strings=[]):
        self.max_files = max_files
        self.list_of_strings = list_of_strings
        self.path = path

    def log(self, string):
        self.list_of_strings.append("{}\n".format(string))

    def log_with_datetime(self, string):
        self.list_of_strings.append("{} {}\n".format(string, datetime.now().strftime("%Y %b %d Time: %H:%M:%S")))

    def flush(self):
        directories = os.listdir(self.path)
        directories.sort()

        if len(directories) >= self.max_files:
            removing = "{}{}".format(self.path, directories[0])
            # print(removing)
            self.log("Removing File From Folder: {}".format(removing))
            os.remove(removing)

        now = datetime.now()
        self.log_with_datetime("Creating log file...")
        with open(self.path+"log_{}.txt".format(now.strftime("%y%m%d_%H%M%S")), "w") as writer:
            writer.writelines(self.list_of_strings)
