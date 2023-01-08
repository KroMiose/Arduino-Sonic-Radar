import serial 
import serial.tools.list_ports
from time import sleep, localtime, strftime
from tkinter import ARC, Tk, Canvas
import _thread


class BluetoothManager: # 蓝牙管理模块
    bps = 9600  # 通信波特率 标准值：50,75,110,134,150,200,300,600,1200,1800,2400,4800,9600,19200,38400,57600,115200
    timex = 2   # 超时设置  None：永远等待操作；
                    #         0：立即返回请求结果
                    #      其他：等待超时时间（单位为秒）
    portx = 'COM6'   # 端口
    ser = None

    def __init__(self):
        self.connect()

    # 连接端口
    def connect(self):
        if(self.ser):
            return True
        print('正在连接:', self.portx)
        try:
            self.ser = serial.Serial(self.portx, self.bps, timeout= self.timex)
            return True
        except Exception as e:
            print('ERROR!', e)
            return False

    # 发送数据
    def transmit(self, data):
        if not self.ser:    # 如果断链自动重连
            self.connect()
        if self.connect():
            result = self.ser.write(data.encode("gbk"))
            print('已发送:', data, '共计', result, '字节')
            return result

    # 读取数据
    def read(self):
        if not self.ser:    # 如果断链自动重连
            self.connect()
        if self.connect():
            result = self.ser.read() # 读一个字节字符
            return result

    # 关闭连接
    def close(self):
        self.ser.close()
        self.ser.close()

class Radar():  # 雷达模块
    scanrunning = True

    def __init__(self): # 初始化蓝牙连接模块
        port_list = list(serial.tools.list_ports.comports())
        if len(port_list) == 0:
            print("无可用串口！")
        else:   # 显示可用串口
            print('+ 当前可用串口:')
            for i in range(0, len(port_list)):
                print('  -', port_list[i])
        self.bt = BluetoothManager()
    
    def startScanning(self):
        global updateRay
        while self.scanrunning:
            recv = self.bt.read()
            if(recv == b'>'):   # 解析读取到的信息
                rot = self.bt.read()
                recv = self.bt.read()
                if(recv == b'-'):
                    dst = self.bt.read()
                    rot = int.from_bytes(rot, 'big')
                    dst = int.from_bytes(dst, 'big')
                    updateRay(rot, dst)
                    print('当前角度:', rot, '; 当前距离:', dst)


backGroundColor = 'black'   # 背景颜色
radarLimitLine = [0.2, 0.4, 0.6, 0.8]    # 雷达参考线
centerPos = (600, 550)  # 雷达中心点坐标 
radarRange = 500        # 雷达显示范围
window_width = 1220     # 窗口宽度
window_height = 610     # 窗口高度
maxRange = 70           # 最大探测距离
scanrunning = True      # 扫描开启

def updateRay(deg, det_dst):    # 更新射线
    det_dst = det_dst if det_dst < maxRange else maxRange
    show_dst = det_dst * (radarRange // maxRange)
    coord_base = (centerPos[0] - radarRange, centerPos[1] - radarRange, centerPos[0] + radarRange, centerPos[1] + radarRange)

    coord = (centerPos[0] - show_dst, centerPos[1] - show_dst, centerPos[0] + show_dst, centerPos[1] + show_dst)
    rc.create_arc(coord_base, start=deg - 1.2, extent= 2.4, width=2, fill='red')
    rc.create_arc(coord, start=deg - 1.3, extent= 2.6, outline=backGroundColor, width=1, fill=backGroundColor)

    for l in radarLimitLine:
        coord_line = (centerPos[0] - radarRange * l, centerPos[1] - radarRange * l, centerPos[0] + radarRange * l, centerPos[1] + radarRange * l)
        rc.create_arc(coord_line, start=0, extent=180, outline='green', width=1)

    rc.create_arc(coord_base, start=0, extent=180, outline='green', width=5)
    rc.create_arc(coord_base, start=45, extent=90, outline='green', width=1)
    rc.create_arc(coord_base, start=90, extent=45, outline='green', width=1)

def scanThread(threadName, delay):  # 扫描子线程
    print('线程起点:', threadName)
    radar = Radar()
    radar.startScanning()

windows = Tk()  # 创建窗口
rc = Canvas(windows, bg=backGroundColor, confine=False, height=window_height, width=window_width)   # 创建画板

if __name__ == '__main__':
    rc.pack()
    coord = (centerPos[0] - radarRange - 2, centerPos[1] - radarRange - 2, centerPos[0] + radarRange + 2, centerPos[1] + radarRange + 2)
    # rc.create_rectangle(coord, outline='green')
    rc.create_arc(coord, start=0, extent=180, outline='green', width=5)

    try:
        _thread.start_new_thread(scanThread, ('Thread-scan', 2))
    except Exception as e:
        print('扫描线程错误:', e)

    windows.mainloop()  # 主窗口循环

