# devops-test-task

Результат выполнения тестового задания на вакансию
"Инженер-программист в отдел тестирования / SDET / DevOps for Testing Department"

Результатом является скрипт devops-test-task.py

Скрипт выполнен на Python с учетом различий между версиями Python 2.7 и 3.4, поэтому
он одинаково выполняется интерпретаторами обеих этих версий.

Виртуальная машина с VirtualBox Ubuntu 14.04 amd64 получена выполнением в shell команд:

`vagrant box add ubuntu/trusty64`
`mkdir -p ~/vagrant/DevopsTestUbuntu1404amd64`
`cd ~/vagrant/DevopsTestUbuntu1404amd64`
`mv Vagrantfile Vagrantfile.old`
`cat Vagrantfile.old|sed '/config\.vm\.box\ \=/ a\config.vm.define "DevopsTestUbuntu1404amd64" do |t|\nend' > Vagrantfile`
`vagrant init ubuntu/trusty64`

В git-репозиторий github.com/cpjs0000/devoptest.git загружено содержимое архива test_SDET_DevOps.zip

Доступ в git-репозиторий осуществляется по протоколу HTTPS. 
Для доступа по SSH потребуется загрузить свой ключ RSA для текущего пользователя на сервер git.

Скрипт запускается командой:
`./devops-test-task.py -u <URL git-репозитория> -m <имя виртуальной машины> -d <путь к директории для сохранения отчета> -b <ветка git-репозитория>`

Если хочется видеть вывод лога в текущую консоль, можно добавить опцию -v.
