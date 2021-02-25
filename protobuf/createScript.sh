!/bin/bash
python3 -m grpc_tools.protoc  \
        -I ./protos \
        --python_out=./unary \
        --grpc_python_out=./unary \
        ./protos/unary.proto

for entry in "."/*
do 
        echo "$entry"
        if ["$entry"="./unary"]
        then
                echo HI
        fi
done

