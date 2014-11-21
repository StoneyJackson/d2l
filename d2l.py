#   d2l - A library for working with Desire2Learn
#   Copyright (C) 2014  Stoney Jackson <dr.stoney@gmail.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.


import shutil
import pathlib
import datetime
import unzipr


def prep(zipFile):
    extractDirectory = unzipr.unzipFile(zipFile)
    extractDirectory = Directory(extractDirectory)
    extractDirectory.deleteAllButLastSubmissions()
    extractDirectory.renameSubmissions()
    extractDirectory = str(extractDirectory)
    unzipr.unzipFilesInDirectoryRecursively(extractDirectory)
    unzipr.deleteZipFilesFromDirectoryRecursively(extractDirectory)


class Directory:
    def __init__(self, directory):
        self.directory = pathlib.Path(directory)

    def renameSubmissions(self):
        files = self._getFiles()
        for f in files:
            parts = f.studentName.split()
            last = parts[-1]
            first = '-'.join(parts[:-1])
            name = last + '_' + first
            name += ''.join(f.namePath.suffixes)
            pathlib.Path(str(f)).rename(self.directory/name)

    def deleteAllButLastSubmissions(self):
        files = self._getFiles()
        self._sortFilesByDateTime(files)
        files.reverse()
        seen = set()
        for f in files:
            if f.studentId not in seen:
                seen.add(f.studentId)
            else:
                (self.directory / f.namePath).unlink()

    def _getFiles(self):
        files = [File(f) for f in self.directory.iterdir() if File.isFile(f)]
        return files

    def _sortFilesByDateTime(self, fileList):
        fileList.sort(key=File.getDateTime)

    def __repr__(self):
        return str(self.directory)


class File:
    '''
    A Desire2Learn file's name has the following structure:

        studentId-courseId - studentFullName - dateTimeSubmitted - fileName
    '''
        
    @staticmethod
    def isFile(path):
        return str(path).count(' - ') == 3

    def __init__(self, file):
        self.fullPath = pathlib.Path(file)
        self.namePath = pathlib.Path(self.fullPath.name)
        parts = str(self.namePath).split(' - ')
        self.studentId, self.postid = parts[0].split('-')
        self.studentName = parts[1]
        (mon, day, year, hm, ampm) = [p.strip(',') for p in parts[2].split()]
        minutes = hm[-2:]
        hours = hm[:-2]
        hours = hours.zfill(2)
        self.datetime = ' '.join([mon, day, year, hours, minutes, ampm])
        self.studentFilename = parts[3]

    def getDateTime(self):
        return datetime.datetime.strptime(self.datetime, '%b %d %Y %I %M %p')

    def __repr__(self):
        return str(self.fullPath)


import sys
prep(sys.argv[1])
