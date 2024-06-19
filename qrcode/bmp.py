# copied somewhere but i dont remember

def write_grayscale(file, pixels):
    height = len(pixels)
    width = len(pixels[0])

    file.write(b'BM')

    size_bookmark = file.tell()  # The next four bytes hold the filesize as a 32-bit
    file.write(b'\x00\x00\x00\x00')  # little-endian integer. Zero placeholder for now.

    file.write(b'\x00\x00')  # Unused 16-bit integer - should be zero
    file.write(b'\x00\x00')  # Unused 16-bit integer - should be zero

    pixel_offset_bookmark = file.tell()  # The next four bytes hold the integer offset
    file.write(b'\x00\x00\x00\x00')  # to the pixel data. Zero placeholder for now.

    # Image header
    file.write(b'\x28\x00\x00\x00')  # Image header size in bytes - 40 decimal
    file.write(_int32_to_bytes(width))  # Image width in pixels
    file.write(_int32_to_bytes(height))  # Image height in pixels
    file.write(b'\x01\x00')  # Number of image planes
    file.write(b'\x08\x00')  # Bits per pixel 8 for grayscale
    file.write(b'\x00\x00\x00\x00')  # No compression
    file.write(b'\x00\x00\x00\x00')  # Zero for uncompressed images
    file.write(b'\x00\x00\x00\x00')  # Unused pixels per meter
    file.write(b'\x00\x00\x00\x00')  # Unused pixels per meter
    file.write(b'\x00\x00\x00\x00')  # Use whole color table
    file.write(b'\x00\x00\x00\x00')  # All colors are important

    # Color palette - a linear grayscale
    for c in range(256):
        file.write(bytes((c, c, c, 0)))

    # Pixel data
    pixel_data_bookmark = file.tell()
    for row in reversed(pixels):  # BMP files are bottom to top
        row_data = bytes(row)
        file.write(row_data)
        padding = b'\x00' * ((4 - (len(row) % 4)) % 4)  # Pad row to multiple of four bytes
        file.write(padding)

    # End of file
    eof_bookmark = file.tell()

    # Fill in file size placeholder
    file.seek(size_bookmark)
    file.write(_int32_to_bytes(eof_bookmark))

    # Fill in pixel
    file.seek(pixel_offset_bookmark)
    file.write(_int32_to_bytes(pixel_data_bookmark))

def _int32_to_bytes(i):
    """Convert an integer to four bytes in little-endian format."""
    return bytes((i & 0xff,
                  i >> 8 & 0xff,
                  i >> 16 & 0xff,
                  i >> 24 & 0xff))

