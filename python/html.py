#!/usr/bin/env python3

import sys, re
import os
import csv
import string
from . import utils

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
        table_string = "<tr>"
        cels = line.split(';')
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


class HTML:

    string = ""
    htmlfile = ""
    
    def __init__(self, htmlfile):
        self.htmlfile = htmlfile

    def init_page(self, title):
        self.string += "<html>\n" 
        self.string += "<head> <title>"+title+"</title></head>\n"
        self.string += "<body>\n"
        self.string += "<h1>"+title+"</h1>\n"
        return self.string

    def close_page(self):
        self.string += "</body>\n"
        self.string += "</html>\n"
        self.f = open(self.htmlfile, "w")
        self.f.write (self.string);
        self.f.close()
        return self.string

    @staticmethod    
    def fail():
        string = "<b><font color=\"crimson\"> failed </font></b>"
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

class HTMLIndex():

    htmlfile = ""
    archcrev = ""

    def __init__(self, env):
        self.htmlfile = env.htmlroot + "/index.html" 
        if not os.path.isfile(self.htmlfile):
            self.create()
        
        env.index         = str(self.getindex())
        self.archcrev     = self.getarchcrev()

    def create(self):
        html = HTML(self.htmlfile)
        html.init_page("ArchC's NightlyTester Main Page")
        html.append_raw("<p>Produced by NightlyTester @ "+utils.gettime()+"</p>")
        
        table = Table()
        table.init(['Test #', 'Date', 'ArchC GIT revision', 'Report', 'Comment', 'Started by'])
        table.append_raw("<tr><td>0</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td></tr>")
        table.close()

        html.append_table(table)
        html.close_page()

    def getindex(self):
        index = 0
        with open(self.htmlfile, "r") as f:
            for l in f:
               s = re.search(r'^<tr><td>([0-9]*)</td>', l)
               if s:
                   index = int(s.group(1))+1
                   break
        return index

    def getarchcrev(self):
        index = 0
        archcrev = 0
        with open(self.htmlfile, "r") as f:
            for l in f:
                s = re.search(r'<td>([0-9a-zA-Z-]*)..</td>',l)
                if s:
                    archcrev = s.group(1)
                    break
        return archcrev


class HTMLLog:

    htmlfile = ""
    string   = ""
    html     = ""

    env      = None

    table1 = None
    table2 = None

    def __init__(self, env):
        self.env = env
        self.string   = ""
        self.htmlfile = env.htmlroot + "/" + env.index + "-index.html";
        self.create()


    def create(self):
        self.html = HTML(self.htmlfile)
        self.html.init_page("NightlyTester "+utils.version+" Run #"+self.env.index)
        self.html.append_raw("Produced by NightlyTester @ "+utils.gettime())

        self.table1 = Table()
        self.table1.init(['Component', 'Link/Path', 'Version', 'Status'])

        self.table2 = Table()
        self.table2.init(['Model', 'Link/Path', 'Version', 'Generator', 'Options', \
                         'Compilation', 'Benchmark', 'Tested in'])
         
    def close(self):
        self.table1.close()
        self.table2.close()
        
        self.html.append_table(self.table1)
        self.html.append_raw('<h3>Tests</h3>')
        self.html.append_table(self.table2)

        self.html.close_page()
        

    def appendtable1(self, strline):
        self.table1.append_csv_line(strline)


#
#table = Table();
#table.init( ['c1', 'c2', 'c3', 'c4'] )
#table.from_csv("/tmp/teste.csv")
#table.finalize()
#
#html = HTML("/home/max/public_html/teste.html")
#html.init_page("teste")
#html.append_table(table)
#html.finalize_page()








