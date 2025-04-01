import os
import time

NUM_PROCESOS = 3

def hijo():
    print(f'Hijo PID {os.getpid()} iniciado.')
    time.sleep(3)
    print(f'Hijo PID {os.getpid()} terminado.')
    os._exit(0)

def main():
    hijos = []
    
    for _ in range(NUM_PROCESOS):
        pid = os.fork()
        if pid == 0:
            hijo()
        else:
            hijos.append(pid)

    for pid in hijos:
        os.waitpid(pid, 0)

    print('Todos los hijos han terminado.')

if __name__ == '__main__':
    main()