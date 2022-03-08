Data-Collection-App
A data collection application that gathers metrics about processes from an OS system

We import these modules.

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

I created a class, MetricsApp ()

class  MetricsApp():

I have defined some instance variables because I need them several times for certain methods.
In order not to call every time the first method that returned the variable.
Basically, by the method that returns a certain variable that I need for other methods, I also populated the respective instance variable.

    def __init__(self):
        self.average_data = []
        self.average_memory = None
        self.average_cpu = None
        self.average_descriptor = None
        self.all_process_names = None
        self.all_process_sorted = None
        self.processor_name = None
        self.collect_number = None

This, startAPP (self), is the only class method in this class.
Inside it are all the other methods used for the application.


    def startAPP(self):

The first method inside the class method is validateTime ().
With its help I take the two time entries from the graphical interface, the total time duration and the sampling interval.

        def validateTime():
            value1 = tt1.get()
            unit1 = tu1.get()
            value2 = tt2.get()
            unit2 = tu2.get()
The units of measurement are independent for each time entry, as well as the entered values and that is why I have created a logic below for the possible cases of units.
The first case, when there are the same units, namely seconds, in case the value of the sample interval is greater than the total time duration,
then this is an invalid case and we give the specific message: "ERROR: interval must be smaller or equal with total collection time"
 
            if ((unit1=='SEC') and (unit2=='SEC')):
                if int(value2)>int(value1):
                    logging.error("ERROR: interval must be smaller or equal with total collection time")
                    
We check if the total time is divisible by the sample interval.
 
                elif int(value1)%int(value2)==0:
                    value1 = int(value1)
                    
In case they are not divisible we will get an error with the message: "ERROR: interval time must be divisible with total collection time"
 
                else:
                    logging.error("ERROR: interval time must be divisible with total collection time")
                    
The next case, when for the sample interval we have seconds and for the total duration we have minutes, we transform the minutes into seconds, in order to
have a reference to the unit of measurement that the sample interval has.
 
            elif ((unit1=='MIN') and (unit2=='SEC')):
                value1 = int(value1)*60
                
Here we do the same divisibility check.
 
                if value1%int(value2)!=0:
                    logging.error("ERROR: interval time must be divisible with total collection time")
                    
We now treat the case where we have seconds for the sample interval and hours for the total duration, we will turn the hours into seconds.  
 
            elif ((unit1=='HOUR') and (unit2=='SEC')):
                value1 = int(value1)*3600
                
Here we do the same divisibility check.
  
                if value1%int(value2)!=0:
                    logging.error("ERROR: interval time must be divisible with total collection time")
 
The next case is when we have minutes for both time values.
 
            elif ((unit1=='MIN') and (unit2=='MIN')):
            
If the value of the sample interval is longer than the total time duration,
then this is an invalid case and we give the specific message: "ERROR: interval must be smaller or equal with total collection time"
 
                if int(value2)>int(value1):
                    logging.error("ERROR: interval must be smaller or equal with total collection time")
                    
Next we check that the time duration is divisible by the sample interval.                  
                    
                elif int(value1)%int(value2)==0:
                    value1 = int(value1)
                    
If they are not divisible, we will also get an error message. 

                else:
                    logging.error("ERROR: interval time must be divisible with total collection time")
                    
The case where we have minutes for the sample interval and hours for the total duration of time.
We convert the total time into minutes to refer to the sample interval.

            elif ((unit1=='HOUR') and (unit2=='MIN')):
                value1=int(value1)*60
                
 We check the divisibility.
 
                if value1%int(value2)!=0:
                    logging.error("ERROR: interval time must be divisible with total collection time")
                    
The next case, when there are the same units, namely hours, in case the value of the sample interval is greater than the total time duration,
then this is an invalid case and we give the specific message: "ERROR: interval must be smaller or equal with total collection time" 

            elif ((unit1=='HOUR') and (unit2=='HOUR')):
                if int(value2)>int(value1):
                    logging.error("ERROR: interval must be smaller or equal with total collection time")

