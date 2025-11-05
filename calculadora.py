#!/usr/bin/env python3
"""
Calculadora Básica con Interfaz Web
Una calculadora simple con interfaz gráfica usando Python y HTML
"""

import http.server
import socketserver
import webbrowser
import os
from urllib.parse import parse_qs, urlparse

PORT = 8000

# HTML de la interfaz de la calculadora
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Calculadora Básica</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        .calculator {
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            width: 320px;
        }
        
        .calculator h1 {
            text-align: center;
            color: #667eea;
            margin-bottom: 20px;
            font-size: 24px;
        }
        
        .display {
            width: 100%;
            height: 60px;
            background: #f0f0f0;
            border: 2px solid #667eea;
            border-radius: 10px;
            margin-bottom: 20px;
            font-size: 28px;
            text-align: right;
            padding: 15px;
            font-weight: bold;
            color: #333;
        }
        
        .buttons {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
        }
        
        button {
            height: 60px;
            border: none;
            border-radius: 10px;
            font-size: 20px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            color: white;
        }
        
        button:hover {
            transform: scale(1.05);
        }
        
        button:active {
            transform: scale(0.95);
        }
        
        .num-btn, .decimal-btn {
            background: #667eea;
        }
        
        .operator-btn {
            background: #764ba2;
        }
        
        .clear-btn {
            background: #e74c3c;
            grid-column: span 2;
        }
        
        .equals-btn {
            background: #27ae60;
            grid-column: span 2;
        }
        
        .zero-btn {
            grid-column: span 2;
        }
    </style>
</head>
<body>
    <div class="calculator">
        <h1>Calculadora Básica</h1>
        <input type="text" class="display" id="display" value="0" readonly>
        <div class="buttons">
            <button class="clear-btn" onclick="clearDisplay()">C</button>
            <button class="operator-btn" onclick="appendOperator('/')">/</button>
            <button class="operator-btn" onclick="appendOperator('*')">×</button>
            
            <button class="num-btn" onclick="appendNumber('7')">7</button>
            <button class="num-btn" onclick="appendNumber('8')">8</button>
            <button class="num-btn" onclick="appendNumber('9')">9</button>
            <button class="operator-btn" onclick="appendOperator('-')">-</button>
            
            <button class="num-btn" onclick="appendNumber('4')">4</button>
            <button class="num-btn" onclick="appendNumber('5')">5</button>
            <button class="num-btn" onclick="appendNumber('6')">6</button>
            <button class="operator-btn" onclick="appendOperator('+')">+</button>
            
            <button class="num-btn" onclick="appendNumber('1')">1</button>
            <button class="num-btn" onclick="appendNumber('2')">2</button>
            <button class="num-btn" onclick="appendNumber('3')">3</button>
            <button class="decimal-btn" onclick="appendNumber('.')">.</button>
            
            <button class="num-btn zero-btn" onclick="appendNumber('0')">0</button>
            <button class="equals-btn" onclick="calculate()">=</button>
        </div>
    </div>
    
    <script>
        let display = document.getElementById('display');
        let currentValue = '0';
        let operator = null;
        let previousValue = null;
        let resetDisplay = false;
        
        function appendNumber(num) {
            if (resetDisplay || currentValue === '0') {
                currentValue = num === '.' ? '0.' : num;
                resetDisplay = false;
            } else {
                if (num === '.' && currentValue.includes('.')) return;
                currentValue += num;
            }
            updateDisplay();
        }
        
        function appendOperator(op) {
            if (operator && !resetDisplay) {
                calculate();
            }
            previousValue = currentValue;
            operator = op;
            resetDisplay = true;
        }
        
        function calculate() {
            if (operator && previousValue !== null) {
                let prev = parseFloat(previousValue);
                let current = parseFloat(currentValue);
                let result;
                
                switch(operator) {
                    case '+':
                        result = prev + current;
                        break;
                    case '-':
                        result = prev - current;
                        break;
                    case '*':
                        result = prev * current;
                        break;
                    case '/':
                        if (current !== 0) {
                            result = prev / current;
                        } else {
                            currentValue = 'Error';
                            operator = null;
                            previousValue = null;
                            resetDisplay = true;
                            updateDisplay();
                            return;
                        }
                        break;
                }
                
                currentValue = result.toString();
                operator = null;
                previousValue = null;
                resetDisplay = true;
                updateDisplay();
            }
        }
        
        function clearDisplay() {
            currentValue = '0';
            operator = null;
            previousValue = null;
            resetDisplay = false;
            updateDisplay();
        }
        
        function updateDisplay() {
            display.value = currentValue;
        }
        
        // Soporte para teclado
        document.addEventListener('keydown', function(event) {
            if (event.key >= '0' && event.key <= '9') {
                appendNumber(event.key);
            } else if (event.key === '.') {
                appendNumber('.');
            } else if (event.key === '+' || event.key === '-' || event.key === '*' || event.key === '/') {
                appendOperator(event.key);
            } else if (event.key === 'Enter' || event.key === '=') {
                calculate();
            } else if (event.key === 'Escape' || event.key === 'c' || event.key === 'C') {
                clearDisplay();
            }
        });
    </script>
</body>
</html>
"""


class CalculadoraHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        """Maneja las peticiones GET"""
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode('utf-8'))
        else:
            self.send_error(404, 'Archivo no encontrado')


def main():
    """Función principal para iniciar el servidor"""
    print("=" * 50)
    print("Calculadora Básica con Interfaz Web")
    print("=" * 50)
    print(f"\nIniciando servidor en http://localhost:{PORT}")
    print("\nInstrucciones:")
    print("1. El navegador se abrirá automáticamente")
    print("2. Si no se abre, visita: http://localhost:{}".format(PORT))
    print("3. Usa el mouse o el teclado para realizar cálculos")
    print("4. Presiona Ctrl+C para detener el servidor")
    print("\nControles del teclado:")
    print("  - Números: 0-9")
    print("  - Operadores: +, -, *, /")
    print("  - Decimal: .")
    print("  - Calcular: Enter o =")
    print("  - Limpiar: Esc o C")
    print("=" * 50)
    
    with socketserver.TCPServer(("", PORT), CalculadoraHandler) as httpd:
        # Intentar abrir el navegador automáticamente
        try:
            webbrowser.open(f'http://localhost:{PORT}')
        except (OSError, webbrowser.Error) as e:
            print(f"Nota: No se pudo abrir el navegador automáticamente: {e}")
            print(f"Por favor, abre manualmente: http://localhost:{PORT}")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nServidor detenido.")
            print("¡Gracias por usar la calculadora!")


if __name__ == "__main__":
    main()
