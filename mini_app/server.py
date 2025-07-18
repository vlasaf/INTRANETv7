#!/usr/bin/env python3
"""
Простой HTTP сервер для тестирования EM.Intranet Mini App
Запуск: python server.py
"""

import http.server
import socketserver
import os
import sys
import webbrowser
from pathlib import Path

# Конфигурация
PORT = 8000
HOST = "localhost"

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Кастомный обработчик с правильными MIME типами и CORS заголовками"""
    
    def end_headers(self):
        # Добавляем CORS заголовки для разработки
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def guess_type(self, path):
        # Правильные MIME типы для веб файлов
        if path.endswith('.js'):
            return 'application/javascript'
        elif path.endswith('.css'):
            return 'text/css'
        elif path.endswith('.html'):
            return 'text/html'
        
        # Возвращаем стандартный тип для остальных файлов
        return super().guess_type(path)
    
    def do_GET(self):
        # Если запрашивают корень, отдаем index.html
        if self.path == '/':
            self.path = '/index.html'
        
        return super().do_GET()
    
    def log_message(self, format, *args):
        # Красивые логи
        print(f"🌐 {args[0]} - {args[1]}")

def main():
    """Запуск сервера"""
    
    # Проверяем, что мы в правильной директории
    if not Path('index.html').exists():
        print("❌ Файл index.html не найден!")
        print("   Запустите скрипт из папки mini_app")
        sys.exit(1)
    
    print("🍄 EM.Intranet Mini App Server")
    print("=" * 40)
    
    try:
        with socketserver.TCPServer((HOST, PORT), CustomHTTPRequestHandler) as httpd:
            url = f"http://{HOST}:{PORT}"
            
            print(f"🚀 Сервер запущен на {url}")
            print("📱 Откройте ссылку в браузере для тестирования")
            print("🔧 Для тестирования в Telegram используйте ngrok или аналогичный туннель")
            print("\n📋 Горячие клавиши:")
            print("   Ctrl+C - остановить сервер")
            print("   Ctrl+Shift+R - перезагрузить страницу без кеша")
            print("=" * 40)
            
            # Автоматически открываем браузер
            try:
                webbrowser.open(url)
                print("🌐 Браузер открыт автоматически")
            except:
                print("⚠️  Не удалось открыть браузер автоматически")
                print(f"   Откройте {url} вручную")
            
            print(f"\n💡 Для остановки сервера нажмите Ctrl+C")
            print("🔄 Обновляйте страницу для просмотра изменений\n")
            
            # Запускаем сервер
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n\n🛑 Сервер остановлен")
        sys.exit(0)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Порт {PORT} уже используется!")
            print("   Попробуйте:")
            print("   1. Остановить другие серверы")
            print("   2. Изменить PORT в скрипте")
            print("   3. Подождать несколько секунд и попробовать снова")
        else:
            print(f"❌ Ошибка запуска сервера: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 