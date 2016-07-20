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

    def finalize(self):
        self.string += "</table></p>\n" 
        return self.string

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

    def fail_string(self):
        self.string += "<b><font color=\"crimson\"> failed </font></b>\n"
        return self.string

    def success_string(self):
        self.string += "<b><font color=\"green\"> OK </font></b>\n" 
        return self.string

    def fuchsia_string(self):
        self.string += "<b><font color=\"fuchsia\"> N/A </font></b>"
        return self.string

    def href_string(self, title, url):
        self.string += "<a href=\""+url+"\">"+title+"</a>\n"
        return self.string

    def append_raw(self, html):
        self.string += html
        return self.string

    def append_table(self, table):
        self.string += table.string



class HTMLIndex():

    index = 0
    htmlfile = ""
    archcrev = ""

    def __init__(self, htmlfile):
        self.htmlfile = htmlfile;
        if not os.path.isfile(htmlfile):
            self.create(htmlfile)
        
        self.index        = self.getindex(htmlfile)
        self.archcrev     = self.getarchcrev(htmlfile)

    def create(self, htmlfile):
        html = HTML(htmlfile)
        html.init_page("ArchC's NightlyTester Main Page")
        html.append_raw("<p>Produced by NightlyTester @ "+utils.gettime()+"</p>")
        
        table = Table()
        table.init(['Test #', 'Date', 'ArchC GIT revision', 'Report', 'Comment', 'Started by'])
        table.append_raw("<tr><td>0</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td></tr>")
        table.finalize()

        html.append_table(table)
        html.close_page()

    def getindex(self, htmlfile):
        index = 0
        with open(htmlfile, "r") as f:
            for l in f:
               s = re.search(r'^<tr><td>([0-9]*)</td>', l)
               if s:
                   index = int(s.group(1))+1
                   break
        return index

    def getarchcrev(self, htmlfile):
        index = 0
        archcrev = 0
        with open(htmlfile, "r") as f:
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

    def __init__(self, htmlfile, index):
        self.string   = ""
        self.htmlfile = htmlfile;
        self.create(htmlfile, index)


    def create(self, htmlfile, index):
        self.html = HTML(htmlfile)
        self.html.init_page("NightlyTester "+utils.version+" Run #"+str(index))
        self.html.append_raw("Produced by NightlyTester @ "+utils.gettime())
        self.html.close_page()
 


        


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








