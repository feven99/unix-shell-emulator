# Test every supported command, including errors
pwd
who
ls /
cd /home/student
ls
md5 hello.txt
cp hello.txt /tmp/copied.txt
ls /tmp
md5 /tmp/copied.txt
cp /tmp/copied.txt /tmp/other.txt
md5 /tmp/other.txt
cp missing.txt /tmp/failed.txt
md5 /tmp
notacommand
cd /etc
ls
exit
