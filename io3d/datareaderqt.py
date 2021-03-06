#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © %YEAR%  <>
#
# Distributed under terms of the %LICENSE% license.

"""

"""

import logging

logger = logging.getLogger(__name__)
import argparse

from PyQt4.QtGui import QGridLayout, QLabel,\
    QPushButton, QLineEdit, QApplication
from PyQt4 import QtGui
import sys
import os.path
import copy


from . import datareader
from . import cachefile as cachef


class DataReaderWidget(QtGui.QWidget):

    def __init__(
            self,
            datapath=None,
            loadfiledir='',
            loaddir='',
            show_message_function=None,
            after_function=None,
            before_function=None,
            cachefile=None

    ) :
        """

        :param datapath: is also output var. Describes path to selected data
        :param loadfiledir: init dir fo file dialog
        :param loaddir: init dir for dir dialog
        :param show_message_function:
        :param after_function:
        :param before_function:
        :param cachefile:
        """
        super(DataReaderWidget, self).__init__()

        # status function can be used to proceed messages out of this module
        # it is defined fcn(str)
        self.show_message_function = show_message_function
        self.loadfiledir = loadfiledir
        self.loaddir = loaddir
        self.datapath = datapath
        self.after_function = after_function
        self.before_function = before_function
        self.cachefile = cachefile
        if self.cachefile is not None:
            self.cache = cachef.CacheFile(self.cachefile)
        else:
            self.cache = None

        self.datap = None

        self.init_ui()

    def init_ui(self):
        self.mainLayout = QGridLayout(self)
        # self.mainLayout.addWidget(QLabel("Key"), 0, 1)
        # self.mainLayout.addWidget(QLabel("Value"), 0, 2)
        btn_load_file = QPushButton("Load file", self)
        btn_load_file.clicked.connect(self.read_data_file_dialog)
        self.mainLayout.addWidget(btn_load_file, 0, 0)

        btn_load_file = QPushButton("Load dir", self)
        btn_load_file.clicked.connect(self.read_data_dir_dialog)
        self.mainLayout.addWidget(btn_load_file, 0, 1)

        self.text_dcm_dir = QLabel('data path:')
        self.text_dcm_data = QLabel('data description:')
        self.mainLayout.addWidget(self.text_dcm_dir, 1, 0, 1, 2)
        self.mainLayout.addWidget(self.text_dcm_data, 2, 0, 1, 2)

    def __get_datafile(self, app=False):
        """
        Draw a dialog for directory selection.
        """

        if self.cache is not None:
            self.loadfiledir = self.cache.get_or_none('loadfiledir')

        if self.loadfiledir is None:
            self.loadfiledir = ''
        directory=self.loadfiledir
        from PyQt4.QtGui import QFileDialog
        if app:
            dcmdir = QFileDialog.getOpenFileName(
                caption='Select Data File',
                directory=directory
                # ptions=QFileDialog.ShowDirsOnly,
            )
        else:
            app = QApplication(sys.argv)
            dcmdir = QFileDialog.getOpenFileName(
                caption='Select DICOM Folder',
                # ptions=QFileDialog.ShowDirsOnly,
                directory=directory
            )
            # pp.exec_()
            app.exit(0)
        if len(dcmdir) > 0:

            dcmdir = "%s" % (dcmdir)
            dcmdir = dcmdir.encode("utf8")
        else:
            dcmdir = None


        head, teil = os.path.split(dcmdir)
        if self.cache is not None:
            self.cache.update('loadfiledir', head)
        return dcmdir

    def __get_datadir(self, app=False):
        """
        Draw a dialog for directory selection.
        """
        # if 'datadir' in self.oseg.cache.data.keys():
        # if :
        #     directory = self.oseg.input_datapath_start
        if self.cache is not None:
            self.loaddir = self.cache.get_or_none('loaddir')

        if self.loaddir is None:
            self.loaddir = ''

        directory = self.loaddir

        from PyQt4.QtGui import QFileDialog
        if app:
            dcmdir = QFileDialog.getExistingDirectory(
                caption='Select DICOM Folder',
                options=QFileDialog.ShowDirsOnly,
                directory=directory
            )
        else:
            app = QApplication(sys.argv)
            dcmdir = QFileDialog.getExistingDirectory(
                caption='Select DICOM Folder',
                options=QFileDialog.ShowDirsOnly,
                directory=directory
            )
            # pp.exec_()
            app.exit(0)
        if len(dcmdir) > 0:

            dcmdir = "%s" % (dcmdir)
            dcmdir = dcmdir.encode("utf8")
        else:
            dcmdir = None

        if self.cache is not None:
            self.cache.update('loaddir', dcmdir)
        return dcmdir

    def read_data_file_dialog(self):


        self.__show_message('Reading data file...')
        QApplication.processEvents()

        if self.before_function is not None:
            self.before_function(self)

        self.datapath = self.__get_datafile(
            app=True,
            )

        if self.datapath is None:
            self.__show_message('No data path specified!')
            return
        head, teil = os.path.split(self.datapath)
        self.loadfiledir = head

        self.read_data_from_prepared_datapath()

    def read_data_dir_dialog(self):
        self.__show_message('Reading data file...')
        QApplication.processEvents()

        if self.before_function is not None:
            self.before_function(self)

        self.datapath = self.__get_datadir(
            app=True
        )

        if self.datapath is None:
            self.__show_message('No DICOM directory specified!')
            return
        # head, teil = os.path.split(oseg.datapath)
        self.loaddir = copy.copy(self.datapath)

        self.read_data_from_prepared_datapath()

        # print("Transferred: {0}\tOut of: {1}".format(transferred, toBeTransferred))

    def read_data_from_prepared_datapath(self):
        """
        Function is called in the end of process
        :return:
        """

        reader = datareader.DataReader()

        self.datap = reader.Get3DData(self.datapath, dataplus_format=True)

        _set_label_text(self.text_dcm_dir, _make_text_short(self.datapath), self.datapath)
        _set_label_text(self.text_dcm_data, self.get_data_info())
        if self.after_function is not None:
            self.after_function(self)
        self.__show_message('Data read finished')

    def get_data_info(self):
        vx_size = self.datap['voxelsize_mm']
        vsize = tuple([float(ii) for ii in vx_size])
        ret = ' %dx%dx%d,  %fx%fx%f mm' % (self.datap['data3d'].shape + vsize)

        return ret

    def __show_message(self, msg):
        logger.debug(msg)

        if self.show_message_function is not None:
            self.show_message_function(msg)


