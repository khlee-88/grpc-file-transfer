import os

import lib2


if __name__ == '__main__':
    client = lib2.FileClient('localhost:8888')

    # demo for file uploading
    in_file_name = './defpedimg.jpg'
    client.upload(in_file_name)

    # demo for file downloading:
    out_file_name = './result2.jpg'
    if os.path.exists(out_file_name):
        os.remove(out_file_name)
    client.download('whatever_name', out_file_name)
    os.system(f'sha1sum {in_file_name}')
    os.system(f'sha1sum {out_file_name}')
