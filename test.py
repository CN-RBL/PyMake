import subprocess as sp
import os
import re
import string


class Error(Exception): pass
class ScriptError(Error): pass
class VBoxError(ScriptError): pass

class NoVBox7_2_2EXISTS(VBoxError): pass


VMM = "VBoxManage"
VMM_INI_PATH = "C:\\Users\\RBL\\Desktop\\vmm.ini"
try:
    with open(VMM_INI_PATH, "r", encoding="utf-8") as f:
        VMM_PATH = f.read()
except:
    VMM_PATH = ""

print("尝试获取VBox版本")

try:
    if os.path.exists(VMM_PATH):
        VMM = VMM_PATH
    elif "VBoxManage" in os.environ.get("PATH", ""):
        result = sp.run([VMM, "--version"], capture_output=True, text=True, timeout=7)
        vbox_version = re.search(r"(\d+\.\d+\.\d+)", result.stdout.strip()).group(1)
    else:
        results = []

        # 获取所有驱动器
        drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]

        for drive in drives:
            print(f"正在搜索 {drive}...")
            for root, dirs, files in os.walk(drive):
                if "VBoxManage.exe" in files:
                    file_path = os.path.join(root, "VBoxManage.exe")
                    results.append(file_path)
        for _ in results:
            result = sp.run([_, "--version"], capture_output=True, text=True, timeout=7)
            vbox_version = re.search(r"(\d+\.\d+\.\d+)", result.stdout.strip()).group(1)
            if vbox_version == "7.2.2":
                VMM = _
                with open("C:\\Users\\RBL\\Desktop\\vmm.ini", "wt") as vmm_path:
                    vmm_path.write(VMM)
                break
        else:
            raise NoVBox7_2_2EXISTS("没有VBoxManage.exe v7.2.2，无法继续")

except NoVBox7_2_2EXISTS as e:
    raise e
except Exception as e:
    print(e)


