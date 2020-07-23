'''
PACX Personal Accounting Software

Author: Boren Xue
'''
import os
import math
import time
import datetime as dt
import calendar as cal
import locale

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

import numpy as np

import transaction

class App(tk.Tk):

    '''SETTING UP TEMPLATE -----------------------------------------------------------------------------'''
    def __init__(self, filename=None, size='1400x690',):
        tk.Tk.__init__(self)
        self.filename = filename
        #geometry
        self.size = size
        #locale settings
        locale.setlocale(locale.LC_ALL, 'english-nz')
        #font
        #buttons/app text
        self.font1 = ('calibri', '12')
        #display text
        self.font2 = ('courier', '11')
        #analysis text
        self.font3 = ('courier', '9')
        #info_box_text
        self.font4 = ('calibri', '11')

        #default period 0-3 (day/week/month/quarter)
        self.default_period = 1
        self.period = self.default_period
        #default period 2 (analysis) 1-4 (week/month/quarter/year)
        self.default_period2 = 1
        self.period2 = self.default_period2
        #saved or not
        self.changed = False

        #these variables must exist at all times
        self.transactions = []
        self.analysis = []
        
        #loading file (if any), self.transactions is always sorted according to date
        if self.filename == None:
            self.title('PACX - "New"')
            self.transactions = []
        else:
            self.title('PACX - "' + self.filename + '"')
            self.load_file(self.filename)
        
        #window size
        self.geometry(self.size)

        self.init_window()

        self.create_shortcut_keys()

        self.after(0, self.after_func)
        
    def init_window(self):
        #main frame
        self.main_frame = tk.Frame(self, borderwidth=4, relief='sunken')
        
        #set main frame
        self.main_frame.pack(fill='both', expand=1)
        self.minsize(860, 400)
        
        self.create_menu()

        #make L/R paned window
        self.LR_paned = ttk.PanedWindow(self.main_frame, orient='horizontal')
        self.LR_paned.pack(fill='both', expand=1)
        #make left frame/right TB paned window
        self.L_frame = tk.Frame(self.LR_paned)
        self.R_TB_paned = ttk.PanedWindow(self.LR_paned, orient='vertical')
        #set the windows
        self.LR_paned.add(self.L_frame, weight=1)
        self.LR_paned.add(self.R_TB_paned)

        #make the individual frames
        self.top_left_frame = tk.Frame(self.L_frame)
        self.bot_left_frame = tk.Frame(self.L_frame, bg='orange', padx=5, pady=4)
        self.top_right_frame = tk.Frame(self.R_TB_paned)
        self.bot_right_frame = tk.Frame(self.R_TB_paned, bg='cyan', padx=10, pady=6)
        self.info_box_frame = tk.Frame(self.L_frame)

        #set the individual frames
        self.bot_left_frame.pack(side='bottom', fill='x')
        self.info_box_frame.pack(side='bottom', fill='x')
        self.top_left_frame.pack(fill='both', expand=1)
        self.R_TB_paned.add(self.top_right_frame, weight=1)
        self.R_TB_paned.add(self.bot_right_frame)

        #fill in the frames
        self.init_top_left_frame(self.top_left_frame)
        self.init_bot_left_frame(self.bot_left_frame)
        self.init_top_right_frame(self.top_right_frame)
        self.init_bot_right_frame(self.bot_right_frame)
        self.init_info_box(self.info_box_frame)

        #so it always exist
        self.LR_pane_width = 0
        self.R_TB_pane_height = 0

        self.create_events()

        self.show_file_contents()

        self.init_analysis()
        
    def create_menu(self):
        #menu bar
        menubar = tk.Menu(self)
        self['menu'] = menubar
        
        #file menu
        self.file_menu = tk.Menu(menubar, tearoff=0)
        #new
        self.file_menu.add_command(label='New')
        #open
        self.file_menu.add_command(label='Open', command=self.open_file)
        #save
        self.file_menu.add_command(label='Save (Ctrl+s)', command=self.save_file)
        #save as
        self.file_menu.add_command(label='Save as', command=self.save_as_file)
        self.file_menu.add_separator()
        #exit
        self.file_menu.add_command(label='Exit', command=self.ask_quit)
        menubar.add_cascade(label='File', menu=self.file_menu)
        
        #edit menu
        self.edit_menu = tk.Menu(menubar, tearoff=0)
        #undo
        self.edit_menu.add_command(label='Undo')
        #print
        self.edit_menu.add_command(label='Print')
        menubar.add_cascade(label='Edit', menu=self.edit_menu)
        
        #help menu
        self.help_menu = tk.Menu(menubar, tearoff=0)
        #about
        self.help_menu.add_command(label='About', command=self.show_about_top)
        menubar.add_cascade(label='Help', menu=self.help_menu)

    def init_top_left_frame(self, parent):
        self.treeview = ttk.Treeview(parent, columns=[1,2,3,4], displaycolumns='#all', selectmode='browse')
        
        self.treeview.heading(1, text='Amount', anchor=tk.CENTER)
        self.treeview.heading(2, text='Description', anchor=tk.CENTER)
        self.treeview.heading(3, text='Type', anchor=tk.CENTER)
        self.treeview.heading(4, text='Date', anchor=tk.CENTER)

        self.treeview.column('#0', anchor=tk.E, stretch=False, width=20)
        self.treeview.column(1, anchor=tk.E, minwidth=60, stretch=False, width=140)
        self.treeview.column(2, anchor=tk.W, minwidth=90, stretch=False, width=300)
        self.treeview.column(3, anchor=tk.CENTER, minwidth=148, stretch=False, width=148)
        self.treeview.column(4, anchor=tk.W, minwidth=100, stretch=False, width=150)

        self.treeview.tag_configure('font', font=self.font2)
        self.treeview.tag_configure('font2', font=self.font2 + ('bold',))
        
        yscrollbar = ttk.Scrollbar(parent, orient='vertical', command=self.treeview.yview)
        self.treeview.config(yscrollcommand=yscrollbar.set)

        yscrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        self.treeview.pack(fill=tk.BOTH, expand=1)
        
    def init_bot_left_frame(self, parent):
        #entry boxes
        self.e_amount = ttk.Entry(parent, font=self.font1)
        self.e_name = ttk.Entry(parent, font=self.font1)
        self.e_type = ttk.Entry(parent, font=self.font1)

        #comboboxes
        self.sel_day, self.sel_month, self.sel_year = tk.StringVar(), tk.StringVar(), tk.StringVar()
        frame_date = ttk.Frame(parent)
        self.cb_day = ttk.Combobox(frame_date, state='readonly', width=3,
                                     values=['1', '2', '3', '4', '5', '6', '7', '8' ,'9', '10', '11', '12', '13',
                                             '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25',
                                             '26', '27', '28', '29', '30', '31'])
        self.cb_month = ttk.Combobox(frame_date, state='readonly', width=10,
                                     values=['January', 'February', 'March', 'April', 'May', 'June', 'July',
                                             'August', 'September', 'October', 'November', 'December'])
        self.cb_year = ttk.Combobox(frame_date, state='normal', width=5)
        self.cb_period = ttk.Combobox(parent, state='readonly', values=['Day', 'Week', 'Month', 'Quarter'], width=15)

        #labels
        label_amount = tk.Label(parent, text='Amount:', font=self.font1)
        label_name = tk.Label(parent, text='Description:', font=self.font1)
        label_type = tk.Label(parent, text='Type:', font=self.font1)
        label_date = tk.Label(parent, text='Date:', font=self.font1)
        label_period = tk.Label(parent, text='Period (Income):', font=self.font1)
        #Enter button
        self.enter_button = tk.Button(parent, text='Enter', font=self.font1, command=self.add_transaction)
        self.enter_button.config(width=15, height=4)
        #other buttons
        self.delete_last_button = tk.Button(parent, text='Delete Last Entry', font=self.font1, command=self.delete_last)
        self.delete_last_button.config(width=15)
        self.show_all_button = tk.Button(parent, text='Show/Hide All', font=self.font1, width=13, command=self.show_hide_all)
        self.open_calc_button = tk.Button(parent, text='Open Calculator', font=self.font1, width=13, command=lambda: os.system('start calc.exe'))

        #display buttons/text
        self.cb_day.grid(row=0, column=0, sticky='ewns')
        self.cb_month.grid(row=0, column=1, sticky='ewns')
        self.cb_year.grid(row=0, column=2, sticky='ewns')
        frame_date.columnconfigure(0, weight=1)
        frame_date.columnconfigure(1, weight=1)
        frame_date.columnconfigure(2, weight=1)
        
        label_amount.grid(padx=5, pady=6, sticky='W')
        label_name.grid(row=1, column=0, padx=5, pady=6, sticky='W')
        label_type.grid(row=2, column=0, padx=5, pady=6, sticky='W')
        label_date.grid(row=3, column=0, padx=5, pady=6, sticky='W')
        self.e_amount.grid(row=0, column=1, sticky='WE')
        self.e_name.grid(row=1, column=1, sticky='WE')
        self.e_type.grid(row=2, column=1, sticky='WE')
        frame_date.grid(row=3, column=1, sticky='WE')
        self.enter_button.grid(row=0, column=2, rowspan=3)
        self.delete_last_button.grid(row=3, column=2)
        label_period.grid(row=0, column=3)
        self.cb_period.grid(row=1, column=3)
        self.show_all_button.grid(row=2, column=3)
        self.open_calc_button.grid(row=3, column=3)

        parent.columnconfigure(1, weight=2, minsize=170)
        parent.columnconfigure(2, weight=1, minsize=140)
        parent.columnconfigure(3, weight=1, minsize=136)
        #initial conditions
        self.e_amount.focus_set()
        self.cb_day.current(dt.date.today().day - 1)
        self.cb_month.current(dt.date.today().month - 1)
        self.cb_year.set(dt.date.today().year)
        self.cb_period.current(self.default_period)

    def init_top_right_frame(self, parent):
        self.notebook = ttk.Notebook(parent, takefocus=False)
        self.notebook.pack(fill=tk.BOTH, expand=1)
        frame1 = ttk.Frame(self.notebook)
        frame2 = ttk.Frame(self.notebook)
        self.main_graph_frame = ttk.Frame(self.notebook)
        self.notebook.add(frame1, text='Analysis')
        self.notebook.add(frame2, text='Analysis 2')
        self.notebook.add(self.main_graph_frame, text='Graphs')
        
        #first tab (treeview2)
        self.treeview2 = ttk.Treeview(frame1, columns=[1,2,3,4,5,6,7], displaycolumns='#all', selectmode='browse', show=['headings'])
        self.treeview2.heading(1, text='* ago', anchor=tk.CENTER)
        self.treeview2.heading(2, text='Period', anchor=tk.CENTER)
        self.treeview2.heading(3, text='Needed', anchor=tk.CENTER)
        self.treeview2.heading(4, text='Extra', anchor=tk.CENTER)
        self.treeview2.heading(5, text='Income', anchor=tk.CENTER)
        self.treeview2.heading(6, text='Special', anchor=tk.CENTER)
        self.treeview2.heading(7, text='Bonuses', anchor=tk.CENTER)

        self.treeview2.column(1, anchor=tk.CENTER, minwidth=40, stretch=False, width=40)
        self.treeview2.column(2, anchor=tk.CENTER, minwidth=80, stretch=False, width=80)
        self.treeview2.column(3, anchor=tk.E, minwidth=57, stretch=True, width=90)
        self.treeview2.column(4, anchor=tk.E, minwidth=57, stretch=True, width=90)
        self.treeview2.column(5, anchor=tk.E, minwidth=57, stretch=True, width=90)
        self.treeview2.column(6, anchor=tk.E, minwidth=57, stretch=True, width=90)
        self.treeview2.column(7, anchor=tk.E, minwidth=57, stretch=True, width=90)

        self.treeview2.tag_configure('font', font=self.font3)
        
        yscrollbar = ttk.Scrollbar(frame1, orient='vertical', command=self.treeview2.yview)
        self.treeview2.config(yscrollcommand=yscrollbar.set)

        yscrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        self.treeview2.pack(fill=tk.BOTH, expand=1)

        #second tab (treeview3)
        self.treeview3 = ttk.Treeview(frame2, columns=[1,2,3,4,5], displaycolumns='#all', selectmode='browse', show=['headings'])
        self.treeview3.heading(1, text='* ago', anchor=tk.CENTER)
        self.treeview3.heading(2, text='Period', anchor=tk.CENTER)
        self.treeview3.heading(3, text='Essentials', anchor=tk.CENTER)
        self.treeview3.heading(4, text='Plus Extras', anchor=tk.CENTER)
        self.treeview3.heading(5, text='Net', anchor=tk.CENTER)

        self.treeview3.column(1, anchor=tk.CENTER, minwidth=40, stretch=False, width=40)
        self.treeview3.column(2, anchor=tk.CENTER, minwidth=80, stretch=False, width=80)
        self.treeview3.column(3, anchor=tk.E, minwidth=57, stretch=True, width=90)
        self.treeview3.column(4, anchor=tk.E, minwidth=57, stretch=True, width=90)
        self.treeview3.column(5, anchor=tk.E, minwidth=57, stretch=True, width=90)

        self.treeview3.tag_configure('font', font=self.font3)
        
        yscrollbar2 = ttk.Scrollbar(frame2, orient='vertical', command=self.treeview3.yview)
        self.treeview3.config(yscrollcommand=yscrollbar2.set)

        yscrollbar2.pack(fill=tk.Y, side=tk.RIGHT)
        self.treeview3.pack(fill=tk.BOTH, expand=1)

        #third tab (graph)
        self.create_figures(self.main_graph_frame)
    
    def init_bot_right_frame(self, parent):
        #labels
        label_period2 = tk.Label(parent, text='Period (Analysis):', font=self.font1)
        self.average_text1, self.average_text2 = tk.StringVar(), tk.StringVar()
        self.label_average1 = tk.Label(parent, font=self.font2, anchor='e', width=16, textvariable=self.average_text1)
        self.label_average2 = tk.Label(parent, font=self.font2, anchor='e', width=16, textvariable=self.average_text2)
        label_average = tk.Label(parent, text='Average:', font=self.font1)
        label_comma1 = tk.Label(parent, text=':', font=self.font1)
        label_comma2 = tk.Label(parent, text=':', font=self.font1)
        label_from = tk.Label(parent, text='from', font=self.font1)
        label_to = tk.Label(parent, text='to', font=self.font1)
        label_ago1 = tk.Label(parent, text='* ago', font=self.font1)
        label_ago2 = tk.Label(parent, text='* ago', font=self.font1)
        #Comboboxes
        self.cb_period2 = ttk.Combobox(parent, width=16, state='readonly', values=['Week', 'Month', 'Quarter', 'Year'])
        self.cb_average1 = ttk.Combobox(parent, width=12, state='readonly',
                                        values=['NONE', 'Needed', 'Extra', 'Income', 'Special', 'Bonuses', 'Essentials', 'Plus Extras', 'Net'])
        self.cb_average2 = ttk.Combobox(parent, width=12, state='readonly',
                                        values=['NONE', 'Needed', 'Extra', 'Income', 'Special', 'Bonuses', 'Essentials', 'Plus Extras', 'Net'])
        self.cb_start = ttk.Combobox(parent, width=3, state='readonly', values=[])
        self.cb_end = ttk.Combobox(parent, width=3, state='readonly', values=[])
        #quit button
        self.quit_button = tk.Button(parent, text='Quit', command=self.ask_quit)

        #arrange
        label_average.grid(row=0, column=0)
        self.cb_average1.grid(row=1, column=0, sticky='ew')
        label_comma1.grid(row=1, column=1)
        self.label_average1.grid(row=1, column=2, sticky='ew')
        label_from.grid(row=1, column=3, padx=10)
        self.cb_start.grid(row=1, column=4, sticky='ew')
        label_ago1.grid(row=1, column=5)
        self.cb_average2.grid(row=2, column=0, sticky='ew')
        label_comma2.grid(row=2, column=1)
        self.label_average2.grid(row=2, column=2, sticky='ew')
        label_to.grid(row=2, column=3)
        self.cb_end.grid(row=2, column=4, sticky='ew')
        label_ago2.grid(row=2, column=5)

        label_period2.grid(row=0, column=6, padx=10)
        self.cb_period2.grid(row=1, column=6)
        self.quit_button.grid(row=3, column=7)

        #initial conditions
        self.cb_period2.current(self.default_period2 - 1)
        self.cb_average1.current(0)
        self.cb_average2.current(0)
        
    def init_info_box(self, parent):
        self.info_text = tk.StringVar()
        self.info_text.set('Welcome')
        self.info_box = tk.Label(parent, font=self.font4, anchor=tk.W, textvariable=self.info_text)
        self.info_box.pack(fill='both', expand=1)

    def create_figures(self, parent):
        self.graph_frame1 = ttk.Frame(parent)
        self.toolbar_frame1 = ttk.Frame(parent)
        self.graph_frame2 = ttk.Frame(parent)
        self.toolbar_frame2 = ttk.Frame(parent)
        option_frame = ttk.Frame(parent)
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)
        
        figure1 = Figure(figsize=(0.1,0.1))
        self.axes1 = figure1.add_subplot(111)
        self.canvas1 = FigureCanvasTkAgg(figure1, self.graph_frame1)
        self.canvas1.draw()
        self.canvas1.get_tk_widget().pack(fill='both', expand=1)
        toolbar1 = NavigationToolbar2Tk(self.canvas1, self.toolbar_frame1)
        toolbar1.update()
        self.canvas1._tkcanvas.pack(fill='both', expand=1)

        figure2 = Figure(figsize=(0.1,0.1))
        self.axes2 = figure2.add_subplot(111)
        self.canvas2 = FigureCanvasTkAgg(figure2, self.graph_frame2)
        self.canvas2.draw()
        self.canvas2.get_tk_widget().pack(fill='both', expand=1)
        toolbar2 = NavigationToolbar2Tk(self.canvas1, self.toolbar_frame2)
        toolbar2.update()
        self.canvas2._tkcanvas.pack(fill='both', expand=1)

        self.cb_graph = ttk.Combobox(option_frame, width=10, state='readonly', values=['Bar Graph', 'Other'])
        self.check_var1 = tk.IntVar()
        self.check_var2 = tk.IntVar()
        self.check_var3 = tk.IntVar()
        self.check_var4 = tk.IntVar()
        self.check_var5 = tk.IntVar()
        self.check_graph1 = ttk.Checkbutton(option_frame, text='1', variable=self.check_var1,
                                            command=lambda: self.create_graphs(self.analysis))
        self.check_graph2 = ttk.Checkbutton(option_frame, text='2', variable=self.check_var2,
                                            command=lambda: self.create_graphs(self.analysis))
        self.check_graph3 = ttk.Checkbutton(option_frame, text='3', variable=self.check_var3,
                                            command=lambda: self.create_graphs(self.analysis))
        self.check_graph4 = ttk.Checkbutton(option_frame, text='4', variable=self.check_var4,
                                            command=lambda: self.create_graphs(self.analysis))
        self.check_graph5 = ttk.Checkbutton(option_frame, text='5', variable=self.check_var5,
                                            command=lambda: self.create_graphs(self.analysis))
        self.check_graph1.pack(side='left', expand=1)
        self.check_graph2.pack(side='left', expand=1)
        self.check_graph3.pack(side='left', expand=1)
        self.check_graph4.pack(side='left', expand=1)
        self.check_graph5.pack(side='left', expand=1)
        self.cb_graph.pack(expand=1)

        self.graph_frame1.grid(row=0, column=0, columnspan=2, sticky='ewns')
        self.toolbar_frame1.grid(row=1, column=0, sticky='ewns')
        option_frame.grid(row=1, column=1, ipadx=10, sticky='ewns')

        self.cb_graph.current(0)
        self.axes1.invert_xaxis()

    '''EVENTS AND BINDINGS ----------------------------------------------------------'''
    def create_events(self):
        #when closing window
        self.protocol('WM_DELETE_WINDOW', self.ask_quit)
        
        #what enter does
        self.e_amount.bind('<Return>', self.focus1)
        self.e_amount.bind('<KeyPress-Down>', self.focus1)
        self.e_amount.bind('<KeyPress-Right>', self.focus3)
        
        self.e_name.bind('<Return>', self.focus2)
        self.e_name.bind('<KeyPress-Down>', self.focus2)
        self.e_name.bind('<KeyPress-Up>', self.focus6)
        self.e_name.bind('<KeyPress-Right>', self.focus3)
        
        self.e_type.bind('<Return>', self.focus3)
        self.e_type.bind('<KeyPress-Down>', self.focus7)
        self.e_type.bind('<KeyPress-Up>', self.focus1)
        self.e_type.bind('<KeyPress-Right>', self.focus3)
        
        self.enter_button.bind('<Return>', self.focus4)
        self.enter_button.bind('<space>', self.focus6)
        self.enter_button.bind('<KeyPress-Left>', self.focus6)
        self.enter_button.bind('<KeyPress-Down>', self.focus10)

        self.cb_day.bind('<KeyPress-Right>', self.focus8)
        self.cb_day.bind('<KeyPress-Up>', self.focus2)
        self.cb_day.bind('<KeyPress-Left>', self.focus2)

        self.cb_month.bind('<KeyPress-Right>', self.focus9)
        self.cb_month.bind('<KeyPress-Up>', self.focus2)
        self.cb_month.bind('<KeyPress-Left>', self.focus7)

        self.cb_year.bind('<KeyPress-Right>', self.focus3)
        self.cb_year.bind('<KeyPress-Up>', self.focus2)
        self.cb_year.bind('<KeyPress-Left>', self.focus8)

        self.delete_last_button.bind('<Return>', self.focus11)
        self.delete_last_button.bind('<KeyPress-Left>', self.focus6)
        self.delete_last_button.bind('<KeyPress-Up>', self.focus3)

        #select new period
        self.cb_period.bind('<<ComboboxSelected>>', self.change_period)
        self.cb_period2.bind('<<ComboboxSelected>>', self.change_period2)

        #select new graph type
        self.cb_graph.bind('<<ComboboxSelected>>', self.change_graph)

        #select new average to analyse
        self.cb_average1.bind('<<ComboboxSelected>>', lambda e: self.change_average(e, 1))
        self.cb_average2.bind('<<ComboboxSelected>>', lambda e: self.change_average(e, 2))
        self.cb_start.bind('<<ComboboxSelected>>', lambda e: self.change_average(e, 1))
        self.cb_start.bind('<<ComboboxSelected>>', lambda e: self.change_average(e, 2), add='+')
        self.cb_end.bind('<<ComboboxSelected>>', lambda e: self.change_average(e, 1))
        self.cb_end.bind('<<ComboboxSelected>>', lambda e: self.change_average(e, 2), add='+')

    '''EVENT HANDLERS --------------------------------------------------------------------------------------'''
    def ask_quit(self):
        if self.changed == True:
            answer = messagebox.askyesno('Save before closing?', 'Do you want to save before closing?')
            if answer:
                self.save_file()
                self.destroy()
            else:
                self.destroy()
        else:
            self.destroy()
        
        
    def focus1(self, event):
        self.e_name.focus_set()

    def focus2(self, event):
        self.e_type.focus_set()

    def focus3(self, event):
        self.enter_button.focus_set()

    def focus4(self, event):
        #self.enter_button.config(relief='sunken')
        self.enter_button.invoke()
        #self.enter_button.unbind('<Return>')
        #self.enter_button.bind('<KeyRelease-Return>', self.focus5)

    def focus5(self, event):
        self.enter_button.config(relief='raised')
        self.enter_button.unbind('<KeyRelease-Return>')
        self.enter_button.bind('<Return>', self.focus4)

    def focus6(self, event):
        self.e_amount.focus_set()

    def focus7(self, event):
        self.cb_day.focus_set()

    def focus8(self, event):
        self.cb_month.focus_set()

    def focus9(self, event):
        self.cb_year.focus_set()

    def focus10(self, event):
        self.delete_last_button.focus_set()

    def focus11(self, event):
        self.delete_last_button.config(relief='sunken')
        self.delete_last_button.invoke()
        self.delete_last_button.unbind('<Return>')
        self.delete_last_button.bind('<KeyRelease-Return>', self.focus12)

    def focus12(self, event):
        self.delete_last_button.config(relief='raised')
        self.delete_last_button.unbind('<KeyRelease-Return>')
        self.delete_last_button.bind('<Return>', self.focus11)

    def change_period(self, event):
        cur_period = self.cb_period.current()
        if cur_period != self.period:
            dict_ = {0:'Days', 1:'Weeks', 2:'Months', 3:'Quarters', 4:'Years'}
            self.period = cur_period
            self.show_file_contents()
            self.info_text.set('Income view period changed to: {}'.format(dict_[self.period]))

    def change_period2(self, event):
        cur_period = self.cb_period2.current() + 1
        if cur_period != self.period2:
            dict_ = {0:'Days', 1:'Weeks', 2:'Months', 3:'Quarters', 4:'Years'}
            self.period2 = cur_period
            self.init_analysis()
            self.info_text.set('Analysis period changed to: {}'.format(dict_[self.period2]))

    def change_graph(self, event):
        current = self.main_graph_frame.grid_slaves(column=0)
        if self.cb_graph.current() == 0:
            current[0].grid_forget()
            current[1].grid_forget()
            self.graph_frame1.grid(row=0, column=0, columnspan=2, sticky='ewns')
            self.toolbar_frame1.grid(row=1, column=0, sticky='ewns')
        elif self.cb_graph.current() == 1:
            current[0].grid_forget()
            current[1].grid_forget()
            self.graph_frame2.grid(row=0, column=0, columnspan=2, sticky='ewns')
            self.toolbar_frame2.grid(row=1, column=0, sticky='ewns')
        else:
            print('Strange Error (change_graph)')
    
    def change_average(self, event, num):
        self.set_average_text(self.analysis, num)

    """COMMANDS/EXECUTIONS ==========================================================="""
    def load_file(self, filename):
        file = open(filename, 'r')
        self.transactions = []
        lines = file.readlines()
        file.close()
        comparison = '[PACX save file]\n'
        if lines[0] == comparison:
            lines = lines[1:]
            for line in lines:
                if line[:3] == 't//':
                    self.transactions += [self.parse_txt_file(line[:-1])]
                else:
                    raise IOError('file transaction indent error')
            self.transactions.sort(key=lambda t: t.get_date())
        else:
            raise IOError('File incompatible')

    #show from self.transactions
    def show_file_contents(self):
        self.treeview.delete(*self.treeview.get_children())
        self.treeview.yview('moveto', 0)
        #if there are transactions
        if len(self.transactions) > 0:
            #days
            if self.period == 0:
                for t in self.transactions:
                    self.t_to_screen('', t, index='end')
                #see fully the selected line
                self.treeview.yview('moveto', 0)
                self.select_line(self.treeview, self.treeview.get_children()[-1])
                    
            #weeks
            elif self.period == 1:
                #{weekday:[difference days to monday, difference days to sunday]}
                dict_ = {0:[0, 6], 1:[1, 5], 2:[2, 4], 3:[3, 3], 4:[4, 2], 5:[5, 1], 6:[6, 0]}
                #insert first transaction
                date, weekday = self.transactions[0].get_date(), self.transactions[0].get_date().weekday()
                self.t_to_screen_newperiod(self.transactions[0], index='end')
                if len(self.transactions) >= 2:
                    #insert the rest
                    for t in self.transactions[1:]:
                        delta = t.get_date() - date
                        if delta.days <= dict_[weekday][1]:
                            self.t_to_screen(self.treeview.get_children()[-1], t, index='end')
                        else:
                            date, weekday = t.get_date(), t.get_date().weekday()
                            self.t_to_screen_newperiod(t, index='end')

                #close other children
                if len(self.treeview.get_children()) > 1:
                    for child in self.treeview.get_children()[:-1]:
                        self.treeview.item(child, open=False)
                #see fully the selected line
                self.select_line(self.treeview, self.treeview.get_children(self.treeview.get_children()[-1])[-1])
                
            #months
            elif self.period == 2:
                month, year = None, None
                for t in self.transactions:
                    if t.get_date().month == month and t.get_date().year == year:
                        self.t_to_screen(self.treeview.get_children()[-1], t, index='end')
                    else:
                        month, year = t.get_date().month, t.get_date().year
                        self.t_to_screen_newperiod(t, index='end')
                
                if len(self.treeview.get_children()) > 1:
                    for child in self.treeview.get_children()[:-1]:
                        self.treeview.item(child, open=False)
                #see fully the selected line
                self.select_line(self.treeview, self.treeview.get_children(self.treeview.get_children()[-1])[-1])
            #quarters
            elif self.period == 3:
                dict_ = {1:[1, 2, 3], 2:[4, 5, 6], 3:[7, 8, 9], 4:[10, 11, 12], None:[None]}
                quarter, year = None, None
                for t in self.transactions:
                    if t.get_date().month in dict_[quarter] and t.get_date().year == year:
                        self.t_to_screen(self.treeview.get_children()[-1], t, index='end')
                    else:
                        quarter, year = math.ceil(t.get_date().month / 3), t.get_date().year
                        self.t_to_screen_newperiod(t, 'end')
                
                if len(self.treeview.get_children()) > 1:
                    for child in self.treeview.get_children()[:-1]:
                        self.treeview.item(child, open=False)
                #see fully the selected line
                self.select_line(self.treeview, self.treeview.get_children(self.treeview.get_children()[-1])[-1])
        #do nothing if there are no transactions
        else:
            pass

    def init_analysis(self):
        self.treeview2.delete(*self.treeview2.get_children())
        self.treeview3.delete(*self.treeview3.get_children())
        self.treeview2.yview('moveto', 0)
        self.treeview3.yview('moveto', 0)
        period_transaction_dict = {}
        if len(self.transactions) > 0:
            if self.period2 == 1:
                dict_ = {0:[0, 6], 1:[1, 5], 2:[2, 4], 3:[3, 3], 4:[4, 2], 5:[5, 1], 6:[6, 0]}
                #weeks are strings
                min_week = self.convert_date_str(self.transactions[0].get_date() -
                                                 dt.timedelta(days=self.transactions[0].get_date().weekday()))
                max_week = self.convert_date_str(self.transactions[-1].get_date() -
                                                 dt.timedelta(days=self.transactions[-1].get_date().weekday()))
                
                period_transaction_dict[min_week] = [self.transactions[0]]
                if len(self.transactions) > 1:
                    week = min_week
                    for t in self.transactions[1:]:
                        while t.get_date() - dt.timedelta(days=t.get_date().weekday()) != self.convert_date_str(week):
                            week = self.convert_date_str(self.convert_date_str(week) + dt.timedelta(days=7))
                            period_transaction_dict[week] = []
                            if self.convert_date_str(week) > self.convert_date_str(max_week):
                                raise ValueError('Strange Error (init_analysis)')
                        period_transaction_dict[week].append(t)
                
            elif self.period2 == 2:
                min_month = (self.transactions[0].get_date().month, self.transactions[0].get_date().year)
                max_month = (self.transactions[-1].get_date().month, self.transactions[-1].get_date().year)
                
                period_transaction_dict[min_month] = [self.transactions[0]]
                if len(self.transactions) > 1:
                    month, year = min_month[0], min_month[1]
                    for t in self.transactions[1:]:
                        while (t.get_date().month, t.get_date().year) != (month, year):
                            if month < 12:
                                month = month + 1
                            else:
                                month = 1
                                year = year + 1
                            period_transaction_dict[(month, year)] = []
                            if year > max_month[1]:
                                raise ValueError('Strange Error (init_analysis)')
                        period_transaction_dict[(month, year)].append(t)
                
            elif self.period2 == 3:
                min_quarter = (math.ceil(self.transactions[0].get_date().month / 3), self.transactions[0].get_date().year)
                max_quarter = (math.ceil(self.transactions[-1].get_date().month / 3), self.transactions[-1].get_date().year)
                
                period_transaction_dict[min_quarter] = [self.transactions[0]]
                if len(self.transactions) > 1:
                    quarter, year = min_quarter[0], min_quarter[1]
                    for t in self.transactions[1:]:
                        while (math.ceil(t.get_date().month / 3), t.get_date().year) != (quarter, year):
                            if quarter < 4:
                                quarter = quarter + 1
                            else:
                                quarter = 1
                                year = year + 1
                            period_transaction_dict[(quarter, year)] = []
                            if year > max_quarter[1]:
                                raise ValueError('Strange Error (init_analysis)')
                        period_transaction_dict[(quarter, year)].append(t)
                
            elif self.period2 == 4:
                min_year = self.transactions[0].get_date().year
                max_year = self.transactions[-1].get_date().year
                
                period_transaction_dict[min_year] = [self.transactions[0]]
                if len(self.transactions) > 1:
                    year = min_year
                    for t in self.transactions[1:]:
                        while t.get_date().year != year:
                            year = year + 1
                            period_transaction_dict[year] = []
                        
                        period_transaction_dict[year].append(t)
            
            #get analysis from 'period_transaction_dict', then display that.
            self.analysis = self.analyse_data(period_transaction_dict, self.transactions[0].get_date(), self.transactions[-1].get_date())
            
            self.display_analysis(self.analysis)

            #plot the graphs
            self.create_graphs(self.analysis)

            #set the average values
            self.set_average_start_end(self.analysis)

            self.set_average_text(self.analysis, 1)
            self.set_average_text(self.analysis, 2)

        else:
            pass

    def analyse_data(self, period_dict, min_date, max_date):
        items_to_return = []
        
        if self.period2 == 1:
            min_week_date = min_date - dt.timedelta(days=min_date.weekday())
            week = self.convert_date_str(min_week_date)
            weeks_ago = (dt.date.today() - dt.timedelta(days=dt.date.today().weekday()))  - min_week_date
            weeks_ago = weeks_ago.days // 7
            while self.convert_date_str(week) <= max_date:
                period_str = week
                temp_dict = {'ago':weeks_ago, 'period':period_str, 1:0, 2:0, 3:0, 4:0, 5:0}
                for t in period_dict[week]:
                    temp_dict[t.get_type()] += float(t.get_amount())
                items_to_return.append(temp_dict)
                week = self.convert_date_str(self.convert_date_str(week) + dt.timedelta(days=7))
                weeks_ago -= 1
            
        elif self.period2 == 2:
            month, year = min_date.month, min_date.year
            months_ago = (dt.date.today().year - year) * 12 + (dt.date.today().month - month)
            while (month, year) != (max_date.month, max_date.year):
                period_str = '{} {}'.format(self.month_name(month), str(year))
                temp_dict = {'ago':months_ago, 'period':period_str, 1:0, 2:0, 3:0, 4:0, 5:0}
                for t in period_dict[(month, year)]:
                    temp_dict[t.get_type()] += float(t.get_amount())
                items_to_return.append(temp_dict)
                if month < 12:
                    month = month + 1
                else:
                    month = 1
                    year = year + 1
                months_ago -= 1
            period_str = '{} {}'.format(self.month_name(month), str(year))
            temp_dict = {'ago':months_ago, 'period':period_str, 1:0, 2:0, 3:0, 4:0, 5:0}
            for t in period_dict[(month, year)]:
                temp_dict[t.get_type()] += float(t.get_amount())
            items_to_return.append(temp_dict)
            
        elif self.period2 == 3:
            quarter, year = math.ceil(min_date.month / 3), min_date.year
            quarters_ago = (dt.date.today().year - year) * 4 + (math.ceil(dt.date.today().month / 3) - quarter)
            while (quarter, year) != (math.ceil(max_date.month / 3), max_date.year):
                period_str = 'Q{0} {1}'.format(quarter, str(year))
                temp_dict = {'ago':quarters_ago, 'period':period_str, 1:0, 2:0, 3:0, 4:0, 5:0}
                for t in period_dict[(quarter, year)]:
                    temp_dict[t.get_type()] += float(t.get_amount())
                items_to_return.append(temp_dict)
                if quarter < 4:
                    quarter = quarter + 1
                else:
                    quarter = 1
                    year = year + 1
                quarters_ago -= 1
            period_str = 'Q{0} {1}'.format(quarter, str(year))
            temp_dict = {'ago':quarters_ago, 'period':period_str, 1:0, 2:0, 3:0, 4:0, 5:0}
            for t in period_dict[(quarter, year)]:
                temp_dict[t.get_type()] += float(t.get_amount())
            items_to_return.append(temp_dict)
            
        elif self.period2 == 4:
            year = min_date.year
            years_ago = dt.date.today().year - year
            while year <= max_date.year:
                period_str = str(year)
                temp_dict = {'ago':years_ago, 'period':period_str, 1:0, 2:0, 3:0, 4:0, 5:0}
                for t in period_dict[year]:
                    temp_dict[t.get_type()] += float(t.get_amount())
                items_to_return.append(temp_dict)
                year = year + 1
                years_ago -= 1
            
        #returns a list of dictionaries for each period, with item data
        return items_to_return

    def display_analysis(self, analysis):
        for a in analysis:
            #iid is period minus the whitespace
            self.treeview2.insert('', 'end', iid=a['period'].replace(' ', ''), tags=['font'],
                            values=[a['ago'], a['period'], self.currency(a[1]), self.currency(a[2]), self.currency(a[3]),
                                    self.currency(a[4]), self.currency(a[5])])
            self.treeview3.insert('', 'end', iid=a['period'].replace(' ', ''), tags=['font'],
                                  values=[a['ago'], a['period'], self.currency(a[1] + a[3]),
                                          self.currency(a[1] + a[2] + a[3]), self.currency(a[1] + a[2] + a[3] + a[4] + a[5])])
        self.treeview2.yview('moveto', 0)
        self.treeview2.see(self.treeview2.get_children()[-1])
        self.treeview3.yview('moveto', 0)
        self.treeview3.see(self.treeview3.get_children()[-1])

    def create_graphs(self, analysis):
        self.axes1.clear()
        self.axes2.clear()
        
        if self.period2 == 1:
            dates = np.array([x['ago'] for x in analysis])
            data = np.array([self.check_var1.get() * x[1] + self.check_var2.get() * x[2] + self.check_var3.get() * x[3] +
                             self.check_var4.get() * x[4] + self.check_var5.get() * x[5] for x in analysis])
            self.axes1.set_xlabel('Weeks Ago')
            #self.axes1.set_xticklabels(['W{}'.format(x['ago']) for x in analysis])
        elif self.period2 == 2:
            dates = np.array([x['ago'] for x in analysis])
            data = np.array([self.check_var1.get() * x[1] + self.check_var2.get() * x[2] + self.check_var3.get() * x[3] +
                             self.check_var4.get() * x[4] + self.check_var5.get() * x[5] for x in analysis])
            self.axes1.set_xlabel('Months Ago')
            #self.axes1.set_xticklabels(['M{}'.format(x['ago']) for x in analysis])
        elif self.period2 == 3:
            dates = np.array([x['ago'] for x in analysis])
            data = np.array([self.check_var1.get() * x[1] + self.check_var2.get() * x[2] + self.check_var3.get() * x[3] +
                             self.check_var4.get() * x[4] + self.check_var5.get() * x[5] for x in analysis])
            self.axes1.set_xlabel('Quarters Ago')
        elif self.period2 == 4:
            dates = np.array([x['ago'] for x in analysis])
            data = np.array([self.check_var1.get() * x[1] + self.check_var2.get() * x[2] + self.check_var3.get() * x[3] +
                             self.check_var4.get() * x[4] + self.check_var5.get() * x[5] for x in analysis])
            self.axes1.set_xlabel('Years Ago')
        else:
            print('Strange error (create_graphs)')

        self.axes1.bar(dates, data, width=1, align='edge')
        self.axes1.axhline(y=0, linewidth=2, color='black')

        self.axes1.set_xlim(left=len(analysis), right=0)
        self.axes1.set_xticks(np.arange(len(analysis)))
        self.axes1.grid(True, which='both')
        self.create_graph_ylabel()
        self.canvas1.draw()
            
    def create_graph_ylabel(self):
        c = (self.check_var1.get(), self.check_var2.get(), self.check_var3.get(), self.check_var4.get(), self.check_var5.get())
        dict1 = {0:'Needed Expenses', 1:'Extra Expenses', 2:'Income', 3:'Special Expenses', 4:'Bonuses'}
        if c == (0, 0, 0, 0, 0):
            self.axes1.set_ylabel('None')
        elif sum(c) == 1:
            self.axes1.set_ylabel(dict1[c.index(1)])
            
        elif c == (1, 1, 0, 0, 0):
            self.axes1.set_ylabel('Needed + Extra Expenses')
        elif c == (1, 0, 0, 1, 0):
            self.axes1.set_ylabel('Needed + Special Expenses')
        elif c == (0, 1, 0, 1, 0):
            self.axes1.set_ylabel('Extra + Special Expenses')
        elif sum(c) == 2:
            first_i = c.index(1)
            self.axes1.set_ylabel(' + '.join([dict1[first_i], dict1[c[first_i + 1:].index(1) + first_i + 1]]))
            
        elif c == (1, 1, 1, 0, 0):
            self.axes1.set_ylabel('Needed + Extra + Income')
        elif c == (1, 1, 0, 1, 0):
            self.axes1.set_ylabel('Needed + Extra + Special')
        elif c == (1, 1, 0, 0, 1):
            self.axes1.set_ylabel('Needed + Extra + Bonuses')
        elif c == (1, 0, 1, 1, 0):
            self.axes1.set_ylabel('Needed + Income + Special')
        elif c == (1, 0, 1, 0, 1):
            self.axes1.set_ylabel('Needed + Income + Bonuses')
        elif c == (1, 0, 0, 1, 1):
            self.axes1.set_ylabel('Needed + Special + Bonuses')
        elif c == (0, 1, 1, 1, 0):
            self.axes1.set_ylabel('Extra + Income + Special')
        elif c == (0, 1, 1, 0, 1):
            self.axes1.set_ylabel('Extra + Income + Bonuses')
        elif c == (0, 1, 0, 1, 1):
            self.axes1.set_ylabel('Extra + Special + Bonuses')
        elif c == (0, 0, 1, 1, 1):
            self.axes1.set_ylabel('Income + Special + Bonuses')
        elif c == (1, 1, 1, 1, 0):
            self.axes1.set_ylabel('Needed + Extra + Income + Special')
        elif c == (1, 1, 1, 0, 1):
            self.axes1.set_ylabel('Needed + Extra + Income + Bonuses')
        elif c == (1, 1, 0, 1, 1):
            self.axes1.set_ylabel('Needed + Extra + Special + Bonuses')
        elif c == (1, 0, 1, 1, 1):
            self.axes1.set_ylabel('Needed + Income + Special + Bonuses')
        elif c == (0, 1, 1, 1, 1):
            self.axes1.set_ylabel('Extra + Income + Special + Bonuses')
        elif c == (1, 1, 1, 1, 1):
            self.axes1.set_ylabel('Net')
        else:
            self.axes1.set_ylabel('zzzzzzzzzzzzzzzzzzzz')

    def set_average_start_end(self, analysis):
        min_ago = analysis[-1]['ago']
        max_ago = analysis[0]['ago']
        values = [x for x in range(min_ago, max_ago + 1)]
        self.cb_start.config(values=values)
        self.cb_end.config(values=values)
        self.cb_start.current(0)
        self.cb_end.current(len(values) - 1)

    def set_average_text(self, analysis, combobox_num):
        if combobox_num == 1:
            index = self.cb_average1.current()
            strvar = self.average_text1
        elif combobox_num == 2:
            index = self.cb_average2.current()
            strvar = self.average_text2
        else:
            raise TypeError('Strange error (set_average_text)')
        
        #NONE
        if index == 0:
            strvar.set('Select an option')
        else:
            start_index = self.cb_start.current()
            end_index = self.cb_end.current()
            if start_index > end_index:
                start_index, end_index = end_index, start_index
            list_ = []
            #Needed
            if index == 1:
                for dict_ in analysis[len(analysis) - end_index - 1:len(analysis) - start_index]:
                    list_.append(dict_[1])
            #Extra
            elif index == 2:
                for dict_ in analysis[len(analysis) - end_index - 1:len(analysis) - start_index]:
                    list_.append(dict_[2])
            #Income
            elif index == 3:
                for dict_ in analysis[len(analysis) - end_index - 1:len(analysis) - start_index]:
                    list_.append(dict_[3])
            #Special
            elif index == 4:
                for dict_ in analysis[len(analysis) - end_index - 1:len(analysis) - start_index]:
                    list_.append(dict_[4])
            #Bonus
            elif index == 5:
                for dict_ in analysis[len(analysis) - end_index - 1:len(analysis) - start_index]:
                    list_.append(dict_[5])
            #Essentials
            elif index == 6:
                for dict_ in analysis[len(analysis) - end_index - 1:len(analysis) - start_index]:
                    list_.append(dict_[1] + dict_[3])
            #Plus Extras
            elif index == 7:
                for dict_ in analysis[len(analysis) - end_index - 1:len(analysis) - start_index]:
                    list_.append(dict_[1] + dict_[2] + dict_[3])
            #Net
            elif index == 8:
                for dict_ in analysis[len(analysis) - end_index - 1:len(analysis) - start_index]:
                    list_.append(dict_[1] + dict_[2] + dict_[3] + dict_[4] + dict_[5])
            else:
                raise TypeError('Strange error2 (set_average_text)')
            
            mean = np.mean(list_)
            strvar.set(self.currency(mean))


    #'transaction' is the transaction that is created or deleted
    def refresh_analysis(self, analysis, transaction=None):
        self.init_analysis()
        
        if transaction != None:
            if self.period2 == 1:
                changed = self.convert_date_str(transaction.get_date() - dt.timedelta(days=transaction.get_date().weekday()))
            elif self.period2 == 2:
                changed = self.month_name(transaction.get_date().month) + str(transaction.get_date().year)
            elif self.period2 == 3:
                changed = 'Q{}{}'.format(math.ceil(transaction.get_date().month / 3), transaction.get_date().year)
            elif self.period2 == 4:
                changed = str(transaction.get_date().year)

            if changed in self.treeview2.get_children():
                self.select_line(self.treeview2, changed)
                self.select_line(self.treeview3, changed)

    def add_transaction(self):
        #enter button command
        #gets and checks entries
        valid = True
        valid_except_date = False
        if self.e_amount.get() == '' and self.e_name.get() == '' and self.e_type.get() == '':
            self.info_text.set('Empty entries...')
        else:
            try:
                amount = float(self.e_amount.get())
            except:
                valid = False
            name = self.e_name.get()
            try:
                type_ = int(self.e_type.get())
                test = transaction.type_to_text(type_)
            except:
                valid = False
            #stores and display entry
            if valid:
                try:
                    date = dt.date(int(self.cb_year.get()), self.cb_month.current() + 1, int(self.cb_day.get()))
                except:
                    valid_except_date = True
                if valid_except_date:
                    self.info_text.set('Select a valid date...')
                else:
                    #delete entries
                    self.e_amount.delete(0, 'end')
                    self.e_name.delete(0, 'end')
                    self.e_type.delete(0, 'end')
                    t = transaction.Transaction(amount, name, type_, date)
                    
                    #insert into self.transactions according to date
                    inserted = False
                    temp_list = self.transactions[:]
                    #if self.transactions is empty:
                    if len(self.transactions) == 0:
                        self.transactions.insert(0, t)
                        inserted = True
                    #if self.transactions is not empty:
                    while not inserted:
                        if t.get_date() >= temp_list[-1].get_date():
                            self.transactions.insert(len(temp_list), t)
                            inserted = True
                        else:
                            temp_list.pop()
                            if len(temp_list) == 0:
                                self.transactions.insert(0, t)
                                inserted = True

                    #check for different periods to display
                    #if self.transactions is empty:
                    if len(self.treeview.get_children()) == 0:
                        i = self.t_to_screen_newperiod(t, 0)
                        self.select_line(self.treeview, i[1])
                    else:
                        #days
                        if self.period == 0:
                            i = self.t_to_screen('', t, index=len(temp_list))
                            self.select_line(self.treeview, i)

                        #weeks
                        elif self.period == 1:
                            temp_item = self.treeview.get_children()[-1]
                            got_item = False
                            inserted = False
                            while not got_item:
                                #if newer period
                                if t.get_date() >= self.convert_date_str(temp_item) + dt.timedelta(days=7):
                                    i = self.t_to_screen_newperiod(t, index=self.treeview.index(temp_item) + 1)
                                    got_item = True
                                    inserted = True
                                    #show both period and transaction on screen
                                    self.treeview.see(i[0])
                                    self.select_line(self.treeview, i[1])
                                #if older period, go back one period
                                elif t.get_date() < self.convert_date_str(temp_item):
                                    temp_item = self.treeview.prev(temp_item)
                                    if temp_item == '':
                                        i = self.t_to_screen_newperiod(t, index=0)
                                        got_item = True
                                        inserted = True
                                        self.treeview.see(i[0])
                                        self.select_line(self.treeview, i[1])
                                #otherwise, insert transaction in current period
                                else:
                                    i = temp_item
                                    got_item = True
                            if not inserted:
                                temp_transaction = self.treeview.get_children(i)[-1]
                                while not inserted:
                                    if t.get_date() >= self.convert_date_str(self.treeview.set(temp_transaction, column=4)):
                                        i2 = self.t_to_screen(i, t, index=self.treeview.index(temp_transaction) + 1)
                                        inserted = True
                                        self.treeview.see(i)
                                        self.select_line(self.treeview, i2)

                                    else:
                                        temp_transaction = self.treeview.prev(temp_transaction)
                                        if temp_transaction == '':
                                            i2 = self.t_to_screen(i, t, index=0)
                                            inserted = True
                                            self.treeview.see(i)
                                            self.select_line(self.treeview, i2)

                        #months
                        elif self.period == 2:
                            temp_item = self.treeview.get_children()[-1]
                            got_item = False
                            inserted = False
                            while not got_item:
                                #if newer period
                                if t.get_date().year > int(temp_item[temp_item.index(',') + 1:]) or\
                                (t.get_date().year == int(temp_item[temp_item.index(',') + 1:]) and t.get_date().month > int(temp_item[:temp_item.index(',')])):
                                    i = self.t_to_screen_newperiod(t, index=self.treeview.index(temp_item) + 1)
                                    got_item = True
                                    inserted = True
                                    #show both period and transaction on screen
                                    self.treeview.see(i[0])
                                    self.select_line(self.treeview, i[1])
                                #if same period
                                elif temp_item == str(t.get_date().month) + ',' + str(t.get_date().year):
                                    i = temp_item
                                    got_item = True
                                #otherwise, go back one period
                                else:
                                    temp_item = self.treeview.prev(temp_item)
                                    #if new transaction is ealiest
                                    if temp_item == '':
                                        i = self.t_to_screen_newperiod(t, index=0)
                                        got_item = True
                                        inserted = True
                                        self.treeview.see(i[0])
                                        self.select_line(self.treeview, i[1])
                            if not inserted:
                                temp_transaction = self.treeview.get_children(i)[-1]
                                while not inserted:
                                    if t.get_date() >= self.convert_date_str(self.treeview.set(temp_transaction, column=4)):
                                        i2 = self.t_to_screen(i, t, index=self.treeview.index(temp_transaction) + 1)
                                        inserted = True
                                        self.treeview.see(i)
                                        self.select_line(self.treeview, i2)
                                    else:
                                        temp_transaction = self.treeview.prev(temp_transaction)
                                        if temp_transaction == '':
                                            i2 = self.t_to_screen(i, t, index=0)
                                            inserted = True
                                            self.treeview.see(i)
                                            self.select_line(self.treeview, i2)

                        #quarters
                        elif self.period == 3:
                            temp_item = self.treeview.get_children()[-1]
                            got_item = False
                            inserted = False
                            while not got_item:
                                #if newer period
                                if (t.get_date().month > int(temp_item[:temp_item.index(',')]) * 3 and t.get_date().year >= int(temp_item[temp_item.index(',') + 1:]))\
                                   or t.get_date().year > int(temp_item[temp_item.index(',') + 1:]):
                                    i = self.t_to_screen_newperiod(t, index=self.treeview.index(temp_item) + 1)
                                    got_item = True
                                    inserted = True
                                    #show both period and transaction on screen
                                    self.treeview.see(i[0])
                                    self.select_line(self.treeview, i[1])
                                #if older period, go back one period
                                elif (t.get_date().month < int(temp_item[:temp_item.index(',')]) * 3 - 2 and t.get_date().year <= int(temp_item[temp_item.index(',') + 1:]))\
                                   or t.get_date().year < int(temp_item[temp_item.index(',') + 1:]):
                                    temp_item = self.treeview.prev(temp_item)
                                    if temp_item == '':
                                        i = self.t_to_screen_newperiod(t, index=0)
                                        got_item = True
                                        inserted = True
                                        self.treeview.see(i[0])
                                        self.select_line(self.treeview, i[1])
                                #otherwise, insert transaction in current period
                                else:
                                    i = temp_item
                                    got_item = True
                            if not inserted:
                                temp_transaction = self.treeview.get_children(i)[-1]
                                while not inserted:
                                    if t.get_date() >= self.convert_date_str(self.treeview.set(temp_transaction, column=4)):
                                        i2 = self.t_to_screen(i, t, index=self.treeview.index(temp_transaction) + 1)
                                        inserted = True
                                        self.treeview.see(i)
                                        self.select_line(self.treeview, i2)
                                    else:
                                        temp_transaction = self.treeview.prev(temp_transaction)
                                        if temp_transaction == '':
                                            i2 = self.t_to_screen(i, t, index=0)
                                            inserted = True
                                            self.treeview.see(i)
                                            self.select_line(self.treeview, i2)
                    self.refresh_analysis(self.analysis, t)
                    self.info_text.set('Added: "{}", {} ({}) -- {}'.format(t.get_name(), self.currency(t.get_amount()), t.get_typestr(),
                                                                           self.convert_date_str(t.get_date()) + ' (' + self.weekday_name(t.get_date().weekday()) + ')'))
                    self.changed = True
            else:
                #delete entries
                self.e_amount.delete(0, 'end')
                self.e_name.delete(0, 'end')
                self.e_type.delete(0, 'end')
                self.info_text.set('Invalid entry...')
        self.e_amount.focus_set()
                             
    def t_to_screen(self, parent, t, index='end'):
        #puts a transaction to screen in ordinary format
        str_amount = self.currency(t.get_amount())
        date_str = self.convert_date_str(t.get_date()) + ' (' + self.weekday_name(t.get_date().weekday()) + ')'
        i = self.treeview.insert(parent, index, values=[str_amount, t.get_name(), t.get_typestr(), date_str], tags=['font'])
        return i

    def t_to_screen_newperiod(self, t, index='end'):
        #index is index of the period item, not the transaction
        if self.period == 0:
            i = self.t_to_screen('' , t, index=index)
            return None, i
        elif self.period == 1:
            dict_ = {0:[0, 6], 1:[1, 5], 2:[2, 4], 3:[3, 3], 4:[4, 2], 5:[5, 1], 6:[6, 0]}
            #iid is the date of the monday in the week (eg. 20/4/2016)
            i = self.treeview.insert('', index, iid=self.convert_date_str(t.get_date() - dt.timedelta(days=dict_[t.get_date().weekday()][0])), tags=['font2'],
                                     values=['Week:', self.convert_date_str(t.get_date() - dt.timedelta(days=dict_[t.get_date().weekday()][0]))
                                             + '-' + self.convert_date_str(t.get_date() + dt.timedelta(days=dict_[t.get_date().weekday()][1]))])
            i2 = self.t_to_screen(i, t, index='end')
            return i, i2
        elif self.period == 2:
            #iid is the month and year (eg. 2,2015)
            i = self.treeview.insert('', index, iid=str(t.get_date().month) + ',' + str(t.get_date().year), tags=['font2'],
                                     values=['Month:', self.month_name(t.get_date().month, option='full') + ' ' + str(t.get_date().year)])
            i2 = self.t_to_screen(i, t, index='end')
            return i, i2
        elif self.period == 3:
            dict_ = {1:[1, 2, 3], 2:[4, 5, 6], 3:[7, 8, 9], 4:[10, 11, 12], None:[None]}
            quarter, year = math.ceil(t.get_date().month / 3), t.get_date().year
            #iid is the quarter and year (eg. 4,2017)
            i = self.treeview.insert('', index, iid=str(quarter) + ',' + str(year), values=['Months:', self.month_name(dict_[quarter][0], option='full') + ' - ' +
                                                       self.month_name(dict_[quarter][2]) + ' ' + str(year)], tags=['font2'])
            i2 = self.t_to_screen(i, t, index='end')
            return i, i2
        
    def select_line(self, treeview, item):
        treeview.selection_set(item)
        #treeview.yview('moveto', 0)
        self.update_idletasks()
        treeview.see(item)

    def delete_last(self):
        if len(self.treeview.get_children()) == 0:
            self.info_text.set('Nothing to delete...')
        else:
            t = self.transactions.pop()
            if self.period == 0:
                to_delete = self.treeview.get_children()[-1]
                amount = self.treeview.set(to_delete, column=1)
                name = self.treeview.set(to_delete, column=2)
                type_ = self.treeview.set(to_delete, column=3)
                date = self.treeview.set(to_delete, column=4)
                self.treeview.delete(to_delete)
                if len(self.treeview.get_children()) > 0:
                    self.select_line(self.treeview, self.treeview.get_children()[-1])
                self.info_text.set('Removed: \"{}\", {} ({}) -- {}'.format(name, amount ,type_, date))
            
            if self.period in [1, 2, 3]:
                to_delete = self.treeview.get_children(self.treeview.get_children()[-1])[-1]
                amount = self.treeview.set(to_delete, column=1)
                name = self.treeview.set(to_delete, column=2)
                type_ = self.treeview.set(to_delete, column=3)
                date = self.treeview.set(to_delete, column=4)
                self.treeview.delete(to_delete)
                self.info_text.set('Removed: \"{}\", {} ({}) -- {}'.format(name, amount ,type_, date))
                if len(self.treeview.get_children(self.treeview.get_children()[-1])) > 0:
                    self.select_line(self.treeview, self.treeview.get_children(self.treeview.get_children()[-1])[-1])
                elif len(self.treeview.get_children(self.treeview.get_children()[-1])) == 0:
                    self.treeview.delete(self.treeview.get_children()[-1])
                    if len(self.treeview.get_children()) > 0:
                        self.select_line(self.treeview, self.treeview.get_children(self.treeview.get_children()[-1])[-1])
                else:
                    print('Strange error (delete_last)')
            
            self.refresh_analysis(self.analysis, t)
            self.changed = True
                
    def show_hide_all(self):
        if self.period in [1, 2, 3] and len(self.treeview.get_children()) > 0:
            show = False
            for child in self.treeview.get_children():
                if self.treeview.item(child, option='open') == False:
                    show = True
            if show == True:
                for child in self.treeview.get_children():
                    self.treeview.item(child, open=True)
                self.treeview.yview('moveto', 0)
                self.select_line(self.treeview, self.treeview.get_children(self.treeview.get_children()[-1])[-1])
            else:
                for child in self.treeview.get_children():
                    self.treeview.item(child, open=False)
                self.treeview.yview('moveto', 0)
                self.treeview.selection_remove(self.treeview.selection())
                self.update_idletasks()
                self.treeview.see(self.treeview.get_children()[-1])
        
    '''MENU COMMANDS ----------------------------------------------------------'''
    def open_file(self):
        print('Open file')
    def save_file(self):
        if self.filename != None:
            to_write = '[PACX save file]\n'
            for t in self.transactions:
                to_write += self.parse_transaction(t)
            self.file = open(self.filename, 'w')
            self.file.write(to_write)
            self.file.close()
            self.file = None
            self.info_text.set('Saved')
            self.changed = False
        else:
            print('Save file (save as)')
        
    def save_as_file(self):
        print('Save as file')

    def show_about_top(self):
        top = tk.Toplevel()
        top.title('About')
        top.geometry('210x70')

        text = tk.Message(top, text='Made by Boren Xue')
        text.pack()

        button = tk.Button(top, text='Close', command=top.destroy)
        button.pack()

    '''SHORTCUT KEYS -----------------------------------------------------------------------------------------------'''
    def create_shortcut_keys(self):
        #save
        self.bind('<Control-KeyPress-s>', self.shortcut_save)

    def shortcut_save(self, event):
        self.file_menu.invoke(2)
                         
    '''FUNCTIONS THAT ARE EXECUTED RIGHT AFTER MAINLOOP EXECUTES =================================================='''
    def after_func(self):
        pass
        
    '''USEFUL CONVERSIONS ==========================================================================================='''
    def weekday_name(self, num, option='short'):
        dict1 = {0:'Mon', 1:'Tue', 2:'Wed', 3:'Thu', 4:'Fri', 5:'Sat', 6:'Sun'}
        dict2 = {0:'Monday', 1:'Tuesday', 2:'Wednesday', 3:'Thursday', 4:'Friday', 5:'Saturday', 6:'Sunday'}
        if option == 'short':
            return dict1[num]
        if option == 'full':
            return dict2[num]
        else:
            raise ValueError('Wrong option (short or full)')
        
    def month_name(self, num, option='short'):
        dict1 = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
        dict2 = {1:'January', 2:'Febuary', 3:'March', 4:'April', 5:'May', 6:'June', 7:'July', 8:'August', 9:'September',
                 10:'October', 11:'November', 12:'December'}
        if option == 'short':
            return dict1[num]
        if option == 'full':
            return dict2[num]
        else:
            raise ValueError('Wrong option (short or full)')
        
    def convert_date_str(self, date):
        #date is a datetime.date object or string
        if isinstance(date, dt.date):
            str_ = str(date)[8:] + '/' + str(date)[5:7] + '/' + str(date)[:4]
            return str_
        elif isinstance(date, str):
            temp = date
            day = int(temp[:temp.index('/')])
            temp = temp[temp.index('/') + 1:]
            month = int(temp[:temp.index('/')])
            if temp.find(' (') == -1:
                year = int(temp[temp.index('/') + 1:])
            else:
                year = int(temp[temp.index('/') + 1:temp.index(' (')])
            d = dt.date(year, month, day)
            return d
        else:
            raise TypeError('Wrong type! (convert_date_str)')

    def currency(self, number):
        if isinstance(number, (float, int)):
            return locale.currency(number, symbol=False, grouping=True, international=False)
        elif isinstance(number, str):
            return locale.currency(float(number), symbol=False, grouping=True, international=False)
        else:
            raise TypeError('Wrong type (currency)')
    
    def parse_txt_file(self, string):
        if string[:3] == 't//':
            string = string[3:]
            amount = float(string[:string.index(',,,')])
            string = string[string.index(',,,') + 3:]
            name = string[:string.index(',,,')]
            string = string[string.index(',,,') + 3:]
            type_ = int(string[:string.index(',,,')])
            string = string[string.index(',,,') + 3:]

            year = int(str(string[:string.index('-')]))
            string = string[string.index('-') + 1:]
            month = int(str(string[:string.index('-')]))
            string = string[string.index('-') + 1:]
            day = int(string)
            date = dt.date(year, month, day)
            
            return(transaction.Transaction(amount, name, type_, date))
        else:
            raise TypeError('Line in txt file is not a transaction object')

    def parse_transaction(self, t):
        amount = str(t.get_amount())
        name = t.get_name()
        type_ = str(t.get_type())
        date = str(t.get_date())
        string = 't//{},,,{},,,{},,,{}\n'.format(amount, name, type_, date)
        return string

def main():
    filename = 'Boren Personal.txt'
    app = App(filename=filename)
    app.mainloop()
    
    #make default file

main()
