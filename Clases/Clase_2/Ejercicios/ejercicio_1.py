import os
import time

def main():
    pid = os.fork()

    if pid == 0:
        print(f'Hijo: Mi PID es {os.getpid()}, mi padre es {os.getppid()}')
        time.sleep(60)
        print('Hijo: Terminando...')
        os._exit(0)
    else:
        print(f'Padre: Mi PID es {os.getpid()}, esperando al hijo...')
        os.wait()
        print('Padre: Mi hijo ha terminado.')

if __name__ == '__main__':
    main()
