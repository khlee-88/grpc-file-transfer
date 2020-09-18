import os
from concurrent import futures
import cv2
import grpc
import time
import chunk_pb2, chunk_pb2_grpc

CHUNK_SIZE = 1024 * 1024  # 1MB

def get_file_chunks(filename):
    with open(filename, 'rb') as f:
        count = 0;
        while True:
            print("get file chunk : %d" % count)
            count = count +1
            piece = f.read(CHUNK_SIZE)
            if len(piece) == 0:
                return
            yield chunk_pb2.Chunk(buffer=piece)


def save_chunks_to_file(chunks, filename):
    with open(filename, 'wb') as f:
        for chunk in chunks:
            f.write(chunk.buffer)

def print_detection(response):
    print("classID : %d" % response.classID)
    print("confidence : %f" % response.confidence)
    print("left : %f" % response.lefet)
    print("top : %f" % response.top)
    print("right : %f" % response.right)
    print("bottom : %f" % response.bottom)
    print("width : %f" % response.width)
    print("height : %f" % response.height)
    print("area : %f" % response.area)
    print("center_x : %f" % response.center_x)
    print("center_y : %f" % response.center_y)

class FileClient:
    def __init__(self, address):
        channel = grpc.insecure_channel(address)
        self.stub = chunk_pb2_grpc.FileServerStub(channel)

    def upload(self, in_file_name):
        chunks_generator = get_file_chunks(in_file_name)
        response = self.stub.upload(chunks_generator)
        #print(response)
        #print(response.length)
        #print(os.path.getsize(in_file_name))
        #assert response.length == os.path.getsize(in_file_name)

    def upload_box(self, in_file_name):
        chunks_generator = get_file_chunks(in_file_name)
        response = self.stub.upload_box(chunks_generator)
        print(response.length)
        print(os.path.getsize(in_file_name))
        #assert response.length == os.path.getsize(in_file_name)

    def download(self, target_name, out_file_name):
        response = self.stub.download(chunk_pb2.Request(name=target_name))
        save_chunks_to_file(response, out_file_name)
    def download_detection(self, target_name, out_file_name):
        response = self.stub.download_detection(chunk_pb2.Detection(name=target_name))

    def alive(self, al):
        response = self.stub.alive(chunk_pb2.Alive(heartbeat=10))
        print("alive return : %d" % response.heartbeat)

    def alive_stream(self, img):
        request = chunk_pb2.Alive(heartbeat=10)
        response_iterator = self.stub.alive_stream(request)
        image = cv2.imread(img, 1)
        for response in response_iterator :
            #print("alive stream return : %f" % response.left)
            cv2.rectangle(image, (int(response.left), int(response.top)), (int(response.right), int(response.bottom)), (0,0,255), 3)
        cv2.imwrite('result_box.jpg', image)
        



        
