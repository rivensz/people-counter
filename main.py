import cv2

# Função pra encontrar o centro do contorno feito em volta do objeto se movendo
def center(x, y, w, h):
    x1 = int(w / 2)
    y1 = int(h / 2)
    cx = x + x1
    cy = y + y1
    return cx, cy

# Fonte do vídeo a ser analisado 
cap = cv2.VideoCapture('1.mp4')

# Background Subtractor do OpenCV
fgbg = cv2.createBackgroundSubtractorMOG2()

# posL = posição da linha na vertical
posL = 150
# offset = número de pixels pra cima ou pra baixo pra considerar a contagem
offset = 30

# xy1 e xy2 = posição da linha
xy1 = (20, posL)
xy2 = (300, posL)

# Cache das posições pra seguir as pessoas/tracking do objeto
# Vai ser um array de arrays com as posições das pessoas, as posições que a pessoa (ID) esteve
detects = []

# total de pessoas
total = 0

# up = pessoas que subiram
up = 0
# down = pessoas que desceram
down = 0

# Loop para ler o vídeo
while 1:
    
    ret, frame = cap.read()

    # Transformando vídeo para escala de cinza
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Obtendo a máscara do frame
    # Máscara = diferença na imagem do frame anterior para o frame atual.
    # Assim detectamos o que está se movendo.
    fgmask = fgbg.apply(gray)

    # Limpando a sujeira do fgmask usando a função threshold
    retval, th = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)

    # Removendo mais a sujeira usando Morphological Transformations.
    # Precisamos iniciar um kernel (matriz)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

    # Usando a função opening
    opening = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel, iterations = 2)

    # Aumentando/deixando mais nítidos os objetos com a função dilation
    dilation = cv2.dilate(opening,kernel,iterations = 8)

    # Completando as formas do objeto dilatado usando closing
    closing = cv2.morphologyEx(dilation, cv2.MORPH_CLOSE, kernel, iterations = 8)

    # Criando contornos em volta das imagens/frames presentes no closing
    contours, hierarchy = cv2.findContours(closing, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Desenhando a linha da contagem
    # Essa linha serve pra saber a direção que a pessoa foi
    cv2.line(frame, xy1, xy2, (255, 0, 0), 3)
    # Linhas do offset
    # O contador só sobe/desce se a pessoa passar de todas as linhas, pra evitar bugs etc
    cv2.line(frame,(xy1[0],posL-offset),(xy2[0],posL-offset),(255,255,0),2)
    cv2.line(frame,(xy1[0],posL+offset),(xy2[0],posL+offset),(255,255,0),2)

    # Variável pra contar os IDs
    i = 0

    # Percorrer o array de contornos
    for cnt in contours:

        # x e y = onde o contorno começa
        # w e h = height e width
        (x, y, w, h) = cv2.boundingRect(cnt)
        area = cv2.contourArea(cnt)

        # Esse if é pra decidir se o tamanho do objeto é suficiente pra ser reconhecido como pessoa pra contagem
        if int(area) > 3000:

            # Usando a função center pra saber o centro do contorno
            centro = center(x, y, w, h)

            # Escrever o ID
            cv2.putText (frame, str(i), (x+5, y+5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
            # Desenhar o contorno
            cv2.rectangle(frame, (x,y), (x+w, y+h), (0, 255, 0), 2)
            # Desenhando o círculo no centro do contorno
            cv2.circle(frame, centro, 4, (0, 0,255), -1)

            # Se o tamanho de detects for menor ou igual a i (a quantidade de IDs), a posição do ID é adicionada na lista
            if len(detects) <= i:
                detects.append([])
            # Se o centro for maior que o offset e menor que a posição + offset, damos o append
            # O contador só considera a pessoa pra contagem dentro do espaço do offset (pra evitar alguns bugs)
            if centro[1] > posL-offset and centro[1] < posL+offset:
                detects[i].append(centro)
            else:
                detects[i].clear()

            # Incrementando o contador de ID
            i += 1
            
        # Se não tiver nenhuma pessoa na tela, limpamos a lista das detecções
        if len(contours) == 0:
            detects.clear()
        # Se tiver algo no detects:
        else:
            for detect in detects:
                # For (count, line) in enumerate(detect), pra cada item em detects
                for (c, l) in enumerate(detect):
                    
                    # if pra saber se a pessoa subiu e aumentar o contador
                    if detect[c-1][1] < posL and l[1] > posL :
                        detect.clear()
                        up+=1
                        total+=1
                        cv2.line(frame,xy1,xy2,(0,255,0),5)
                        continue

                    # if pra saber se a pessoa desceu e aumentar o contador
                    if detect[c-1][1] > posL and l[1] < posL:
                        detect.clear()
                        down+=1
                        total+=1
                        cv2.line(frame,xy1,xy2,(0,0,255),5)
                        continue

                    if c > 0:
                        cv2.line(frame,detect[c-1], l, (0, 0, 255), 1)

    # print(detects)
    cv2.putText(frame, "TOTAL: "+str(total), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255),2)
    cv2.putText(frame, "SUBINDO: "+str(up), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0),2)
    cv2.putText(frame, "DESCENDO: "+str(down), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255),2)

            

    # CASO QUEIRA VER COMO FICA CADA ETAPA DO PROCESSO DE REMOÇÃO DO FUNDO E EDIÇÃO DA IMAGEM DO VÍDEO, 
    # DESCOMENTE AS LINHAS ABAIXO:

    # cv2.imshow("gray", gray)
    # cv2.imshow("fgmask", fgmask)
    # cv2.imshow("th", th)
    # cv2.imshow("opening", opening)
    # cv2.imshow("dilation", dilation)

    # Exibindo o vídeo original (frame) e o editado (closing)
    cv2.imshow("frame", frame)
    cv2.imshow("closing", closing)

    # Pressione a tecla Q para parar o programa
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()