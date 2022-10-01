# import ctypes
# user32 = ctypes.windll.User32
# lst = ['Unlocked']
# print('Unlocked')
# while True:
#     if user32.GetForegroundWindow() == 0: # check if the user changed the window he is working on
#         if lst[-1] != 'Locked':
#             lst.append('Locked')
#             print('Locked')
#     else:
#         if lst[-1] != 'Unlocked':
#             lst.append('Unlocked')
#             print('Unlocked')


# import psutil
#
# name = ''
# while True:
#     for proc in psutil.process_iter():
#         if proc.name() == "LogonUI.exe":
#             print("Locked")
#             break
