#!/usr/bin/env python3

import sys
import os
import csv
import string

class Table:

    string = ""

    def init(self, cols):
        self.string += '<p><table border="1" cellspacing="1" cellpadding="5"><tr>\n'
        for col in cols:
            self.string += "<th>"+col+"</th>"
        self.string += "</tr>"
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


class HTML:

    string = ""
    
    def __init__(self, htmlfile):
        self.f = open(htmlfile, "w")

    def init_page(self, title):
        self.string += "<html>\n" 
        self.string += "<head> <title>"+title+"</title></head>\n"
        self.string += "<body>\n"
        self.string += "<h1>"+title+"</h1>\n"
        return self.string

    def finalize_page(self):
        self.string += "</body>\n"
        self.string += "</html>\n"
        self.f.write (self.string);
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








