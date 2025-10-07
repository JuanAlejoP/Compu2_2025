import socket
import operator
import math

class CalculatorServer:
    def __init__(self, host='::1', port=8892):
        self.server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port, 0, 0))
        
        # Operadores permitidos y sus funciones correspondientes
        self.operators = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv,
            '^': operator.pow,
            'sqrt': math.sqrt
        }
    
    def evaluate(self, expression):
        try:
            # Manejo especial para raíz cuadrada
            if expression.startswith('sqrt '):
                num = float(expression[5:])
                if num < 0:
                    return "ERROR: Raíz cuadrada de número negativo"
                return f"RESULTADO: {self.operators['sqrt'](num)}"
            
            # Para otras operaciones
            parts = expression.split()
            if len(parts) != 3:
                return "ERROR: Formato inválido. Use: número operador número"
            
            num1 = float(parts[0])
            op = parts[1]
            num2 = float(parts[2])
            
            if op not in self.operators:
                return f"ERROR: Operador no soportado: {op}"
            
            if op == '/' and num2 == 0:
                return "ERROR: División por cero"
            
            result = self.operators[op](num1, num2)
            return f"RESULTADO: {result}"
            
        except ValueError:
            return "ERROR: Números inválidos"
        except Exception as e:
            return f"ERROR: {str(e)}"
    
    def start(self):
        self.server.listen(5)
        print(f"Calculadora escuchando en [{self.server.getsockname()[0]}]:{self.server.getsockname()[1]}")
        
        while True:
            client, address = self.server.accept()
            print(f"Nueva conexión de {address}")
            
            try:
                while True:
                    data = client.recv(1024).decode().strip()
                    if not data:
                        break
                    
                    if data.lower() == 'quit':
                        break
                    
                    response = self.evaluate(data)
                    client.sendall(f"{response}\n".encode())
            
            except Exception as e:
                print(f"Error con cliente {address}: {e}")
            finally:
                client.close()
                print(f"Cliente {address} desconectado")

class CalculatorClient:
    def __init__(self, host='::1', port=8892):
        self.client = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        self.client.connect((host, port, 0, 0))
    
    def run(self):
        print("Calculadora Cliente IPv6")
        print("Operaciones disponibles: +, -, *, /, ^")
        print("Formato: número operador número")
        print("También: sqrt número")
        print("Escriba 'quit' para salir")
        
        try:
            while True:
                expression = input("> ")
                if expression.lower() == 'quit':
                    break
                
                self.client.sendall(expression.encode())
                response = self.client.recv(1024).decode()
                print(response.strip())
        
        finally:
            self.client.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "server":
        server = CalculatorServer()
        server.start()
    else:
        client = CalculatorClient()
        client.run()