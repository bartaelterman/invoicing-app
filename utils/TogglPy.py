#--------------------------------------------------------------
# TogglPy is a non-cluttered, easily understood and implemented
# library for interacting with the Toggl API.
#
# Original version: https://github.com/matthewdowney/TogglPy
# Updates by Bart Aelterman:
#   - Ported to Python 3,
#   - Uses requests instead of urllib
#   - Added a getTimeEntries method
#--------------------------------------------------------------
from datetime import datetime
# for making requests
import logging
logging.basicConfig(level=logging.INFO)
import requests
from requests.auth import HTTPBasicAuth

# parsing json data
import json
#
#---------------------------------------------
# Class containing the endpoint URLs for Toggl
#---------------------------------------------
class Endpoints():
    WORKSPACES = "https://api.track.toggl.com/api/v8/workspaces"
    CLIENTS = "https://api.track.toggl.com/api/v8/clients"
    PROJECTS = "https://api.track.toggl.com/api/v8/projects"
    REPORT_WEEKLY = "api.track.toggl.com/reports/api/v2/weekly"
    REPORT_DETAILED = "api.track.toggl.com/reports/api/v2/details"
    REPORT_SUMMARY = "api.track.toggl.com/reports/api/v2/summary"
    START_TIME = "https://api.track.toggl.com/api/v8/time_entries/start"
    TIME_ENTRIES = "https://api.track.toggl.com/api/v8/time_entries"
    @staticmethod
    def STOP_TIME(pid):
        return "https://www.toggl.com/api/v8/time_entries/" + str(pid) + "/stop"
    CURRENT_RUNNING_TIME = "https://www.toggl.com/api/v8/time_entries/current"

