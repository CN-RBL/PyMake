import py7zr
import zipfile
import os
import shutil

try:shutil.rmtree(".release")
except:pass
os.mkdir(".release")

if os.path.exists("pymake.7z"):
    os.remove("pymake.7z")

if os.path.exists("pymake.zip"):
    os.remove("pymake.zip")

os.system(".venv\\Scripts\\python.exe main.py --load-config config.json")
os.rename(".release\\main.exe", ".release\\pymake.exe")
shutil.copytree("lang", ".release\\lang\\")

with py7zr.SevenZipFile("pymake.7z", "w", password="pymake") as release_7z:
    for _ in os.listdir(".release"):
        release_7z.write(f".release\\{_}")

with zipfile.ZipFile("pymake.zip", "w") as release_zip:
    for _ in os.listdir(".release"):
        release_zip.write(f".release\\{_}")

shutil.rmtree(".release")
