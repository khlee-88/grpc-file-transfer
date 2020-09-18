import os
from concurrent import futures

import grpc
import time
import jetson.inference
import jetson.utils
import chunk_pb2, chunk_pb2_grpc

CHUNK_SIZE = 1024 * 1024  # 1MB
sys_argv = ['--network=pednet', '--prototxt=deploy.prototxt', '--model=snapshot_iter_70800.cafemodel']
network = 'pednet'
overlay = 'box,labels,conf'
threshold = 0.5
out_filename = '/tmp/outfile.jpg'
detections = 0

def get_file_chunks(filename):
    with open(filename, 'rb') as f:
        while True:
            piece = f.read(CHUNK_SIZE);
            if len(piece) == 0:
                return
            yield chunk_pb2.Chunk(buffer=piece)

def response_detection():
    for i in detections:
        response = chunk_pb2.Detection(
            classID = i.classID,
            confidence = i.confidence,
            left = i.left,
            top = i.top,
            right = i.right,
            bottom = i.bottom,
            width = i.width,
            height = i.height,
            area = i.area,
            center_x = i.center_x,
            center_y = i.center_y)
        yield response


def save_chunks_to_file(chunks, filename):
    with open(filename, 'wb') as f:
        for chunk in chunks:
            f.write(chunk.buffer)
        img, width, height = jetson.utils.loadImageRGBA(filename)
        net = jetson.inference.detectNet(network, sys_argv, threshold)
        detections = net.Detect(img, width, height, overlay)
        #for i in detections:
        #    print(i)
        jetson.utils.saveImageRGBA(out_filename, img, width, height)
        return detections


def get_detection(boxs):
    for i in boxs:
        yield chunk_pb2.Detection(
            classID = i.classID,
            confidence = i.confidence,
            left = i.left,
            top = i.top,
            right = i.right,
            bottom = i.bottom,
            width = i.width,
            height = i.height,
            area = i.area,
            center_x = i.center_x,
            center_y = i.center_y)
        



class FileServer(chunk_pb2_grpc.FileServerServicer):
    def __init__(self):

        class Servicer(chunk_pb2_grpc.FileServerServicer):
            detections = 0
            def __init__(self):
                self.tmp_file_name = './server_save'

            def upload(self, request_iterator, context):
                self.detections = save_chunks_to_file(request_iterator, self.tmp_file_name)
                for i in self.detections:
                    print(i)
                return chunk_pb2.Reply(length=os.path.getsize(out_filename))

            def upload_box(self, request_iterator, context):
                boxs = save_chunk_to_file(request_iterator, self.temp_file_name)
                return get_detection(boxs)

            def download(self, request, context):
                if request.name:
                    #return get_file_chunks(self.tmp_file_name)
                    return get_file_chunks(out_filename)
            def download_detection(self, request, context):
                return response_detection()
            
            def alive(self, request, context):
                return chunk_pb2.Alive(heartbeat=request.heartbeat)

            def alive_stream(self, request, context):
                def response_message():
                    for i in self.detections:
                        response = chunk_pb2.Detection( classID = i.ClassID, confidence = i.Confidence, left = i.Left, top = i.Top, right = i.Right, bottom = i.Bottom, width = i.Width, height = i.Height, area = i.Area, center_x = i.Center[0], center_y = i.Center[1])
                        yield response
                return response_message()
  
   
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
        chunk_pb2_grpc.add_FileServerServicer_to_server(Servicer(), self.server)

    def start(self, port):
        self.server.add_insecure_port(f'[::]:{port}')
        self.server.start()

        try:
            while True:
                time.sleep(60*60*24)
        except KeyboardInterrupt:
            self.server.stop(0)
