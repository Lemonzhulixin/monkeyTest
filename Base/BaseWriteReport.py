import os
import xlsxwriter
from Base import BaseReport
import time


PATH = lambda p: os.path.abspath(
    os.path.join(os.path.dirname(__file__), p)
)


def report(info):
    #run_time = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    #workbook = xlsxwriter.Workbook('report.' + run_time + '.xlsx')
    workbook = xlsxwriter.Workbook('performance_report.xlsx')
    bo = BaseReport.OperateReport(workbook)
    bo.monitor(info)
    bo.crash()
    bo.analysis(info)
    bo.close()