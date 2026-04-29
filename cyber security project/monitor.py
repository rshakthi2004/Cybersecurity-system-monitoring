import psutil
 
def get_system_data():
    return {
        "cpu": psutil.cpu_percent(interval=1),
        "memory": psutil.virtual_memory().percent,
        # "disk": psutil.disk_usage('C:\\').percent,  
        "processes": [p.info['name'] for p in psutil.process_iter(['name'])]
    }