We check the divisibility.

                elif int(value1)%int(value2)==0:
                    value1 = int(value1)
                else:
                    logging.error("ERROR: interval time must be divisible with total collection time")

And because the rest of the combination cases are invalid, for example we can't have seconds for the total duration and 
hours for the sample interval, for all we will get an error.

            else:
                logging.error("ERROR: The specified interval and sample time are not compatible, please review them")
                
We calculate a variable, collect_number, which will be the number of samples to be taken. It is equal to the result of dividing the total time by the sample interval.

            collect_number= int(value1)//int(value2)
            print('the number of samples for the process is '  + "{}".format(collect_number) + ' and will be taken at an interval of '+ "{}".format(value2) + ' '+ "{}".format(unit2)+ ' during a period of '+ "{}".format(value1) +' '+ "{}".format(unit2))
            
As I said at the beginning, I populate the self.collect_number instance variable, so that I can use it in other methods as well, without further calling
again this function, validateTime (), to return it again.

            self.collect_number = collect_number
            return(collect_number)

I use the calculated Interval () method to return the value of the time interval in seconds. I will use this value to put a sleep after each collection
data, basically this value allows me to take the necessary time break between data collections.

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

The getProcessNames () method iterates through the list of processes we take with the psutil.process_iter () method, psutil being 
a special python module for processes.

        def getProcessNames():
            ######Iterate over all running process and get processes names
            # Iterate over all running process
            
We define the list of processes to be empty at the beginning. 

            listOfProcessNames = []
            for proc in psutil.process_iter():
                # Get process detail as dictionary
 
We create a variable, and we populate it with the name of the process.
 
                pInfoDict = proc.as_dict(attrs=['name'])
                
We will put one by one in the empty list defined at the beginning each process name.

                # Append dict of process name in list
                listOfProcessNames.append(pInfoDict["name"])
           
We also populate the self.all_process_names instance variable with this list.

                self.all_process_names = listOfProcessNames
              return (listOfProcessNames)

This method, getListOfProcessSortedByMemory (), iterates through processes and sorts them ascending by memory as a multi-key dictionary. 
here is an example for the java process: {'pid': 4609, 'cpu_percent': 0.0, 'name': 'java', 'vms': 6411.94921875}

        def getListOfProcessSortedByMemory():
            '''
            Get list of running process sorted by Memory Usage
            '''
            listOfProcObjects = []
            
Iterate over the list.

            for proc in psutil.process_iter():
                try:
                
Fetch process details as dictionary.

                    pinfo = proc.as_dict(attrs=['pid', 'name', 'cpu_percent'])
                    pinfo['vms'] = proc.memory_info().vms / (1024 * 1024)
                    
Append dictionary to list.

                    listOfProcObjects.append(pinfo);
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
                    
Sort list of dict by key vms i.e. memory usage.

            listOfProcObjects = sorted(listOfProcObjects, key=lambda procObj: procObj['vms'], reverse=True)
            
Populate self.all_process_sorted variable.

            self.all_process_sorted = listOfProcObjects
            print(listOfProcObjects)
            return (listOfProcObjects)
            
The getProcessId () method takes the process we entered from the keyboard and if it is in the list of names of existing processes, self.all_process_names,
we iterate in the self.all_process_sorted list where we have them in the form of a dictionary and we take from there only the ID for the process with the 
respective name.

        def getProcessId(process_name):
            process_name = enteredProcess.get()
            if process_name in self.all_process_names:
                for i in self.all_process_sorted:
                    if i['name'] == process_name:
                        id=i['pid']
            else:
                logging.error("ERROR: The specified process does not exist on the device")
            return (id)

