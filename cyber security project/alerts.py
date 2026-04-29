from plyer import notification

def send_alert(msg):
    notification.notify(
        title="Security Alert",
        message=msg,
        timeout=5
    )