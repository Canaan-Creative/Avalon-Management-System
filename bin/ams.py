#!/usr/bin/env python3

import multiprocessing
import datetime
import time


def f(run_time):
    print("Run at {:%Y%m%d %H:%M:%S}".format(run_time))


class TaskGenerator():
    __filter = []
    schedules = []

    def __init__(self, schedules):
        for schedule in schedules:
            if schedule['function'] in self.__filter:
                self.schedules.append(schedule)

    def get():
        now = datetime.datetime.now()
        for schedule in self.schedules:

        task = Task(datetime.datetime.now(), f, (datetime.datetime.now(),))
        return task


class Task():
    def __init__(self, t, function, args):
        self.time = t
        self.function = function
        self.args = args
        self.process = multiprocessing.Process(
            target=self.function, args=self.args)

    def run(self):
        try:
            time.sleep((self.time - datetime.datetime.now()).total_seconds())
        except ValueError:
            # Overdue
            return False
        self.process.start()
        self.process.join()


if __name__ == '__main__':

    taskGen = TaskGenerator('''
5 0
                            ''')
    p = Task(f, (datetime.datetime.now(),))
    p.run()
