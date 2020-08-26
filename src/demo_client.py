import os
import argparse
import lib_client


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='grpc ip & port setting')

    parser.add_argument('--ip', required=True, help='write ip')
    parser.add_argument('--port', required=False, default='8888', help='write port')
    parser.add_argument('--input', required=True, help='input filename')
    parser.add_argument('--output', required=False, default='result.jpg', help='output filename')


    args = parser.parse_args()


    ipport = args.ip + ":" + args.port
    client = lib_client.FileClient(ipport)


    # demo for file uploading
    #in_file_name = './defpedimg.jpg'
    in_file_name = args.input
    client.upload(in_file_name)

    # demo for file downloading:
    out_file_name = args.output
    if os.path.exists(out_file_name):
        os.remove(out_file_name)
    client.download('whatever_name', out_file_name)
    os.system(f'sha1sum {in_file_name}')
    os.system(f'sha1sum {out_file_name}')
