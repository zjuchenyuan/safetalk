"""
SafeTalk
End to end talk encryption, automatically read and clipboard
Using pure python rsa module, so the message cannot be too long

Author: zjuchenyuan
"""

import rsa
import base64
import pickle
import traceback
import binascii
import threading
import os
from time import sleep
from storage import storage_save, storage_get
from myclipboard import clipboard_write, clipboard_read
__all__ = ['generate_key', 'show_mypubkey']


def b64(data):
    """
    object -> base64 encoded str
    """
    return base64.b64encode(pickle.dumps(data)).decode().replace("/","@")

def d64(mystr):
    """decode
    str -> object
    no exception handle
    """
    return pickle.loads(base64.b64decode(mystr.replace("@","/")))

def generate_key(keysize = 1024, show=True):
    """
    generate and save to mypubkey, myprivkey
    if show, write mypub to clipboard
    return (mypubkey, myprivkey)
    """
    (mypub, mypriv) = rsa.newkeys(keysize, poolsize=4, accurate=False)
    storage_save("mypub",mypub)
    storage_save("mypriv",mypriv)
    if show:
       show_pubkey(mypub)
    return (mypub, mypriv)

def show_pubkey(pubkey=None):
    if pubkey is None:
        pubkey = storage_get("mypub")
    print("* Your Public Key: "+b64(pubkey))
    clipboard_write(b64(pubkey))
    

def receive_hispubkey(mypub=None):
    """
    Try to get his public key from clipboard, saved to "hispub"
    return True if success else False
    """
    if mypub is None:
        mypub = storage_get("mypub")
    try:
        rawdata = clipboard_read()
        hispub = d64(rawdata)
        if not isinstance(hispub, rsa.PublicKey):
            return False
        if hispub == mypub:
            return False # clipboard not changed
        else:
            storage_save("hispub",hispub)
            return True,hispub
    except:
        return False

def decrypt_hismessage(mypriv=None):
    """
    Try to decrypt his message using mypriv
    return message if success else False
    """
    if mypriv is None:
        mypriv = storage_get("mypriv")
    try:
        rawdata = clipboard_read()
        crypto = d64(rawdata)
        message = rsa.decrypt(crypto, mypriv)
        return message
    except:
        return False

def encrypt_mymessage(message, hispub=None):
    if hispub is None:
        hispub = storage_get("hispub")
    message = bytes(message,encoding='utf-8')
    try:
        rawdata = rsa.encrypt(message,hispub)
        return b64(rawdata)
    except OverflowError:
        print("! your message is too long")
        raise
    

def show_message(data):
    message = data.decode()
    print()
    print("$ "+message)

def thread_decrypt(mypriv=None):
    oldmessage = ''
    while True:
        sleep(0.5)
        message = decrypt_hismessage(mypriv)
        if message is not False and message!=oldmessage:
            oldmessage = message
            show_message(message)

def main():
    hispub = None
    tmp = receive_hispubkey("")
    if tmp:
        hispub = tmp[1]
        flag = False
    else:
        flag = True
    mypub,mypriv = generate_key()
    print("! Waiting for copy his key...")
    while flag:
        sleep(0.5)
        tmp = receive_hispubkey(mypub)
        flag = not tmp
    if hispub is None:
        hispub = tmp[1]
    print("* his key received, start chat now")
    print("* Try send this to him: "+encrypt_mymessage("hello world!", hispub))
    t = threading.Thread(target=thread_decrypt,args=[mypriv])
    t.start()
    try:
        while 1:
            userinput = input("! Input your message: ")
            try:
                message = encrypt_mymessage(userinput, hispub)
            except OverflowError:
                clipboard_write("[error]too long message", show=False)
            else:
                clipboard_write(message)
    except:
        traceback.print_exc()
        os._exit(0)
    finally:
        os._exit(0)
    

if __name__ == "__main__":
    main()