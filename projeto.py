import cv2  # Importa a biblioteca OpenCV para processamento de imagem
import numpy as np  # Importa a biblioteca numpy para operações numéricas
import math  # Importa a biblioteca math para operações matemáticas

cap = cv2.VideoCapture(0)  # Inicia a captura de vídeo a partir da câmera (índice 0)

while True:  # Inicia um loop infinito para processar os quadros do vídeo
    try:
        ret, frame = cap.read()  # Lê o quadro atual da captura de vídeo
        frame = cv2.flip(frame, 1)  # Espelha horizontalmente o quadro
        kernel = np.ones((3, 3), np.uint8)  # Cria um kernel (matriz) para operações de dilatação

        # Define a região de interesse (ROI) para análise
        roi = frame[100:300, 100:300]  # Seleciona a ROI (uma área quadrada) no quadro

        # Desenha um retângulo verde ao redor da ROI no quadro principal
        cv2.rectangle(frame, (100, 100), (300, 300), (0, 255, 0), 0)

        # Converte a ROI do espaço de cores BGR para HSV
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        # Define os limites inferior e superior para a cor da pele em HSV
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)

        # Cria uma máscara para isolar a cor da pele na ROI
        mask = cv2.inRange(hsv, lower_skin, upper_skin)

        # Dilata a máscara para preencher áreas escuras
        mask = cv2.dilate(mask, kernel, iterations=4)

        # Aplica um blur gaussiano na máscara para suavizar a imagem
        mask = cv2.GaussianBlur(mask, (5, 5), 100)

        # Encontra os contornos na máscara
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Encontra o contorno com a maior área (presumivelmente a mão)
        cnt = max(contours, key=lambda x: cv2.contourArea(x))

        # Aproxima o contorno para um polígono
        epsilon = 0.0005 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)

        # Cria um casco convexo ao redor do contorno
        hull = cv2.convexHull(cnt)

        # Calcula a área do casco convexo e do contorno
        areahull = cv2.contourArea(hull)
        areacnt = cv2.contourArea(cnt)

        # Calcula a razão entre a área do casco convexo e a área do contorno
        arearatio = ((areahull - areacnt) / areacnt) * 100

        # Encontra defeitos de convexidade no casco convexo em relação ao contorno aproximado
        hull = cv2.convexHull(approx, returnPoints=False)
        defects = cv2.convexityDefects(approx, hull)

        # Inicializa o contador de defeitos
        l = 0

        # Define a região de interesse
        for i in range(defects.shape[0]):
            s, e, f, _ = defects[i, 0]
            start = tuple(approx[s][0])
            end = tuple(approx[e][0])
            far = tuple(approx[f][0])

            # Calcula os comprimentos dos lados do triângulo formado pelos pontos do defeito
            a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
            b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
            c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
            s = (a + b + c) / 2
            ar = math.sqrt(s * (s - a) * (s - b) * (s - c))

            # Calcula a distância entre o ponto do defeito e o casco convexo
            d = (2 * ar) / a

            # Calcula o ângulo no ponto do defeito usando a lei dos cossenos
            angle = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 57

            # Ignora ângulos maiores que 90 graus e defeitos muito próximos (provavelmente ruído)
            if angle <= 90 and d > 30:
                l += 1
                cv2.circle(roi, far, 3, [255, 0, 0], -1)

            # Desenha linhas ao redor da mão
            cv2.line(roi, start, end, [0, 255, 0], 2)

        l += 1  # Incrementa o contador de defeitos

        # Define a fonte para exibir o texto
        font = cv2.FONT_HERSHEY_SIMPLEX

        # Determina a ação com base no número de defeitos
        if l == 1:
            if areacnt < 2000:  # Se a área do contorno for pequena, exibe "Esperando dados"
                cv2.putText(frame, 'Esperando dados', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
            else:
                executado = False
                if arearatio < 12 and not executado:  # Se a razão da área for menor que 12, exibe "0 = Navegador"
                    cv2.putText(frame, '0 = Navegador', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
                    # os.system("start Chrome.exe --window-size=800,600")
                    executado = True
                elif arearatio < 17.5:  # Se a razão da área for menor que 17.5, exibe uma mensagem vazia
                    cv2.putText(frame, '', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
                    # os.system("start Arduino IDE.exe")
                else:  # Caso contrário, exibe "1 = Word"
                    cv2.putText(frame, '1 = Word', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
                    # os.system("start WINWORD.EXE --window-size=600,400")
        elif l == 2:  # Se houver dois defeitos, exibe "2 = Excel"
            cv2.putText(frame, '2 = Excel', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
            # os.system("start Excel.exe --window-size=600,400")
        elif l == 3:
            if arearatio < 27:  # Se a razão da área for menor que 27, exibe "3 = Power Point"
                cv2.putText(frame, '3 = Power Point', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
                # os.system("start POWERPNT.EXE --window-size=600,400")
            else:  # Caso contrário, exibe "ok"
                cv2.putText(frame, 'ok', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
        elif l == 4:  # Se houver quatro defeitos, exibe uma mensagem vazia
            cv2.putText(frame, '', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
            # os.system("start firefox.exe")
        elif l == 5:  # Se houver cinco defeitos, exibe uma mensagem vazia
            cv2.putText(frame, '', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
            # os.system("start Spyder.launch.pyw")
        elif l == 6:  # Se houver seis defeitos, exibe "reposition"
            cv2.putText(frame, 'reposition', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
        else:  # Caso contrário, exibe "reposition"
            cv2.putText(frame, 'reposition', (10, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)

        # Exibe as janelas de visualização
        cv2.imshow('mask', mask)  # Mostra a máscara
        cv2.imshow('frame', frame)  # Mostra o quadro original com as anotações

    except Exception as e:
        print("Erro:", e)
        pass

    k = cv2.waitKey(5) & 0xFF  # Espera por uma tecla ser pressionada por 5 milissegundos
    if k == 27:  # Se a tecla ESC for pressionada, sai do loop
        break

cv2.destroyAllWindows()  # Fecha todas as janelas abertas pelo OpenCV
cap.release()  # Libera a captura de vídeo
