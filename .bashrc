function python3 {
    if [ -z $1 ]; then
        echo "usage: python3 [option] ... [-c cmd | -m mod | file | -] [arg] ..."
        echo "Try \`python -h' for more information."
    elif [ -f $1 ]; then
        echo '  File "'$1'", line 1'
        echo "    `head -1 $1`"
        echo "    ^"
        echo "SyntaxError: invalid syntax"
    else
        echo -n "python3: can't open file '"$1"': "
        echo "[Errno 2] No such file or directory"
    fi
}
export -f python3