The getProcessCpuUsage() method takes the process we entered from the keyboard and if it is in the list of names of existing processes, self.all_process_names,
we iterate in the self.all_process_sorted list where we have them in the form of a dictionary and we take from there only the cpu_percent for the process with the 
respective name.

        def getProcessCpuUsage(process_name):
            process_name = enteredProcess.get()
            if process_name in self.all_process_names:
                for i in self.all_process_sorted:
                    if i['name'] == process_name:
                        cpu_percent=float(i['cpu_percent'])
            else:
                logging.error("ERROR: The specified process does not exist on the device")
            return (cpu_percent)

The getProcessCpuMemoryUsage() method takes the process we entered from the keyboard and if it is in the list of names of existing processes, self.all_process_names,
we iterate in the self.all_process_sorted list where we have them in the form of a dictionary and we take from there only the memory_usage for the process with the 
respective name.

        def getProcessCpuMemoryUsage(process_name):
            process_name = enteredProcess.get()
            if process_name in getProcessNames():
                for i in getListOfProcessSortedByMemory():
                    if i['name'] == process_name:
                        memory_usage=float(i['vms'])
            else:
                logging.error("ERROR: The specified process does not exist on the device")
            return (memory_usage)

The getProcessDescriptors() method takes the process we entered from the keyboard and if it is in the list of names of existing processes, self.all_process_names,
we iterate in the self.all_process_sorted list where we have them in the form of a dictionary and we take from there first the id to that process. 
We need the id to call psutil.Process(pid=id).open_files(), which will return the list of descriptors for the process with the respective id.
We will return the length of that list, descriptors_number = len(files). 


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
            
This is the method which collects data.

            
        def collectData():
        
We get the input process name.

            process_name = enteredProcess.get()
            
We make an empty list for each metric that will be collected.
            
            memory_collection = []
            cpu_collection = []
            descriptor_collection = []
            
We get the interval variable calling calculateInterval() method.         
                        
            interval = int(calculateInterval())

We put for loop with self.collect_number range, having this way the number of samples that will be collected.

            for i in range(self.collect_number):

We call each method to get each metric that we will put in its own list.

                memory = getProcessCpuMemoryUsage(process_name)
                memory_collection.append(memory)
                cpu = float(getProcessCpuUsage(process_name))
                cpu_collection.append(cpu)
                descriptor = getProcessDescriptors(process_name)
                descriptor_collection.append(descriptor)
                
After each metrci is collected we make a time pause, using the interval variable.                
                
                time.sleep(interval)
                
After data is collected for each metric, we calculate the average from each metric list.

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
            
We print 4 messages.             
            
            print('the data was successfully gathered for ' + process_name + ' process and the values are displayed below:')
            print('the average memory usage in KB for ' +process_name+' process is: '+ "{}".format(average_memory))
            print('the average cpu percent usage for '  +process_name+' process is: '+ "{}".format(average_cpu))
            print('the average descriptors usage for '  +process_name+' process is: '+ "{}".format(average_descriptor))
            
Also, we populate 4 instance variables.

            self.average_memory = average_memory
            self.average_cpu = average_cpu
            self.average_descriptor = average_descriptor

            self.average_data=data
            return(data)

This is the method that creates the .CSV report.
Of course that first we will check is there is data collected, else we will display that there is no data collected.

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

We define the checkMemoryLeak () method to check for memory leaks. From what I've researched, such a problem arises when memory is not freed
by a process. The logic I thought would be that there would be an unusually high value for the memory used by certain processes when the issue happens.
Inside the method we compare the memory of each process with a predefined value, I set it at 3000 but only to check that the method works and
prints those processes that exceed that value. I don't know exactly how high an unusually high value should be for a particular process.

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

This is the method to create the window that will open when we want to display the collected data.

        def openNewWindow():
            process_name = enteredProcess.get()
            
We check first if there is average data collected, else we will display an error that there is no data collected.

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

This is where we create the application main window.

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

Here we define each button for each method.

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
