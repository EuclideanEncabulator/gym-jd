from ctypes import *
from ctypes import wintypes as win

PROCESS_ALL_ACCESS = 0x000F0000 | 0x00100000 | 0xFFF
PAGE_EXECUTE_READWRITE = 0x40
MEM_COMMIT = 0x1000
MEM_RESERVE = 0x2000

kernel32 = windll.kernel32

open_process = kernel32.OpenProcess
open_process.argtypes = [win.DWORD, win.BOOL, win.DWORD]
open_process.restype = win.HANDLE

virtual_alloc = kernel32.VirtualAllocEx
virtual_alloc.argtypes = [win.HANDLE, win.LPVOID, win.DWORD, win.DWORD, win.DWORD]
virtual_alloc.restype = win.LPVOID

write_process_memory = kernel32.WriteProcessMemory
write_process_memory.argtypes = [win.HANDLE, win.LPVOID, win.LPCVOID, win.DWORD, win.DWORD]
write_process_memory.restype = win.BOOL

get_module_handle = kernel32.GetModuleHandleA
get_module_handle.argtypes = [win.LPCSTR]
get_module_handle.restype = win.HMODULE

get_proc_address = kernel32.GetProcAddress
get_proc_address.argtypes = [win.HMODULE, win.LPCSTR]
get_proc_address.restype = win.LPVOID

create_remote_thread = kernel32.CreateRemoteThread
create_remote_thread.argtypes = [win.HANDLE, win.LPVOID, win.DWORD, win.LPVOID, win.LPVOID, win.DWORD, win.LPDWORD]
create_remote_thread.restype = win.HANDLE

def inject(pid, dll_path):
    dll_size = len(dll_path)
    thread_id = c_ulong(0)

    process = open_process(PROCESS_ALL_ACCESS, False, pid)
    allocation = virtual_alloc(process, 0, dll_size, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE)
    wrote = write_process_memory(process, allocation, dll_path, dll_size, 0)
    module = get_module_handle(b"kernel32.dll")
    loadlibrary = get_proc_address(module, b"LoadLibraryA")
    thread_return = create_remote_thread(process, None, 0, loadlibrary, allocation, 0, byref(thread_id))
