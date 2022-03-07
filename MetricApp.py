from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from concurrent import futures
import threading
import time
import os
import copy
import psutil
import csv

class  MetricsApp():

    def __init__(self):
        self.average_data = []
        self.average_memory = None
        self.average_cpu = None
        self.average_descriptor = None
        self.all_process_names = None
        self.all_process_sorted = None
        self.processor_name = None
        self.collect_number = None



    def startAPP(self):



        def validateTime():
            value1 = tt1.get()
            unit1 = tu1.get()
            value2 = tt2.get()
            unit2 = tu2.get()
            if ((unit1=='SEC') and (unit2=='SEC')):
                if int(value2)>int(value1):
                    logging.error("ERROR: interval must be smaller or equal with total collection time")
                elif int(value1)%int(value2)==0:
                    value1 = int(value1)
                else:
                    logging.error("ERROR: interval time must be divisible with total collection time")
            elif ((unit1=='MIN') and (unit2=='SEC')):
                value1 = int(value1)*60
                if value1%int(value2)!=0:
                    logging.error("ERROR: interval time must be divisible with total collection time")
            elif ((unit1=='HOUR') and (unit2=='SEC')):
                value1 = int(value1)*3600
                if value1%int(value2)!=0:
                    logging.error("ERROR: interval time must be divisible with total collection time")
            elif ((unit1=='MIN') and (unit2=='MIN')):
                if int(value2)>int(value1):
                    logging.error("ERROR: interval must be smaller or equal with total collection time")
                elif int(value1)%int(value2)==0:
                    value1 = int(value1)
                else:
                    logging.error("ERROR: interval time must be divisible with total collection time")
            elif ((unit1=='HOUR') and (unit2=='MIN')):
                value1=int(value1)*60
                if value1%int(value2)!=0:
                    logging.error("ERROR: interval time must be divisible with total collection time")
            elif ((unit1=='HOUR') and (unit2=='HOUR')):
                if int(value2)>int(value1):
                    logging.error("ERROR: interval must be smaller or equal with total collection time")
                elif int(value1)%int(value2)==0:
                    value1 = int(value1)
                else:
                    logging.error("ERROR: interval time must be divisible with total collection time")
            else:
                logging.error("ERROR: The specified interval and sample time are not compatible, please review them")
            collect_number= int(value1)//int(value2)
            print('the number of samples for the process is '  + "{}".format(collect_number) + ' and will be taken at an interval of '+ "{}".format(value2) + ' '+ "{}".format(unit2)+ ' during a period of '+ "{}".format(value1) +' '+ "{}".format(unit2))
            self.collect_number = collect_number
            return(collect_number)

        def calculateInterval():
            value2 = tt2.get()
            unit2 = tu2.get()
            if unit2 == 'SEC':
                value2=int(value2)
            elif unit2 == 'MIN':
                value2=int(value2)*60
            else:
                value2=int(value2)*3600
            return (value2)

        def getProcessNames():
            ######Iterate over all running process and get processes names
            # Iterate over all running process
            listOfProcessNames = []
            for proc in psutil.process_iter():
                # Get process detail as dictionary
                pInfoDict = proc.as_dict(attrs=['name'])
                # Append dict of process name in list
                listOfProcessNames.append(pInfoDict["name"])
                self.all_process_names = listOfProcessNames
            # Iterate over the list of dictionary and print each elem
            return (listOfProcessNames)

        def getListOfProcessSortedByMemory():
            '''
            Get list of running process sorted by Memory Usage
            '''
            listOfProcObjects = []
            # Iterate over the list
            for proc in psutil.process_iter():
                try:
                    # Fetch process details as dict
                    pinfo = proc.as_dict(attrs=['pid', 'name', 'cpu_percent'])
                    pinfo['vms'] = proc.memory_info().vms / (1024 * 1024)
                    # Append dict to list
                    listOfProcObjects.append(pinfo);
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
                # Sort list of dict by key vms i.e. memory usage
            listOfProcObjects = sorted(listOfProcObjects, key=lambda procObj: procObj['vms'], reverse=True)
            self.all_process_sorted = listOfProcObjects
            print(listOfProcObjects)
            return (listOfProcObjects)

        def getProcessId(process_name):
            process_name = enteredProcess.get()
            if process_name in self.all_process_names:
                for i in self.all_process_sorted:
                    if i['name'] == process_name:
                        id=i['pid']
            else:
                logging.error("ERROR: The specified process does not exist on the device")
            return (id)

        def getProcessCpuUsage(process_name):
            process_name = enteredProcess.get()
            if process_name in self.all_process_names:
                for i in self.all_process_sorted:
                    if i['name'] == process_name:
                        cpu_percent=float(i['cpu_percent'])
            else:
                logging.error("ERROR: The specified process does not exist on the device")
            return (cpu_percent)

        def getProcessCpuMemoryUsage(process_name):
            process_name = enteredProcess.get()
            if process_name in getProcessNames():
                for i in getListOfProcessSortedByMemory():
                    if i['name'] == process_name:
                        memory_usage=float(i['vms'])
            else:
                logging.error("ERROR: The specified process does not exist on the device")
            return (memory_usage)



        def getProcessDescriptors(process_name):
            process_name = enteredProcess.get()
            if process_name in self.all_process_names:
                for i in self.all_process_sorted:
                    if i['name'] == process_name:
                        id = i['pid']
                files = psutil.Process(pid=id).open_files()
                descriptors_number = len(files)
            else:
                logging.error("ERROR: The specified process does not exist on the device")
            return (descriptors_number)

        def collectData():
            process_name = enteredProcess.get()
            memory_collection = []
            cpu_collection = []
            descriptor_collection = []
            interval = int(calculateInterval())
            for i in range(self.collect_number):
                memory = getProcessCpuMemoryUsage(process_name)
                memory_collection.append(memory)
                cpu = float(getProcessCpuUsage(process_name))
                cpu_collection.append(cpu)
                descriptor = getProcessDescriptors(process_name)
                descriptor_collection.append(descriptor)
                time.sleep(interval)
            total_memory = sum(memory_collection)
            length_memory = len(memory_collection)
            average_memory = total_memory / length_memory


            total_cpu = sum(cpu_collection)
            length_cpu = len(cpu_collection)
            average_cpu = total_cpu / length_cpu

            total_descriptor = sum(descriptor_collection)
            length_descriptor = len(descriptor_collection)
            average_descriptor = total_descriptor / length_descriptor
            data = [average_memory, average_cpu, average_descriptor]
            print('the data was successfully gathered for ' + process_name + ' process and the values are displayed below:')
            print('the average memory usage in KB for ' +process_name+' process is: '+ "{}".format(average_memory))
            print('the average cpu percent usage for '  +process_name+' process is: '+ "{}".format(average_cpu))
            print('the average descriptors usage for '  +process_name+' process is: '+ "{}".format(average_descriptor))
            self.average_memory = average_memory
            self.average_cpu = average_cpu
            self.average_descriptor = average_descriptor

            self.average_data=data
            return(data)

        def createCsvReport():
            process_name = enteredProcess.get()
            if self.average_data:
                title = ["the process for which data was collected is: " + "{}".format(process_name)]
                headers = ["average memory usage", "average cpu percent", "average descriptors"]
                list = self.average_data
                with open ("process_report.csv", "w") as csvfile:
                    report = csv.writer(csvfile)
                    report.writerow(title)
                    report.writerow(headers)
                    report.writerow(list)
                print('the report was successfully created for ' + process_name + ' process')
            else:
                logging.error("ERROR: The is no data collected for the specified process, please collect data before making report")

        def checkMemoryLeak():
            possible_leak=[]
            for i in getListOfProcessSortedByMemory():
                if float(i['vms'])> 3000:
                    possible_leak.append(i['name'])
            possible=len(possible_leak)
            if possible==1:
                print("The are possible memory leaks for this process: " + "{}".format(possible_leak) + ", please check it")
            elif possible>=1:
                print("The are possible memory leaks for these processes: " + "\n" + "{}".format(possible_leak) + "\n" + "Please check them")
            else:
                print("The are no possible memory leaks for the processes")
            return (possible_leak)

        def openNewWindow():
            process_name = enteredProcess.get()
            if self.average_data:
                # Toplevel object which will be treated as a new window
                newWindow = Toplevel(window)

                # sets the title of the Toplevel widget
                newWindow.title("Average metrics")

                # sets the geometry of toplevel
                newWindow.geometry("800x200")

                # A Label widget to show in toplevel
                label1 = Label(newWindow, text="Collected data for the specified process", fg="blue", bg='green', width=100, height=3)
                label2 = Label(newWindow, text='the average memory usage in KB for ' + process_name + ' process is: ' + "{}".format(self.average_memory) + "\n" + 'the average cpu percent usage for ' + process_name + ' process is: ' + "{}".format(self.average_cpu) + "\n" + 'the average descriptors usage for ' + process_name + ' process is: ' + "{}".format(self.average_descriptor), fg="blue", bg='green', width=100, height=3)
                label1.grid(column=0, row=0)
                label2.grid(column=0, row=1)
            else:
                logging.error("ERROR: The is no data collected for any process, please collect data for a process first")



        window = Tk()
        window.title("Process metrics collection")
        window.geometry('2000x300')



        ######################################################################################
        # On column 0 we have info related to process #####################################
        ######################################################################################
        lbl_process = Label(window, text="Enter below the process name you need to perform actions over")
        lbl_process.grid(column=0, row=0)
        enteredProcess = Entry(window, width=50)
        enteredProcess.grid(column=0, row=1)
        process_input = enteredProcess.get()


        ######################################################################################
        # On column 1 we're going to have available metrics ###################################
        ######################################################################################
        lbl_ssh_actions = Label(window, text="AVAILABLE METRICS")
        lbl_ssh_actions.grid(column=1, row=0)
        lbl_processor_usage = Label(window, text="% processor usage")
        lbl_processor_usage.grid(column=1, row=2)
        lbl_memory_usage = Label(window, text="memory usage")
        lbl_memory_usage.grid(column=1, row=3)
        lbl_open_handles = Label(window, text="number of open handles")
        lbl_open_handles.grid(column=1, row=4)

        ######################################################################################
        # On column 2 we choose the total collect time duration for each metric independently, by default is 1 minute ##############
        ######################################################################################
        lbl_duration = Label(window, text="SET COLLECT TIME DURATION")
        lbl_duration.grid(column=2, row=0)
        duration_time = tuple([i for i in range(1,60)])
        duration_unit = ('SEC', 'MIN', 'HOUR')
        tt1 = StringVar()
        tt1.set(1)
        tu1 = StringVar()
        tu1.set('MIN')

        tt2 = StringVar()
        tt2.set(5)
        tu2 = StringVar()
        tu2.set('SEC')

        o1 = OptionMenu(window, tt1, *duration_time)
        o1.config(width=7)
        o1.grid(column=2, row=1, sticky='W')

        o2 = OptionMenu(window, tu1, *duration_unit)
        o2.config(width=7)
        o2.grid(column=2, row=1, sticky='E')

        ######################################################################################
        # On column 3 we choose sample time interval, by default it is 5 seconds ##############
        ######################################################################################
        lbl_interval = Label(window, text="SET SAMPLE INTERVAL")
        lbl_interval.grid(column=3, row=0)

        o3 = OptionMenu(window, tt2, *duration_time)
        o3.config(width=7)
        o3.grid(column=3, row=1, sticky='W')
        o4 = OptionMenu(window, tu2, *duration_unit)
        o4.config(width=7)
        o4.grid(column=3, row=1, sticky='E')

        #On column 4 we're going to have the data specific actions
        lbl_actions = Label(window, text="DATA ACTIONS")
        lbl_actions.grid(column=4, row=0)

        btn = Button(window, text="Collect data", bg='green', command= collectData, width = 15)
        btn.grid(column=4, row=2)
        btn = Button(window, text="Create report", bg="green", command= createCsvReport, width=15)
        btn.grid(column=4, row=3)
        btn = Button(window, text="Output process collected data", bg="green", command= openNewWindow, width=25)
        btn.grid(column=4, row=4)
        btn = Button(window, text="Check memory leak", bg="green", command= checkMemoryLeak, width=15)
        btn.grid(column=4, row=5)
        btn = Button(window, text="Validate time inputs", bg='green', command= validateTime, width = 15)
        btn.grid(column=3, row=2)
        window.mainloop()



if __name__ == "__main__":
    app = MetricsApp()
    app.startAPP()