def _make_text_short(text, max_lenght=40):
    return text[:int(max_lenght/2)] + ".." + text[-int(max_lenght/2):]


def _set_label_text(obj, text, tooltip=None):
    dlab = str(obj.text())
    obj.setText(dlab[:dlab.find(':')] + ': %s' % text)
    if tooltip is not None:
        obj.setToolTip(tooltip)


def my_before_fcn(arg):
    arg.loadfiledir = os.path.expanduser("~")


def my_after_fcn(arg):
    print(arg)
    print(arg.loaddir)
    print(arg.loadfiledir)

def main():
    logger = logging.getLogger()

    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    logger.addHandler(ch)

    # create file handler which logs even debug messages
    # fh = logging.FileHandler('log.txt')
    # fh.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(
    #     '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # fh.setFormatter(formatter)
    # logger.addHandler(fh)
    # logger.debug('start')

    # input parser
    parser = argparse.ArgumentParser(
        description=__doc__
    )
    # parser.add_argument(
    #     '-i', '--inputfile',
    #     default=None,
    #     required=True,
    #     help='input file'
    # )
    parser.add_argument(
        '-ld', '--loaddir',
        default="",
        # required=True,
        help='init dir for dir dialog'
    )
    parser.add_argument(
        '-lf', '--loadfiledir',
        default="",
        # required=True,
        help='init dir for file dialog'
    )
    parser.add_argument(
        '-d', '--debug', action='store_true',
        help='Debug mode')
    parser.add_argument(
        '-cf', '--cachefile',
        default=None,
        # required=True,
        help='cache file for last load dir path info'
    )
    args = parser.parse_args()

    if args.debug:
        ch.setLevel(logging.DEBUG)

    app = QtGui.QApplication(sys.argv)

    # w = QtGui.QWidget()
    # w = DictEdit(dictionary={'jatra':2, 'ledviny':7})
    w = DataReaderWidget(loaddir=args.loaddir, loadfiledir=args.loadfiledir,
                         cachefile=args.cachefile,
                             after_function=my_after_fcn, before_function=my_before_fcn)
    w.resize(250, 150)
    w.move(300, 300)
    w.setWindowTitle('io3dQtWidget')
    w.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
