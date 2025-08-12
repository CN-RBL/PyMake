def get_system_language() -> str:
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\International") as key:
                locale_name = winreg.QueryValueEx(key, "LocaleName")[0]
                # 直接转换格式：en-US -> en-us
                return locale_name.lower().replace('_', '-')
        except:
            return "en-us"

if __name__ == '__main__':
    print(get_system_language())
