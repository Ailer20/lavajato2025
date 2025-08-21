#!/usr/bin/env python3
"""
Wrapper Flask para o projeto Django Lava Jato 2025
Este arquivo permite que o projeto Django seja executado através do Flask para deploy
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório do projeto ao Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lavajato2025.settings')

import django
django.setup()

from django.core.wsgi import get_wsgi_application
from flask import Flask

# Criar aplicação Flask
app = Flask(__name__)

# Obter aplicação WSGI do Django
django_app = get_wsgi_application()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy_to_django(path):
    """Proxy todas as requisições para o Django"""
    from werkzeug.serving import WSGIRequestHandler
    from werkzeug.wrappers import Request, Response
    from werkzeug.wsgi import DispatcherMiddleware
    
    # Criar um dispatcher que redireciona tudo para Django
    application = DispatcherMiddleware(django_app)
    
    # Processar a requisição através do Django
    return application

if __name__ == '__main__':
    # Para desenvolvimento local
    app.run(host='0.0.0.0', port=8000, debug=True)

