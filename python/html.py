#!/usr/bin/env python3

import sys, re
import os
import csv
import string
from . import utils

class HTML:
    @staticmethod    
    def fail():
        string = "<b><font color=\"crimson\"> Failed </font></b>"
        return string

    @staticmethod
    def success():
        string = "<b><font color=\"green\"> OK </font></b>" 
        return string

    @staticmethod
    def fuchsia_string():
        string = "<b><font color=\"fuchsia\"> N/A </font></b>"
        return string

    @staticmethod
    def href(title, url):
        string = "<a href=\""+url+"\">"+title+"</a>"
        return string

    @staticmethod
    def monospace(text):
        string = "<font face=\"Courier New\">"+text+"</font>"
        return string

    @staticmethod
    def csvline_to_html(line):
        table_string = ""
        for l in line.splitlines():
            table_string += "<tr>"
            cels = l.split(';')
            for cel in cels:
                if cel:
                    table_string += "<td>"+cel+"</td>"
            table_string += "</tr>" 
        return table_string


class Table:

    string = ""

    def init(self, cols):
        self.string += '<p><table border="1" cellspacing="1" cellpadding="5"><tr>\n'
        for col in cols:
            self.string += "<th>"+col+"</th>"
        self.string += "</tr>\n"
        return self.string

    def close(self):
        self.string += "</table></p>\n" 
        return self.string


    def append_csv_line(self, line):
        table_string = ""
        for l in line.splitlines():
            table_string += "<tr>"
            cels = l.split(';')
            for cel in cels:
                if cel:
                    table_string += "<td>"+cel+"</td>"
            table_string += "</tr>" 
        self.string += table_string


    def from_csv(self, csvfile):
        table_string = ""
        with open( csvfile, newline='') as cf:
            reader       = csv.reader( cf, delimiter=';' )
            for row in reader:
                table_string += "<tr>" + \
                                    "<td>" + \
                                        "</td><td>".join(row)  + \
                                    "</td>" + \
                                "</tr>\n"
        self.string += table_string
        return self.string

    def append_raw(self, html):
        self.string += html + '\n'
        return self.string



class HTMLPage:

    string = ""
    page = ""
    
    def __init__(self, page):
        self.page = page

    def init_page(self, title):
        self.string += "<html>\n" 
        self.string += "<head> <title>"+title+"</title></head>\n"
        self.string += "<body>\n"
        self.string += "<h1>"+title+"</h1>\n"

    def write_page(self):
        self.string += "</body>\n"
        self.string += "</html>\n"
        self.f = open(self.page, "w")
        self.f.write (self.string)
        self.f.close()

    def append_raw(self, html):
        self.string += html + "\n" 
        return self.string

    def append_table(self, table):
        self.string += table.string

    def append_log_formatted(self, log):
        strlog = ""
        with open(log,'r') as f:
            for l in f:
                tmpstr = re.sub(r'\n', r'\n<br>', l)
                tmpstr = re.sub(r'error', r'<b><font color="crinson">error</font></b>', tmpstr)
                tmpstr = re.sub(r'warning', r'<b><font color="fuchsia">warning</font></b>', tmpstr)
                strlog += tmpstr

        self.string += "<table><tr><td><font face=\"Courier\">\n"
        self.string += strlog
        self.string += "</font></td></tr></table>"


   
class IndexPage(HTMLPage):

    def __init__(self, env):
        super().__init__(env.htmloutput + "/" + env.indexhtml)
        
        if not os.path.isfile (self.page):
            self.init_page("ArchC's NightlyTester Main Page")
            self.append_raw("<p>Produced by NightlyTester @ "+utils.gettime()+"</p>")
            
            table = Table()
            table.init(['Test #', 'Date', 'Report', 'Comment', 'Started by'])
            table.append_raw("<tr><td>0</td><td>-</td><td>-</td><td>-</td><td>-</td></tr>")
            table.close()
            
            self.append_table(table)
            self.write_page()

    def update_index_table(self, strline):
        htmlline = HTML.csvline_to_html(strline)
        utils.insert_line_before_once( filepath = self.page,  \
                                       newline  = htmlline,       \
                                       pattern  = '<tr><td>' )    


class TestsPage(HTMLPage):

    tablearchc = None
    tabletests = None

    suffix = "-tests.html"

    def __init__(self, env):
        super().__init__(env.htmloutput + "/" + env.testnumber + self.suffix)
        
        self.init_page("NightlyTester "+utils.version+" Run #"+env.testnumber)
        self.append_raw("Produced by NightlyTester @ "+utils.gettime())

        self.tablearchc = Table()
        self.tablearchc.init(['Component', 'Link/Path', 'Version', 'Status'])

        self.tabletests = Table()
        self.tabletests.init(['Name', 'Link/Path', 'Version', 'Generator', 'Options', \
                              'Compilation', 'Benchmark', 'Tested in'])
         
    def close_tests_page(self):
        self.tablearchc.close()
        self.tabletests.close()
        
        self.append_table(self.tablearchc)
        self.append_raw('<h3>Tests</h3>')
        self.append_table(self.tabletests)

        self.write_page()
        

    def update_archc_table(self, strline):
        self.tablearchc.append_csv_line(strline)

    def update_tests_table(self, strline):
        self.tabletests.append_csv_line(strline)

    def tests_had_failed(self):
        with open(self.page, 'r') as f:
            for l in f:
                if re.search("Failed", l):
                    return True
        return False
        self.testspage.update_archc_table(self.cross.get_crosscsvline())

    def get_tests_page(self):
        return self.page


class SimulatorPage(HTMLPage):
    
    tables = []

    def __init__(self, env, sim):
        super().__init__(env.htmloutput + "/" + env.testnumber + "-" + sim + ".html")


        self.init_page(sim + " Simulator")
        self.append_raw("Produced by NightlyTester @ "+utils.gettime())

    def close_sim_page(self):
        self.write_page()



