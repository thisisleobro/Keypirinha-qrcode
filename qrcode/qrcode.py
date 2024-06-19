import keypirinha as kp
import keypirinha_net as kpn
import keypirinha_util as kpu

from base64 import b64decode
from io import BytesIO, StringIO
import threading
import time
import tempfile

from .lib import segno
from .lib import png
from . import bmp

import ctypes.wintypes
from ctypes import (
	c_buffer, c_byte, c_char, c_char_p, c_ubyte, c_uint8,
	c_void_p, cast, create_string_buffer, c_size_t,
	windll, memmove, sizeof, c_wchar, c_wchar_p, cdll)
import ctypes
from ctypes.wintypes import (
	HGLOBAL, LPVOID, DWORD, LPCSTR, INT, HWND,
	HINSTANCE, HMENU, BOOL, UINT, HANDLE)


OpenClipboard = windll.user32.OpenClipboard
OpenClipboard.argtypes = [HWND]
OpenClipboard.restype = BOOL

EmptyClipboard = windll.user32.EmptyClipboard
EmptyClipboard.argtypes = []
EmptyClipboard.restype = BOOL

SetClipboardData = ctypes.windll.user32.SetClipboardData
SetClipboardData.argtypes = [UINT, HANDLE]
SetClipboardData.restype = HANDLE

CloseClipboard = windll.user32.CloseClipboard
CloseClipboard.argtypes = []
CloseClipboard.restype = BOOL

GlobalAlloc = ctypes.windll.kernel32.GlobalAlloc
GlobalAlloc.argtypes = UINT, c_size_t
GlobalAlloc.restype = HANDLE

GlobalLock = ctypes.windll.kernel32.GlobalLock
GlobalLock.argtypes = (HGLOBAL,)
GlobalLock.restype = LPVOID

GlobalUnlock = ctypes.windll.kernel32.GlobalUnlock
GlobalUnlock.argtypes = (HGLOBAL,)
GlobalUnlock.restype = BOOL

GlobalSize = ctypes.windll.kernel32.GlobalSize
GlobalSize.argtypes = (HGLOBAL,)
GlobalSize.restype = ctypes.c_size_t

CreateWindowExA = windll.user32.CreateWindowExA
CreateWindowExA.argtypes = [DWORD, LPCSTR, LPCSTR, DWORD, INT, INT,
	INT, INT, HWND, HMENU, HINSTANCE, LPVOID]
CreateWindowExA.restype = HWND

DestroyWindow = windll.user32.DestroyWindow
DestroyWindow.argtypes = [HWND]
DestroyWindow.restype = BOOL

wcscpy = ctypes.cdll.msvcrt.wcscpy
OpenClipboard = ctypes.windll.user32.OpenClipboard
EmptyClipboard = ctypes.windll.user32.EmptyClipboard
GetClipboardData = ctypes.windll.user32.GetClipboardData
SetClipboardData = ctypes.windll.user32.SetClipboardData
CloseClipboard = ctypes.windll.user32.CloseClipboard
GlobalAlloc = ctypes.windll.kernel32.GlobalAlloc
GlobalSize = ctypes.windll.kernel32.GlobalSize
GlobalLock = ctypes.windll.kernel32.GlobalLock
GlobalUnlock = ctypes.windll.kernel32.GlobalUnlock

CF_TEXT = 1
CF_BITMAP = 2
CF_DIB = 8
CF_UNICODETEXT = 13

GMEM_FIXED = 0
GMEM_MOVEABLE = 0x0002
GMEM_ZEROINIT = 0x0004
GMEM_DDESHARE = 0x2000

COPY_TO_CLIPBOARD_TARGET = 'copy-to-clipboard'
OPEN_IMAGE_TARGET = 'open-image'


