#!/usr/bin/env python3

import sys
import os
import csv
import string


class HTML:


    def init_page(self, title):
        string = "<html>\n" 
        string += "<head> <title>"+title+"</title></head>\n"
        return string

    def init_body(self, title):
        string += "<body>\n"
        string += "<h1>"+title+"</h1>\n"
        return string

    def finalize_page(self):
        string = "</html>\n"
        return string

    def finalize_body(self, title):
        string = "</body>"
        return string

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
        return table_string;


