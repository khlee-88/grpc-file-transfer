import os
import argparse
import lib_client
import time


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='grpc ip & port setting')

    parser.add_argument('--ip', required=False, default='localhost', help='write ip')
    parser.add_argument('--port', required=False, default='8888', help='write port')
    parser.add_argument('--input', required=False, default='./defpedimg.jpg', help='input filename')
    parser.add_argument('--output', required=False, default='result.jpg', help='output filename')


    args = parser.parse_args()


    ipport = args.ip + ":" + args.port

    try:
        client = lib_client.FileClient(ipport)
    except:
        time.sleep(2)
        print("\n\ntimeout\n\n")
        print("\n\ntimeout\n\n")
        print("\n\ntimeout\n\n")
        print("\n\ntimeout\n\n")


    # demo for file uploading
    #in_file_name = './defpedimg.jpg'
    in_file_name = args.input
    #client.upload(in_file_name)
    result = client.upload(in_file_name)
    print(result)

    # demo for file downloading:
    out_file_name = args.output
    if os.path.exists(out_file_name):
        os.remove(out_file_name)
    #print("download")
    client.download('whatever_name', out_file_name)
    client.alive_stream(in_file_name)
    #print("download detection")
    #client.download_detection('whatever_name', out_file_name)

    #client.download_detection('whatever_name', out_file_name)
    os.system(f'sha1sum {in_file_name}')
    os.system(f'sha1sum {out_file_name}')
