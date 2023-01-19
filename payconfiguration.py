
import os
import sys
def main():
    print(os.name)
MACHINE_IP=''
WORK_DIR=''
API_TOKEN = ''
if os.uname()[0] == 'Linux' :
    WORK_DIR='/home/pi/sch/schWeb/flasky2'    
    MACHINE_IP='raspi2.local'
    
else:
    WORK_DIR='/Users/alexfu/myPython/ebook-flask/schWeb/flasky2'
    MACHINE_IP='192.168.50.75'
    
if __name__ == '__main__':
    main()
