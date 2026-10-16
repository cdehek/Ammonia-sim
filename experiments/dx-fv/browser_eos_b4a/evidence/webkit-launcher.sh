#!/bin/sh
WK_BUNDLE=/workspace/b4a-browsers/webkit-2336/minibrowser-wpe
export WEBKIT_EXEC_PATH="$WK_BUNDLE/bin"
export WEBKIT_INJECTED_BUNDLE_PATH="$WK_BUNDLE/lib"
export WEBKIT_INSPECTOR_RESOURCES_PATH="$WK_BUNDLE/share"
export LD_LIBRARY_PATH="/workspace/b4a-sysroot/usr/lib/x86_64-linux-gnu:$WK_BUNDLE/lib:$WK_BUNDLE/sys/lib"
exec "$WK_BUNDLE/bin/MiniBrowser" "$@"
