
python -m pip install -r requirements.txt --target=./qrcode/lib

7z -mx9 -tzip a ./build/qrcode.keypirinha-package ./qrcode/* && copy /Y .\build\qrcode.keypirinha-package %appdata%\Keypirinha\InstalledPackages\