class Qr(kp.Plugin):
	ITEMCAT_RESULT = kp.ItemCategory.USER_BASE + 1
	scale = 10
	border = 1

	def __init__(self):
		super().__init__()

	def on_start(self):
		pass

	def _generate_dib_content(self, text):
		qrcode = segno.make_qr(text)

		image_uri = qrcode.png_data_uri(
			scale=self.scale,
			border=self.border,
		)

		_header, encoded = image_uri.split("base64,", 1)

		data = b64decode(encoded)

		image = png.Reader(bytes=data).read_flat()

		width = image[3]['size'][0]
		height = image[3]['size'][1]
		content = image[2]

		matrix = []
		for y in range(height):
			matrix.append([])
			for x in range(width):
				matrix[y].append(content[y*width + x -1] * 255)
			# print(matrix[y])

		file = BytesIO()
		bmp.write_grayscale(file, matrix)

		return file.read()

	def _copy_to_clipboard(self, text):
		data = self._generate_dib_content(text)

		OpenClipboard(None)
		EmptyClipboard()

		expected_size = len(data) + 1

		handle  = GlobalAlloc(
			GMEM_MOVEABLE,
			expected_size * sizeof(c_char))

		allocated_size = GlobalSize(handle)

		locked_handle = GlobalLock(handle)
	
		# memmove(c_wchar_p(locked_handle), c_wchar_p('teste'), expected_size * sizeof(c_wchar))
		moved = memmove(c_void_p(locked_handle), c_char_p(data), expected_size)
		# memmove(c_char_p(locked_handle), c_char_p(data), expected_size * sizeof(c_char))

		GlobalUnlock(handle)

		# SetClipboardData(CF_UNICODETEXT, handle)
		SetClipboardData(CF_DIB, handle)

		CloseClipboard()

		# GlobalFree(handle)

		# except:
		# 	kernel32dll.GlobalFree(handle)
		# DestroyWindow(hwnd)
		# 	raise NameError()

	def _open_image(self, text):
		qrcode = segno.make_qr(text)

		# temp_file = tempfile.NamedTemporaryFile('wb', suffix='.png')

		qrcode.show(
			scale=self.scale,
			border=self.border,
		)

	def on_catalog(self):
		# icon_handle = self.load_icon('OUR_ICON')
		self.set_catalog([
			self.create_item(
				category=kp.ItemCategory.REFERENCE,
				label="QR Code",
				short_desc="Input string to transform to QR Code",
				target='Input string',
				args_hint=kp.ItemArgsHint.REQUIRED,
				hit_hint=kp.ItemHitHint.IGNORE,
				# icon_handle =icon_handle,
			)
		])

	def on_suggest(self, user_input, items_chain=[]):
		# icon_handle = self.load_icon('@C:\\Windows\\system32\\shell32.dll,164')
		if not items_chain or items_chain[0].category() != kp.ItemCategory.REFERENCE:
			return

		if not user_input:
			return

		# self.set_default_icon(self.load_icon('@C:\\Windows\\system32\\shell32.dll,164'))


		# self.deb(self._create_image_file)()
		# self._create_image_file()
		# print('image_uri', image_uri)

		self.set_suggestions([
			self.create_item(
				category=self.ITEMCAT_RESULT,
				label=user_input,
				short_desc='Copy image to clipboard',
				target=COPY_TO_CLIPBOARD_TARGET,
				args_hint=kp.ItemArgsHint.FORBIDDEN,
				hit_hint=kp.ItemHitHint.IGNORE,
				icon_handle=None
				# data_bag=image_uri
			),
			self.create_item(
				category=self.ITEMCAT_RESULT,
				label=user_input,
				short_desc='Open image',
				target=OPEN_IMAGE_TARGET,
				args_hint=kp.ItemArgsHint.FORBIDDEN,
				hit_hint=kp.ItemHitHint.IGNORE,
				icon_handle=None
				# data_bag=image_uri
			)
		])

	def on_execute(self, item, action):
		target = item.target()
		text = item.label()

		if target == COPY_TO_CLIPBOARD_TARGET:
			self._copy_to_clipboard(text)

		if target == OPEN_IMAGE_TARGET:
			self._open_image(text)
