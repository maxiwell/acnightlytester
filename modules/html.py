#!/usr/bin/env python3

import sys, re, os, string
from .utils import *

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
    def fuchsia(text):
        string = "<b><font color=\"fuchsia\">" + text + "</font></b>"
        return string

    def running(tag, colspan):
        string  = "<td tag='" + tag + "' align=\"center\" colspan=" + str(colspan) + ">"
        string += HTML.fuchsia("Running...") + "</td>"
        return string

    def colspan(cols, text):
        print(text)
        string   = "<td align=\"center\" colspan=" + str(cols) + ">"
        string  += text + '</td>'
        return string
                   
    @staticmethod  
    def href(title, url):
        string = "<a href=\""+url+"\">"+title+"</a>"
        return string

    @staticmethod
    def lhref(title, url):
        url = './'+os.path.basename(url)
        return HTML.href(title, url)

    @staticmethod
    def monospace(text):
        string = "<font face=\"Courier New\">"+text+"</font>"
        return string

    @staticmethod
    def csvcells_to_html(line):
        table_string = ""
        for l in line.splitlines():
            cels = l.split(';')
            for cel in cels:
                if cel:
                    table_string += "<td>"+cel+"</td>"
        return table_string

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

    @staticmethod
    def log_to_html(logfile, htmlfile, title):
        html = HTMLPage(htmlfile)
        html.init_page(title)
        html.append_log_formatted(logfile)
        html.write_page()

class Table:

    string = ""
    ncols  = 0

    def __init__(self, cols):
        self.string += '<p><table border="1" cellspacing="1" cellpadding="5"><tr>\n'
        for col in cols:
            self.string += "<th>"+col+"</th>"
        self.string += "</tr>\n"
        ncols = len(cols)

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
            table_string += "</tr>\n" 
        self.string += table_string

    def append_csv_line_as_title(self, line):
        table_string = ""
        for l in line.splitlines():
            table_string += "<tr>"
            cels = l.split(';')
            for cel in cels:
                if cel:
                    table_string += "<th>"+cel+"</th>"
            table_string += "</tr>\n" 
        self.string += table_string

    def append_raw(self, html):
        self.string += html 
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
                tmpstr = re.sub(r'<', r'[', l)
                tmpstr = re.sub(r'>', r']', tmpstr)
                tmpstr = re.sub(r'error', r'<b><font color="crinson">error</font></b>', tmpstr)
                tmpstr = re.sub(r'warning', r'<b><font color="fuchsia">warning</font></b>', tmpstr)
                tmpstr = re.sub(r'\n', r'\n<br>', tmpstr)
                strlog += tmpstr

        self.string += "<table><tr><td><font face=\"Courier\">\n"
        self.string += strlog
        self.string += "</font></td></tr></table>"

    def get_page(self):
        return self.page

   
class IndexPage(HTMLPage):

    def __init__(self):
        super().__init__(env.htmloutput + "/" + env.indexhtml)
        
        if not os.path.isfile (self.page):
            self.init_page("ArchC's NightlyTester Main Page")
            self.append_raw("<p>Produced by NightlyTester @ "+gettime()+"</p>")
            
            table = Table(['Test #', 'Initial', 'Final', 'Report', 'Comment', 'Started by'])
            table.append_raw("<tr><td>0</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td></tr>")
            table.close()
            
            self.append_table(table)
            self.write_page()

    def update_index_table(self, strline):
        htmlline = HTML.csvline_to_html(strline)
        insert_line_before_once( filepath = self.page,  \
                                       newline  = htmlline,       \
                                       pattern  = '<tr><td>' )    


class TestsPage(HTMLPage):

    tablearchc = None
    tabletests = None

    suffix = "-tests.html"

    def __init__(self):
        super().__init__(env.htmloutput + "/" + env.testnumber + self.suffix)
        
        self.init_page("NightlyTester "+version+" Run #"+env.testnumber)
        self.append_raw("Produced by NightlyTester @ "+gettime())

        self.tablearchc = Table(['Component', 'Link/Path', 'Version', 'Status'])

        self.tabletests = Table(['Name', 'Link/Path', 'Version', 'Generator', 'Options', \
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


class SimulatorPage(HTMLPage):
    
    benchtable = None

    def __init__(self, sim):
        super().__init__(env.htmloutput + "/" + env.testnumber + "-" + sim + ".html")
        self.benchtable = Table([])

        self.init_page(sim + " Simulator")
        self.append_raw("Produced by NightlyTester @ "+gettime())

    def close_sim_page(self):
        self.append_table(self.benchtable)
        self.write_page()


    def create_benchmark_table(self, bench):
        cols = bench.name.title() + ';Compilation;'
        maxlen = bench.apps[0]
        for app in bench.apps:
            if len(app.dataset) > len(maxlen.dataset):
                maxlen = app
        for ds in maxlen.dataset:
            cols += ds.name.title()+' Dataset;'
        cols += 'Speed;#Instrs.;'
        if bench.custom_links:
            cols += 'Custom Links;'

        self.benchtable.append_csv_line_as_title(cols)

        bench.apps.sort(key=lambda x: x.name)
        for app in bench.apps:
            csvline = app.name + ';' + app.buildstatus + \
                      '(' + HTML.lhref('log', app.buildpage) + ');'
            for ds in app.dataset:

                if ds.execpage == None:
                    csvline += '-;'
                else:
                    if ds.diffstatus:
                        csvline += HTML.success()
                    else:
                        csvline += HTML.fail()

                    csvline += '(' + HTML.lhref('output', ds.execpage) + ', ' + \
                                     HTML.lhref('diff', ds.diffpage) + ');'
                try:
                    with open(ds.execpage) as f:
                        speed = ''
                        instr = ''
                        for l in f:
                            s = re.search('Simulation speed: (.*)',l)
                            i = re.search('Number of instructions executed: (.*)',l)
                            if s:
                                speed += s.group(1)+'<br>'
                            if i:
                                instr += i.group(1)+'<br>'
                        csvline += speed + ';' + instr + ';'
                except:
                    csvline += '-;-;'

            if app.custom_link:
                for link, page in ds.custom_links.items():
                    csvline +=  HTML.lhref (link, page)+'<br>'
            else:
                csvline += '-'
            csvline += ';'

            self.benchtable.append_csv_line(csvline)
        self.benchtable.append_raw('<tr><td colspan=8 height=25></td></tr>')