#-------------------------------------------------------
# Class containing the necessities for Toggl interaction
#-------------------------------------------------------
class Toggl():
    # template of headers for our request
    headers = {
        "Authorization": "",
        "Content-Type": "application/json",
        "Accept": "*/*",
        "User-Agent": "python/urllib",
    }

    # default API user agent value
    user_agent = "TogglPy"

    #-------------------------------------------------------------
    # Auxiliary methods
    #-------------------------------------------------------------

    def decodeJSON(self, jsonString):
        return json.JSONDecoder().decode(jsonString)

    #-------------------------------------------------------------
    # Methods that modify the headers to control our HTTP requests
    #-------------------------------------------------------------
    def setAPIKey(self, APIKey):
        self.api_token = APIKey

    def setUserAgent(self, agent):
        '''set the User-Agent setting, by default it's set to TogglPy'''
        self.user_agent = agent

    #------------------------------------------------------
    # Methods for directly requesting data from an endpoint
    #------------------------------------------------------

    def requestRaw(self, endpoint, parameters=None):
        '''make a request to the toggle api at a certain endpoint and return the RAW page data (usually JSON)'''
        if parameters == None:
            return requests.get(endpoint, headers=self.headers, auth=HTTPBasicAuth(self.api_token, 'api_token'))
        else:
            if 'user_agent' not in parameters:
                parameters['user_agent'] =self.user_agent # add our class-level user agent in there
            return requests.get(endpoint, headers=self.headers, params=parameters, auth=HTTPBasicAuth(self.api_token, 'api_token')) # make request and read the response

    def request(self, endpoint, parameters=None):
        '''make a request to the toggle api at a certain endpoint and return the page data as a parsed JSON dict'''
        response = self.requestRaw(endpoint, parameters)
        print(response.status_code)
        return response.json()

    def postRequest(self, endpoint, parameters=None):
        '''make a POST request to the toggle api at a certain endpoint and return the RAW page data (usually JSON)'''
        if parameters == None:
            return requests.post(endpoint, headers=self.headers, auth=HTTPBasicAuth(self.api_token, 'api_token'))
        else:
            return requests.post(endpoint, data=parameters, headers=self.headers, auth=HTTPBasicAuth(self.api_token, 'api_token')) # make request and read the response

    #----------------------------------
    # Methods for managing Time Entries
    #----------------------------------

    def startTimeEntry(self, description, pid):
        '''starts a new Time Entry'''
        data = {
            "time_entry": {
            "description": description,
            "pid": pid,
            "created_with": self.user_agent
            }
        }
        response = self.postRequest(Endpoints.START_TIME, parameters=data)
        return self.decodeJSON(response)

    def currentRunningTimeEntry(self):
        '''Gets the Current Time Entry'''
        response = self.postRequest(Endpoints.CURRENT_RUNNING_TIME)
        return self.decodeJSON(response)

    def stopTimeEntry(self, entryid):
        '''Stop the time entry'''
        response = self.postRequest(Endpoints.STOP_TIME(entryid))
        return self.decodeJSON(response)

    def createTimeEntry(self, hourduration, projectid=None, projectname=None,
                        clientname=None, year=None, month=None, day=None, hour=None):
        """
        Creating a custom time entry, minimum must is hour duration and project param
        :param hourduration:
        :param projectid: Not required if projectname given
        :param projectname: Not required if projectid was given
        :param clientname: Can speed up project query process
        :param year: Taken from now() if not provided
        :param month: Taken from now() if not provided
        :param day: Taken from now() if not provided
        :param hour: Taken from now() if not provided
        :return: response object from post call
        """
        data = {
            "time_entry": {}
        }

        if not projectid:
            if projectname and clientname:
                projectid = (self.getClientProject(clientname, projectname))['data']['id']
            elif projectname:
                projectid = (self.searchClientProject(projectname))['data']['id']
            else:
                print('Too many missing parameters for query')
                exit(1)

        year = datetime.now().year if not year else year
        month = datetime.now().month if not month else month
        day = datetime.now().day if not day else day
        hour = datetime.now().hour if not hour else hour

        timestruct = datetime(year, month, day, hour-2).isoformat() + '.000Z'
        data['time_entry']['start'] = timestruct
        data['time_entry']['duration'] = hourduration*3600
        data['time_entry']['pid'] = projectid
        data['time_entry']['created_with'] = 'NAME'

        response = self.postRequest(Endpoints.TIME_ENTRIES, parameters=data)
        return response.json()


    def getTimeEntries(self, start_date, end_date, projectid=None):
        """
        wrapper to retrieve all time entries during a given period
        :return: array or time entries
        """
        data = {}
        data['start_date'] = start_date.isoformat() + '+01:00'
        data['end_date'] = end_date.isoformat() + '+01:00'

        entries = self.request(Endpoints.TIME_ENTRIES, parameters=data)

        if projectid:
            entries = [x for x in entries if str(x['pid']) == str(projectid)]
        return entries


    #-----------------------------------
    # Methods for getting workspace data
    #-----------------------------------
    def getWorkspaces(self):
        '''return all the workspaces for a user'''
        return self.request(Endpoints.WORKSPACES)

    def getWorkspace(self, name=None, id=None):
        '''return the first workspace that matches a given name or id'''
        workspaces = self.getWorkspaces() # get all workspaces
        
        # if they give us nothing let them know we're not returning anything
        if name == None and id == None:
            print("Error in getWorkspace(), please enter either a name or an id as a filter")
            return None

        if id == None: # then we search by name
            for workspace in workspaces: # search through them for one matching the name provided
                if workspace['name'] == name:
                    return workspace # if we find it return it
            return None # if we get to here and haven't found it return None
        else: # otherwise search by id
            for workspace in workspaces: # search through them for one matching the id provided
                if workspace['id'] == int(id):
                    return workspace # if we find it return it
            return None # if we get to here and haven't found it return None
    
    #--------------------------------
    # Methods for getting client data
    #--------------------------------
    def getClients(self):
        '''return all clients that are visable to a user'''
        return self.request(Endpoints.CLIENTS)

    def getClient(self, name=None, id=None):
        '''return the first workspace that matches a given name or id'''
        clients = self.getClients() # get all clients
        
        # if they give us nothing let them know we're not returning anything
        if name == None and id == None:
            print("Error in getClient(), please enter either a name or an id as a filter")
            return None

        if id == None: # then we search by name
            for client in clients: # search through them for one matching the name provided
                if client['name'] == name:
                    return client # if we find it return it
            return None # if we get to here and haven't found it return None
        else: # otherwise search by id
            for client in clients: # search through them for one matching the id provided
                if client['id'] == int(id):
                    return client # if we find it return it
            return None # if we get to here and haven't found it return None

    def getClientProjects(self, id):
        """
        :param id: Client ID by which to query
        :return: Projects object returned from endpoint
        """
        return self.request(Endpoints.CLIENTS + '/{0}/projects'.format(id))

    def searchClientProject(self, name):
        """
        Provide only a projects name for query and search through entire available names
        WARNING: Takes a long time!
                 If client name is known, 'getClientProject' would be advised
        :param name: Desired Project's name
        :return: Project object
        """
        for client in self.getClients():
            try:
                for project in self.getClientProjects(client['id']):
                    if project['name'] == name:
                        return project
            except:
                continue

        print('Could not find client by the name')
        return None

    def getClientProject(self, clientName, projectName):
        """
        Fast query given the Client's name and Project's name
        :param clientName:
        :param projectName:
        :return:
        """
        for client in self.getClients():
            if client['name'] == clientName:
                cid = client['id']

        if not cid:
            print('Could not find such client name')
            return None

        for projct in self.getClientProjects(cid):
            if projct['name'] == projectName:
                pid = projct['id']

        if not pid:
            print('Could not find such project name')
            return None

        return self.getProject(pid)

    # --------------------------------
    # Methods for getting PROJECTS data
    # --------------------------------
    def getProject(self, pid):
        '''return all projects that are visable to a user'''
        return self.request(Endpoints.PROJECTS + '/{0}'.format(pid))

    #---------------------------------
    # Methods for getting reports data
    #---------------------------------
    def getWeeklyReport(self, data):
        '''return a weekly report for a user'''
        return self.request(Endpoints.REPORT_WEEKLY, parameters=data)

    def getWeeklyReportPDF(self, data, filename):
        '''save a weekly report as a PDF'''
        # get the raw pdf file data
        filedata = self.requestRaw(Endpoints.REPORT_WEEKLY + ".pdf", parameters=data)

        # write the data to a file
        with open(filename, "wb") as pdf:
            pdf.write(filedata)

    def getDetailedReport(self, data):
        '''return a detailed report for a user'''
        return self.request(Endpoints.REPORT_DETAILED, parameters=data)

    def getDetailedReportPDF(self, data, filename):
        '''save a detailed report as a pdf'''
        # get the raw pdf file data
        filedata = self.requestRaw(Endpoints.REPORT_DETAILED + ".pdf", parameters=data)

        # write the data to a file
        with open(filename, "wb") as pdf:
            pdf.write(filedata)

    def getSummaryReport(self, data):
        '''return a summary report for a user'''
        return self.request(Endpoints.REPORT_SUMMARY, parameters=data)

    def getSummaryReportPDF(self, data, filename):
        '''save a summary report as a pdf'''
        # get the raw pdf file data
        filedata = self.requestRaw(Endpoints.REPORT_SUMMARY + ".pdf", parameters=data)

        # write the data to a file
        with open(filename, "wb") as pdf:
            pdf.write(filedata)

