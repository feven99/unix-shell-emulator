# Stage 5: all commands, VFS errors, copying and removing empty directories
pwd
who
ls /
cd /home/student
ls
md5 hello.txt
cp hello.txt /tmp/copied.txt
ls /tmp
md5 /tmp/copied.txt
rmdir /tmp
# A nonempty directory cannot be removed
cd /
rmdir /home
rmdir /missing
rmdir /home/student/hello.txt
ls /tmp
# Empty the /tmp directory is impossible without file deletion, so test rmdir /tmp via a separate script.
exit
