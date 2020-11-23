#!/usr/bin/env bash

function help(){
    echo "命令格式："
    echo "  server.sh start --port|-p [默认8080] --worker|-w [默认3] --gpu [0|1] --mode|-m [tfserving|single]"
    echo "  server.sh stop"
    echo "  例：bin/server.sh start -p 8080 -w 1 -g 3 -m single"
    exit
}


worker=1

echo "生成样本需要的进程数："  $worker

read -r -p "是否确认? 如果需要修改请选n。 [y/n] " input

case $input in
    [yY][eE][sS]|[yY])
		echo "Yes"
		;;

    [nN][oO]|[nN])
      echo "No"
      read -r -p "输入进程数：" worker

      ;;
    *)
		echo "Invalid input..."
		exit 1
		;;
esac

set -x

python -m generate -w $worker