#!/usr/bin/env python3
"""
Простой HTTP сервер для тестирования EM.Intranet Mini App
Запуск: python simple_server.py
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

def main():
    """Запуск простого сервера"""
    
    # Проверяем, что мы в правильной директории
    if not Path('index.html').exists():
        print("❌ Файл index.html не найден!")
        print("   Запустите скрипт из папки mini_app")
        sys.exit(1)
    
    print("🍄 EM.Intranet Mini App Server (Simple)")
    print("=" * 40)
    
    try:
        # Создаем обработчик на основе SimpleHTTPRequestHandler
        handler = http.server.SimpleHTTPRequestHandler
        
        with socketserver.TCPServer((HOST, PORT), handler) as httpd:
            url = f"http://{HOST}:{PORT}"
            
            print(f"🚀 Сервер запущен на {url}")
            print("📱 Откройте ссылку в браузере для тестирования")
            print("\n💡 Для остановки сервера нажмите Ctrl+C")
            print("🔄 Обновляйте страницу для просмотра изменений\n")
            
            # Автоматически открываем браузер
            try:
                webbrowser.open(url)
                print("🌐 Браузер открыт автоматически")
            except:
                print("⚠️  Не удалось открыть браузер автоматически")
                print(f"   Откройте {url} вручную")
            
            print("\n🟢 Сервер работает...\n")
            
            # Запускаем сервер
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n\n🛑 Сервер остановлен")
        sys.exit(0)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Порт {PORT} уже используется!")
            print("   Попробуйте изменить PORT в скрипте или подождите")
        else:
            print(f"❌ Ошибка запуска сервера: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 