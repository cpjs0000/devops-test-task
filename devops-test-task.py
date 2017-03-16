#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""для унификации между версиями Python 2 и 3 используем print из Python 3"""
from __future__ import print_function

import sys, syslog, optparse, os, errno

from subprocess import Popen, PIPE

"""Включаем запись в syslog"""
syslog.openlog(ident="DevOps Test Task",logoption=syslog.LOG_PID, facility=syslog.LOG_LOCAL0)

"""создаем парсер параметров"""
parser = optparse.OptionParser(usage="%prog <-u --git-url> [-b --git-branch] <-m --vm-name> <-d --target-dir>")

"""Согласно заданию, скрипт принимает следующие параметры:
1) Адрес git репозитория;"""
parser.add_option('-u', '--git-url',
    action="store", dest="git_url",
    help="URL of git repository", default="")

"""2) Имя ветки (по умолчанию - master);"""
parser.add_option('-b', '--git-branch',
    action="store", dest="git_branch",
    help="branch in git repository", default="master")

"""3) Имя виртуальной машины, в которой требуется запустить тест;
Если имя машины содержит пробелы, его следует заключить в апострофы или кавычки"""
parser.add_option('-m', '--vm-name',
    action="store", dest="vm_name",
    help="name of virtual machine", default="")

"""4) Директория, куда сохранять отчет теста."""
parser.add_option('-d', '--target-dir',
    action="store", dest="target_dir",
    help="name of target directory for report", default="")

"""Для отладочных целей скрипт также может выводить лог в stdout"""
parser.add_option('-v', '--verbose',
    action="store_true", dest="verbose",
    help="logging to stdout", default="False")
    
"""получение парсером параметров"""
options, args  = parser.parse_args()

"""функция вывода сообщений в лог, для краткости"""
def mylog(s):
    if options.verbose==True:
      print(s)
    syslog.syslog(s)

mylog("DevOps Test Task started")
mylog("Detected Python " + sys.version.split("\n")[0])

"""вывод параметров в лог"""
for option,value in options.__dict__.items():
    par=option+'='+str(value)
    mylog(par)

"""проверка указания обязательных параметров"""
if not options.git_url:
    mylog("not enough parameteres (git URL)")
    parser.error("git URL is required")
    
if not options.vm_name :
    mylog("not enough parameteres (virtual machine name)")
    parser.error("name of virtual machine is required")
    
if not options.target_dir:
    mylog("not enough parameteres (target directory)")
    parser.error("target dir for saving report is required")

"""весь ненужный вывод результатов выполнения команд будет отправлен сюда"""
FNULL=open(os.devnull,'w')

"""ищем указанную в параметре виртуальную машину с помощью Vagrant"""
for v_global in Popen("vagrant global-status", shell=True, stdin=PIPE, stdout=PIPE).stdout.read().decode('utf8').split("\n"):
    if options.vm_name in v_global:
      v_path=v_global.split()[-1]
      v_id=v_global.split()[0:1]


"""включаем указанную в параметре виртуальную машину"""
v_state=Popen("vagrant status", shell=True, stdin=PIPE, stdout=PIPE, cwd=v_path).stdout.read().decode('utf8').split("\n")
for s in v_state:
    if options.vm_name in s:
      if "power" in s:
        if s.split()[-2]=="poweroff":
          mylog("VM is halted, taking power on")
          r=Popen("vagrant up", shell=True, stdin=PIPE, stdout=PIPE, cwd=v_path)
          output, error = r.communicate()
          if r.returncode == 0:
            mylog('VM powered on')
          else:
            assert r.returncode != 0
            mylog('error occurred: %r' % (error,))


"""получаем и пишем состояние виртуальной машины в лог"""
v_state=Popen("vagrant status", shell=True, stdin=PIPE, stdout=PIPE, cwd=v_path).stdout.read().decode('utf8').split("\n")
for s in v_state:
    if options.vm_name in s:
      n="virtual machine [" + options.vm_name + "] state: " + s.split()[-2]
      mylog(n)

"""делаем снэпшот состояния виртуальной машины"""
mylog ("Saving state of VM...",)
r=Popen("vagrant snapshot push", shell=True, stdin=PIPE, stdout=PIPE, cwd=v_path)
output, error = r.communicate()
if r.returncode == 0:
   mylog('State of VM saved succesfully')
else:
   assert r.returncode != 0
   mylog('error occurred: %r' % (error,))


"""клонируем директорию с файлами теста из репозитория в директорию Vagrant соответствующей виртуальной машины,
эта директория будет доступна внутри виртуальной машины в директории /vagrant"""
mylog ("Cloning test task from git repository...")
r=Popen("cd " + '"' + v_path + '"; rm -fr devoptest; git clone -q -b ' + options.git_branch + ' ' + options.git_url, shell=True, stdin=PIPE, stdout=PIPE, stderr=FNULL)
output, error = r.communicate()
if r.returncode == 0:
   mylog('Test task succesfully cloned')
else:
   assert r.returncode != 0
   mylog('error occurred: %r' % (error,))

"""тест требует python-pip и python-virtualenv, однако в box ubuntu/trusty64 их нет по умолчанию, поэтому устанавливаем"""
mylog("Installing test task dependencies...")
r=Popen("vagrant ssh -c 'sudo apt-get -qq -y install python-{pip,virtualenv}'", shell=True, stdin=PIPE, stdout=PIPE,stderr=FNULL, cwd=v_path)
output, error = r.communicate()
if r.returncode == 0:
   mylog('Task dependencies are installed succesfully')
else:
   assert r.returncode != 0
   mylog('error occurred: %r' % (error,))

"""если директории для сохранения отчета теста нет, создаем её"""
mylog("Creating target directory...")
try:
    os.makedirs(options.target_dir, mode=0o777) 
    mylog ('Target directory created (new)')
except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(options.target_dir):
          mylog( 'Target directory already exists')
          pass
        else:
          raise

"""запускаем тест"""
mylog("Executing test task...")
r=Popen("vagrant ssh -c 'cd /vagrant/devoptest;./run_test.sh'", shell=True, stdin=PIPE, stdout=PIPE, cwd=v_path)
output, error = r.communicate()
if r.returncode == 0:
   mylog('Test task succesfully completed')
else:
   assert r.returncode != 0
   mylog('error occurred: %r' % (error,))

"""копируем отчет теста в указанную в параметрах директорию на хостовой машине"""
mylog ("Copying report.xml to target dir, removing test directory...")
r=Popen("cp devoptest/report.xml "+ options.target_dir + "; rm -fr devoptest", shell=True, stdin=PIPE, stdout=PIPE, cwd=v_path)
output, error = r.communicate()
if r.returncode == 0:
   mylog('Report file succesfully placed to target directory')
else:
   assert r.returncode != 0
   mylog('error occurred: %r' % (error,))

"""восстанавливаем состояние виртуальной машины из снэпшота"""
mylog ("Restoring state of VM...",)
r=Popen("vagrant snapshot pop", shell=True, stdin=PIPE, stdout=PIPE, cwd=v_path)
output, error = r.communicate()
if r.returncode == 0:
   mylog('State of VM successfully restored')
else:
   assert r.returncode != 0
   mylog('error occurred: %r' % (error,))

"""выключаем виртуальную машину"""
mylog ("Halting VM...",)
r=Popen("vagrant halt", shell=True, stdin=PIPE, stdout=PIPE, cwd=v_path)
output, error = r.communicate()
if r.returncode == 0:
   mylog('VM successfully halted')
else:
   assert r.returncode != 0
   mylog('error occurred: %r' % (error,))
   

mylog("DevOps Test Task completed")
