PING localhost -n 4 >NUL
echo %1
echo %2
echo %3
cd %2
%3 x %1
./webcontrol