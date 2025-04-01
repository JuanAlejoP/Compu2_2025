import argparse

def main():
    parser = argparse.ArgumentParser(description='Procesa archivos de entrada y salida.')
    parser.add_argument('-i', '--input', required=True, help='Nombre del archivo de entrada')
    parser.add_argument('-o', '--output', required=True, help='Nombre del archivo de salida')
    
    args = parser.parse_args()
    
    print('Archivo de entrada:', args.input)
    print('Archivo de salida:', args.output)

if __name__ == '__main__':
    main()