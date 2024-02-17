# aidl-visualizer
Tool to generate a visualization of AOSP AIDL binder connections
The intended audience for this tool is developers that develop in AOSP
i.e. making Android devices.

Make sure [Graphviz](https://graphviz.org) is installed and that the 'dot' tool is in the path

## Instructions:

adb root

adb shell ps -ef > my_inputfile.txt

adb shell /system/bin/dumpsys --pid --clients > my_inputfile.txt

./aidlizer.py -i my_inputfile.txt -o outputfile


Open outputfile.svg in your web browser or other tool


