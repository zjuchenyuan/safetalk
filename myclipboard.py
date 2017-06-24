from pyperclip import copy, paste

__all__ = ['clipboard_write', 'clipboard_read']

def clipboard_write(text, show=True):
    try:
        copy(text)
    except:
        print("[clipboard] failed, Please Ctrl+C manually")
    else:
        if show:
            print("[clipboard] success, Please Ctrl+V")

def clipboard_read():
    return paste()