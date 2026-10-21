# Genera dist\Fragil X - Genda.exe
python -m PyInstaller --noconfirm --clean --onefile --windowed `
    --name "Fragil X - Genda" `
    --icon "genda_ui\assets\icono.ico" `
    --add-data "templates\template_frax.docx;templates" `
    --add-data "genda_ui\assets;genda_ui\assets" `
    --collect-data customtkinter `
    --hidden-import win32timezone `
    main.py
