#!/usr/bin/env python3

import sys, re, os, string
from .utils import *

class HTML:
    @staticmethod    
    def fail(i = ""):
        if i == "":
            string = "<b><font color=\"crimson\"> Failed </font></b>"
        else:
            string = "<b><font color=\"crimson\"> "+ i +" </font></b>"
        return string

    @staticmethod
    def success(i = ""):
        if i == "":
            string = "<b><font color=\"green\"> OK </font></b>" 
        else:
            string = "<b><font color=\"green\"> "+ i +" </font></b>" 
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
        string   = "<td align=\"center\" colspan=" + str(cols) + ">"
        string  += text + '</td>'
        return string
                   
    @staticmethod  
    def href(title, url):
        string = "<a href=\""+url+"\">"+title+"</a>"
        return string

    @staticmethod
    def lhref(title, url):
        url = './' + os.path.basename(url)
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
            table_string += "</tr>\n" 
        return table_string

    @staticmethod
    def log_to_html(logfile, htmlfile, title, highlight = []):
        html = HTMLPage(htmlfile)
        html.init_page(title)
        html.append_log_formatted(logfile, highlight)
        html.write_page()

    @staticmethod
    def string_to_html(string, htmlfile, title, highlight = []):
        html = HTMLPage(htmlfile)
        html.init_page(title)
        logfile = create_rand_file()
        f = open(logfile, 'w')
        f.write(string)
        f.close()
        html.append_log_formatted(logfile, highlight)
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

    def append_log_formatted(self, log, highlight = []):
        strlog = ""
        with open(log,'r') as f:
            for l in f:
                if l.startswith("$"):
                    tmpstr = re.sub(r'&&', r'&&\n', l)
                else:
                    tmpstr = re.sub(r'<', r'&lt;', l)
                    tmpstr = re.sub(r'>', r'&gt;', tmpstr)
                    tmpstr = self.custom_sub ('<b><font color="crinson">', 'error', '</font></b>', tmpstr)
                    tmpstr = self.custom_sub ('<b><font color="fuchsia">', 'warning', '</font></b>', tmpstr)
                    for h in highlight:
                        tmpstr = self.custom_sub ('<b><font color="fuchsia">', h, '</font></b>', tmpstr)
                
                tmpstr = re.sub(r'\n', r'\n<br>', tmpstr)
                strlog += tmpstr

        self.string += "<table><tr><td><font face=\"Courier New\">\n"
        self.string += strlog 
        self.string += "</font></td></tr></table>"
    

    def get_page(self):
        return self.page

    def custom_sub(self, begin, words, end, inputstring):

        # Using the 'error' word as example, the regex below avoids matches with 
        # 'werror', 'errorprone', '_error', 'error-'. But match correctly with 'error' 
        # in begin and end of sentences and with other character, like 'error:' and '[error]'
        return re.sub(r'(?P<n1>([^a-zA-Z0-9_-]|^))(?P<n2>' + words + ')(?P<n3>([^a-zA-Z0-9_-]|$))', \
                      r'\g<n1>' +  begin + '\g<n2>' + end + '\g<n3>', inputstring, flags=re.IGNORECASE)

    
class IndexPage(HTMLPage):

    def __init__(self):
        super().__init__(env.get_indexhtml())
        
        if not os.path.isfile (self.page):
            self.init_page("ArchC's NightlyTester Main Page")
            
            table = Table(['Test #', 'Initial', 'Final', 'Report', 'Comment', 'Started by'])
            table.append_raw("<tr><td>0</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td></tr>")
            table.close()
            
            self.append_table(table)
            self.write_page()

    def update_index_table(self, strline):
        htmlline = HTML.csvline_to_html(strline)
        insert_line_before_once( filepath = self.page,      \
                                 newline  = htmlline,       \
                                 pattern  = '<tr><td>' )    


class TestsPage(HTMLPage):

    tablearchc = None
    tabledesc  = None
    tabletests = None

    suffix = "tests.html"

    def __init__(self):
        super().__init__(env.get_htmloutput_fullstring() + self.suffix)
        
        self.init_page("NightlyTester "+version+" Run #"+env.testnumber)
        self.append_raw("Produced by NightlyTester @ "+gettime())

        self.tablearchc = Table(['Component', 'Link/Path', 'Version', 'Status'])

        self.tabledesc  = Table(['Module', 'Generator', 'Options', 'Description'])

        self.tabletests = Table(['Module', 'Link/Path', 'Branch', 'Version', 'Input', \
                              'Compilation', 'Benchmark', 'Tested in'])
         
    def close_tests_page(self):
        self.tablearchc.close()
        self.tabledesc.close()
        self.tabletests.close()
        
        self.append_table(self.tablearchc)
        self.append_raw('<h3>Module Description Table</h3>')
        self.append_table(self.tabledesc)
        self.append_raw('<h3>All Tests Table</h3>')
        self.append_table(self.tabletests)

        self.write_page()
       

    # To use in 'href' tag
    def get_page_relative(self):
        return './' + env.get_htmloutput_prefix() + self.suffix

    def update_archc_table(self, strline):
        self.tablearchc.append_csv_line(strline)

    def update_description_table (self, strline):
        self.tabledesc.append_csv_line(strline)

    def update_tests_table(self, strline):
        self.tabletests.append_csv_line(strline)


class SimulatorPage(HTMLPage):
    
    benchtable = None

    def __init__(self, sim):
        super().__init__(env.get_htmloutput_fullstring() + sim + ".html")
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
            cols += ds.name.title()+' Dataset;Speed;#Instrs.;'
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
                        if speed == '':
                            speed = '-;'
                        if instr == '':
                           instr = '-;'    
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
        self.benchtable.append_raw('<tr><td colspan=10 height=25></td></tr>')

