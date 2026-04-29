def detect_abnormal(system_data, known_processes):
    alerts = []

    cpu = system_data.get("cpu", 0)
    memory = system_data.get("memory", 0)
    processes = system_data.get("processes", [])

    if cpu > 80:
        alerts.append(f"High CPU Usage: {cpu}%")

   
    if memory > 80:
        alerts.append(f" High Memory Usage: {memory}%")

    
    for proc in processes:
        name = proc if isinstance(proc, str) else proc.get("name", "")

        if name and name not in known_processes:
            alerts.append(f"Suspicious Process Detected: {name}")
            break

    return alerts