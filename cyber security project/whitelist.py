import psutil

def generate_whitelist():
    whitelist = []
    for p in psutil.process_iter(['name']):
        try:
            name = p.info['name']
            if  name  not in whitelist:
                whitelist.append(name)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return whitelist