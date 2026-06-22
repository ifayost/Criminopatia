#!/bin/sh
CMD="python criminopatia.py"

[ "$RUN_EPISODES" = "true" ] && CMD="$CMD --episodes"
[ "$RUN_CF" = "true" ] && CMD="$CMD --cf"
[ "$RUN_ARCHIVO" = "true" ] && CMD="$CMD --archivo"

# If no flags set, show help
if [ "$CMD" = "python criminopatia.py" ]; then
    CMD="$CMD --help"
fi

exec $CMD
