# Projeto_AI

## Docker

Construir a imagem:

```powershell
docker compose build
```

Executar a aplicação:

```powershell
docker compose run --rm app
```

A aplicação Tkinter corre dentro de um desktop virtual no contentor e é
disponibilizada no navegador através do noVNC. Depois de iniciar:

```text
http://localhost:8082/vnc.html
```

Não é necessário instalar Python, Tesseract, Tkinter ou VcXsrv na máquina host.

O Tesseract e o idioma português já são instalados na imagem. Para usar outro
caminho do executável, defina `TESSERACT_CMD` ao iniciar o contentor.