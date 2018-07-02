#!/usr/bin/python3

import wx
import subprocess
import time
import os


class WiFiGUI(wx.Frame):

    def __init__(self, *args, **kw):
        super(WiFiGUI, self).__init__(*args, **kw)

        self.init_UI()

    def init_UI(self):

        panel = wx.Panel(self)
        self.Bind(wx.EVT_CLOSE, self.on_close_window)

        self.usrp_control_args = ["gnome-terminal", "-x", "python3", "fake_USRP_control.py"]
        self.matlab_converter_args = ["gnome-terminal", "-x", "python3", "fake_matlab_converter.py"]
        self.matlab_plotter_args = ["gnome-terminal", "-x", "python3", "fake_matlab_plotter.py"]

        usrp_control_button = wx.Button(panel, label="Run USRP controller", pos=(20, 20))
        usrp_control_button.Bind(wx.EVT_BUTTON, self.on_usrp)
        matlab_extract_button = wx.Button(panel, label="Extract .mat file", pos=(20, 60))
        matlab_extract_button.Bind(wx.EVT_BUTTON, self.on_extract)
        matlab_plot_button = wx.Button(panel, label="Plot results", pos=(20, 100))
        matlab_plot_button.Bind(wx.EVT_BUTTON, self.on_plot)
        control_all_button = wx.Button(panel, label="Run all commands", pos=(20, 140))
        control_all_button.Bind(wx.EVT_BUTTON, self.on_run_all_pressed)

        self.SetSize((600, 400))
        self.SetTitle("SYSC WiFi Control Panel")
        self.Centre()

    def on_usrp(self, e):
        print("USRP button pressed\n")
        proc = subprocess.Popen(self.usrp_control_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None, shell=False)
        proc.wait()

        return


    def on_extract(self, e):
        print("Matlab extract button pressed\n")
        proc = subprocess.Popen(self.matlab_converter_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None, shell=False)
        proc.wait()

        return

    def on_plot(self, e):
        print("Plot button pressed\n")
        proc = subprocess.Popen(self.matlab_plotter_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None, shell=False)
        proc.wait()

        return

    def on_run_all_pressed(self, e):
        print("Run all button pressed\n")

        #os.system("")
        proc_1 = subprocess.Popen(self.usrp_control_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None, shell=False)
        proc_1.wait()
        proc_2 = subprocess.Popen(self.matlab_converter_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None, shell=False)
        proc_2.wait()
        proc_3 = subprocess.Popen(self.matlab_plotter_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None, shell=False)
        proc_3.wait()

        return


    def on_close_window(self, e):

        dial = wx.MessageDialog(None, 'Are you sure to quit?', 'Question',
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

        ret = dial.ShowModal()

        if ret == wx.ID_YES:
            self.Destroy()
        else:
            e.Veto()


def main():

    app = wx.App()
    gui = WiFiGUI(None)
    gui.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
