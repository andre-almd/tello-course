#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 22:21:28 2021

@author: andre-itv
"""

import keyPressModule as kp

from djitellopy import tello
import time
import cv2
import numpy as np
import os

# Variável para testar decolagem e pouso
voando = False
run = True

# Inicia o módulo de capturar o teclado com pygame
kp.init()

# Cria o objeto tello paracontrolar o drone
me = tello.Tello()

# Conecta com o drone e checa nível de bateria
me.connect()
print(f'Battery: {me.get_battery()}')

# Cria a variável para salvar as imagens
global img

# Inicia o steam da câmera
me.streamon()

out = cv2.VideoWriter('output.avi', cv2.VideoWriter_fourcc(*'MJPG'), 5, (640,480))


# inia os dados para o yolo
#**************************************************************************************
# constantes do modelo
CONFIDENCE_MIN = 0.4
NMS_THRESHOLD = 0.2
MODEL_BASE_PATH = "yolo"

# extrair os nomes das classes a partir do arquivo
print("[+] Carregando labels das classes treinadas...")
with open(os.path.sep.join([MODEL_BASE_PATH, 'coco.names'])) as f:
    labels = f.read().strip().split("\n")

    # gerar cores únicas para cada label
    np.random.seed(42)
    colors = np.random.randint(0, 255, size=(len(labels), 3), dtype="uint8")


# carregar o modelo treinado YOLO (c/ COCO dataset)
print("[+] Carregando o modelo YOLO treinado no COCO dataset...")
net = cv2.dnn.readNetFromDarknet(
    os.path.sep.join([MODEL_BASE_PATH, 'yolov4.cfg']),
    os.path.sep.join(['../../darknet', 'yolov4.weights']))

# extrair layers não conectados da arquitetura YOLO
ln = net.getLayerNames()
ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]
#**************************************************************************************



# Função para executar o yolo
#**************************************************************************************
def detect(frame):
    
    (H, W) = frame.shape[:2]
    
    # construir um container blob e fazer uma passagem (forward) na YOLO
    blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    layer_outputs = net.forward(ln)

    # criar listas com boxes, nível de confiança e ids das classes
    boxes = []
    confidences = []
    class_ids = []

    for output in layer_outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            # filtrar pelo threshold da confiança
            if confidence > CONFIDENCE_MIN:
                box = detection[0:4] * np.array([W, H, W, H])
                (center_x, center_y, width, height) = box.astype("int")

                x = int(center_x - (width / 2))
                y = int(center_y - (height / 2))

                boxes.append([x, y, int(width), int(height)])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    # eliminar ruído e redundâncias aplicando non-maxima suppression
    new_ids = cv2.dnn.NMSBoxes(boxes, confidences,CONFIDENCE_MIN, NMS_THRESHOLD)
    if len(new_ids) > 0:
        for i in new_ids.flatten():
            (x, y) = (boxes[i][0], boxes[i][1])
            (w, h) = (boxes[i][2], boxes[i][3])

            # plotar retângulo e texto das classes detectadas no frame atual
            color_picked = [int(c) for c in colors[class_ids[i]]]
            cv2.rectangle(frame, (x, y), (x + w, y + h), color_picked, 1)
            text = "{}: {:.4f}".format(labels[class_ids[i]], confidences[i])
            cv2.putText(frame, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.3, color_picked, 1)
            
    return frame
#**************************************************************************************





# Função para os comandos de voo do drone
def getKeyboardInput():
    
    # lr: left - rigth
    # fb: forward - backward
    # ud: up - down
    # yv: yaw velocity
    
    lr, fb, ud, yv = 0, 0, 0, 0
    speed = 30
    
    global voando
    global run
    
    # Captura dos movimentos
    if kp.getKey('LEFT'):
        lr = -speed
    elif kp.getKey('RIGHT'):
        lr = speed
        
    if kp.getKey('UP'):
        fb = speed
    elif kp.getKey('DOWN'):
        fb = -speed
        
    if kp.getKey('w'):
        ud = speed
    elif kp.getKey('s'):
        ud = -speed
        
    if kp.getKey('a'):
        yv = -speed
    elif kp.getKey('d'):
        yv = speed
        
    # Captura das teclas de takeoff e land
    if kp.getKey('e'):
        if voando == False:
            print('decolando')
            me.takeoff()
            voando = True
        else: pass
                
        
    if kp.getKey('q'):
        if voando == True:
            print('pousando...')
            me.land()
            voando = False
            out.release()
            run = False
        else: pass
        
    # Captura da tecla de salvar foto
    if kp.getKey('z'):
        cv2.imwrite(f'Resources/Images/{time.time()}.jpg', img)
        time.sleep(0.3)
        
    return [lr, fb, ud, yv]



# Loop de execução principal
while run:
    
    # Captura as teclas
    vals = getKeyboardInput()
    
    # Envia comandos de voo parao drone
    me.send_rc_control(vals[0], vals[1], vals[2], vals[3])
    
    # Captra o frame
    img = me.get_frame_read().frame
    img = cv2.resize(img, (640,480))
    
    img = detect(img)
    
    #time.sleep(0.01)
    
    out.write(img)
    
    cv2.imshow('image from Drone', img)
    
    if cv2.waitKey(1) & 0xFF == ord('k'):
        #me.land()
        #time.sleep(0.1)
        #out.release()
        break
    
cv2.destroyAllWindows()
out.release()