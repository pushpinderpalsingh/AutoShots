#!/usr/bin/python3
import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from git import Repo
from InstagramApi import InstagramAPI
import os
import time
import logging
import shutil

targetPath = "/home/pp/Shots/images/"
targetRepoPath = "/home/pp/Shots/"
sourcePath = "/media/pictures/Edited/public"

credentials = open("creds","r").read().split(",")[:2]
instagramUser = credentials[0]
instagramPassword = credentials[1]

class AutoShots:
    watchDirectory = sourcePath

    # This will initialize the logger and oberver object
    def __init__(self):
        self.observer = Observer()
        self.logger = logging.getLogger("AutoShots")
        self.logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler('AutoShots.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        print("Initialized Successfully")

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.watchDirectory, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Observer Stopped")

        self.observer.join()

    # This will rename and move the file to its desired location
    def MoveFiles(self,event):
        oldFile = event.src_path.split("/")[-1]

        if oldFile.split(".")[-1] == "DS_Store":
            self.logger.debug("Gone")
            return
        time.sleep(20)
        newFile = datetime.datetime.today().strftime('%S%H%d%m%y') + "-" + oldFile

        shutil.copy(event.src_path, targetPath + newFile)
        self.logger.debug("Renaming and Moving Successful")

        filePath = targetPath + newFile

        self.updateGit(filePath)

    # This will add and update the git repo with a commit named "Update from script"
    def updateGit(self, newFilePath):

        repo = Repo(targetRepoPath)
        origin = repo.remote(name='origin')
        repo.index.add([newFilePath])
        repo.index.commit("Update From Script")
        origin.push()
        time.sleep(110)
        repo.index.remove([newFilePath], working_tree = True, force=True)
        origin.pull(force=True)
        self.logger.debug("Pushed latest")

    def updateInstagram(self,newFilePath):

        InstagramAPI = InstagramAPI(instagramUser,instagramPassword)
        InstagramAPI.login()

        InstagramAPI.uploadPhoto(newFilePath)


class Handler(FileSystemEventHandler):

    @staticmethod
    def on_created(event):
        AutoShots().MoveFiles(event)

    @staticmethod
    def on_moved(event):
        AutoShots().MoveFiles(event)



watch = AutoShots()
watch.run()
