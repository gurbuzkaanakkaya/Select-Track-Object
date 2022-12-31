import cv2
import time
from PIL import Image
from mss import mss
import keyboard
import serial
import struct 
from collections import deque
import matplotlib.pyplot as plt



import warnings
warnings.filterwarnings("ignore")


# %% Servo motor kontrolü için servoyu bağlanılan arduino ile program arasında seri iletişim başlatır
seri = serial.Serial("COM3",9600)   # ########################### Arduino ile çalışmak için aç/kapa #
time.sleep(2)                       # ########################### Arduino ile çalışmak için aç/kapa #


# Sözlük 1
OPENCV_OBJECT_TRACKERS = {"CSRT"      : cv2.legacy.TrackerCSRT_create,
		                  "KCF"       : cv2.legacy.TrackerKCF_create,
		                  "Boosting"  : cv2.legacy.TrackerBoosting_create,
		                  "Mil"       : cv2.legacy.TrackerMIL_create,
		                  "TLD"       : cv2.legacy.TrackerTLD_create,
		                  "MedianFlow": cv2.legacy.TrackerMedianFlow_create,
		                  "Mosse"     : cv2.legacy.TrackerMOSSE_create}

# Sözlük 2
TRACKERS_KEYS = { "1"    : "CSRT",
                  "2"    : "KCF",
                  "3"    : "Boosting",
                  "4"    : "Mil",
                  "5"    : "TLD",
                  "6"    : "MedianFlow",
                  "7"    : "Mosse"}

tracker_name = ["Boosting"] # Sözlük yapısı boş bırakılamıyor, bu sebepten default bir anahtar oluşturuldu
tracker = OPENCV_OBJECT_TRACKERS[tracker_name[0]]() # Track (Takip) işleminin gerçekleştirileceği algoritmanın temsili
choice = 0

print('''
      1. CSRT
      2. KCF
      3. Boosting
      4. Mil
      5. TLD
      6. MedianFlow
      7. Mosse
   ''')
   
# Program başladığında algoritmalar arasından seçim yapılmasını sağlayacak olan fonksiyon
def algoritma(TRACKERS_KEYS, OPENCV_OBJECT_TRACKERS):
    choice = input("Takip algoritmasını sec (1-7)   : ") 
    keys = TRACKERS_KEYS.keys() 
    if choice in keys: # Eğer klavyeden girilen değer sözlüğün anahtarları arasında ise ;
        tracker_name.append(TRACKERS_KEYS[choice]) # 2. sözlükten anahtar değerine göre alınan ve aslında 1. sözlüğün anahtarı olan değer
        tracker_name.remove(tracker_name[0]) # Performansı etkilememesi için listeye 1 değer eklendikten sonra önceki değer silinir
        print(choice, tracker_name) 
        tracker = OPENCV_OBJECT_TRACKERS[tracker_name[len(tracker_name)-1]]() 
        
    else: # Eğer klavyeden girilen değer 2. sözlüğün anahtarları arasında değilse
        print("! Gecersiz secim ! Varsayilan Takip Algoritmasi {}".format(tracker_name))
    print("Cikis icin 'q'")

algoritma(TRACKERS_KEYS, OPENCV_OBJECT_TRACKERS) 

cap = cv2.VideoCapture(1) # kameradan frame yakalama ve bunları "cap" de depolama
                          # (x) ; Dahili kamera icin x = 0 ; Harici kamera icin x = COMx
#Cascade
# cap.set(3,frameWidth)
# cap.set(4,frameHeight)

# def empty(a): pass

xlis=[90] # Motorların başlangıç açı değeri 
ylis=[90] # Motorların başlangıç açı değeri 


success, img = cap.read() # "cap" içine frame depolanıyorsa "success" ve "img" değeri döndürür

#%% Cascade
# cv2.namedWindow("Sonuc")
# cv2.resizeWindow("Sonuc",frameWidth,frameHeight +100)
# cv2.createTrackbar("Scale","Sonuc", 400,1000,empty)
# cv2.createTrackbar("Neighbor","Sonuc",4,50,empty)

# cascade = cv2.CascadeClassifier("cascade.xml")

    
#%% Obje sınırlarını belirtmek / objeyi kutucuk içerisine alma fonksiyonu
def drawBox(img, bbox): # Seçilen objenin sınırlarını, merkez noktasını ve aldığımız framelerin merkez noktasını belirtmek için
    x, y, w, h = int(bbox[0]),int(bbox[1]),int(bbox[2]),int(bbox[3])
    center_x = int(x+w/2) # Objenin x eksenine göre merkezi
    center_y = int(y+h/2) # Objenin y eksenine göre merkezi
    
    cv2.rectangle(img, (x,y), ((x+w), (y+h)), (255,0,255), 3, 1) # A noktasından B noktasına (x,x,x) renginde dikdörtgen çiz ### Objenin sınırları 
    cv2.circle(img, (center_x, center_y), 2,(0,0,255),-1) # Obje merkezine (x,x,x) renginde çember/nokta çiz
    cv2.putText(img,"Object At :",(10,15),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
    cv2.putText(img,"X ="+str(center_x),(140,15),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2) 
    cv2.putText(img,"Y ="+str(center_y),(240,15),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
    cv2.putText(img,"Algoritma : "+tracker_name[0],(400,15),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
    cv2.line(img, (320, 240), (center_x, center_y), (255,0,255), 1) # Ana Frame merkezinden obje merkez noktasına (x,x,x) renginde çizgi çekmek için;
# %% Servo motor kontrolü için oluşturulan fonksiyon
def servo(bbox): # Servo motorlarına gönderilecek olan komutlar
    x, y, w, h = int(bbox[0]),int(bbox[1]),int(bbox[2]),int(bbox[3])
    center_x = int(x+w/2)
    center_y = int(y+h/2)
    print(" ")
    print(bbox)
    
    
    
    # Ana Frame ekranda merkez noktası (320, 240), o halde kamera merkezini obje merkezine yakınsak oranlarda ayarlayabilmek için
    if center_x < 300 and center_x > 340 : # Obje x merkezi ana frame x ekseni üstünde 300-340 arasında ise son konum değeri kalsın
        print("kilitlendi_x")
        xlis.append(xlis[len(xlis)-1]) # Bulunduğu açı kaç derecede ise listeye onu ekle 
        xlis.remove(xlis[0]) # İlk elemanı/öncekini elemanı sil
        

    elif center_x > 340: # Obje kameranın solunda ise
        print("sag")
        xlis.append(xlis[len(xlis)-1]-1) # Motoru sola döndürmek için bulunduğu son konum açısını küçült 
        xlis.remove(xlis[0])    

    elif center_x < 300: # Obje kameranın sağında ise
        print("sol")
        xlis.append(xlis[len(xlis)-1]+1) # Motoru sağa döndürmek için bulunduğu son konum açısını küçült
        xlis.remove(xlis[0])
    
        
    xdeg=xlis[len(xlis)-1] # Listenin son elemanının değerini "xdeg" değişkenine ayarla
    
    if center_y < 220 and center_y > 260:
        print("kilitlendi_y")
        ylis.append(ylis[len(ylis)-1])
        ylis.remove(ylis[0])

    elif center_y > 260:
        print("yukari")
        ylis.append(ylis[len(ylis)-1]+1)
        ylis.remove(ylis[0])

    elif center_y < 220:
        print("asagi")
        ylis.append(ylis[len(ylis)-1]-1)
        ylis.remove(ylis[0])

    ydeg=ylis[len(ylis)-1]
    
    
    # Seri iletişimde motora gönderilen PWM sinyali 0-255 arasında olduğundan 0 dan az 255 den fazla değeri döndürülmeli
    # Servo motorların dönüş açı sınırları 0-180 derece olduğu için 0 ve 180 derece sınırlarını aşamazlar
    # Bu nedenle oluşturulan listelerdeki son konumlar 0 dan düşük 180 den fazla olmamalı :
    if xdeg >= 180:
        xlis.append(xlis[len(xlis)-1]-1)
        xlis.remove(xlis[0])
        print("x ekseni sınır acısı 180 derece")
    elif xdeg <= 0:
        xlis.append(xlis[len(xlis)-1]+1)
        xlis.remove(xlis[0])
        print("x ekseni sınır acısı 0 derece")
    if ydeg >= 180:
        ylis.append(ylis[len(ylis)-1]-1)
        ylis.remove(ylis[0])
        print("y ekseni sınır acısı 180 derece")
    elif ydeg <= 0:
        ylis.append(ylis[len(ylis)-1]+1)
        ylis.remove(ylis[0])
        print("y ekseni sınır acısı 0 derece")

    
    print(xdeg,ydeg) # Döndürülen dereceler
    cv2.putText(img,"derece X ="+str(xdeg),(50,465),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
    cv2.putText(img,"derece Y ="+str(ydeg),(250,465),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)   
    
    seri.write(struct.pack('>BBB', xdeg, ydeg)) ############################### Arduino ile çalışmak için aç/kapa 

# %% "success" değeri döndürüldüğü sürece  kameradan görüntü alma ;
while True:
    timer = cv2.getTickCount()
    success, img = cap.read()
    success, bbox = tracker.update(img) 
    
    print(img.shape) # Ana frame boyutunu/pixel miktarını ve buna bağlı olarak koordinatları öğrenmek için
    
    center = cv2.circle(img, (320, 240), 2,(0,0,255),-1) # Ana frame merkezine nokta/çember çizdirme
    
    if success:
        drawBox(img, bbox) # Obje sınırlarını belirtme fonksiyonu ^
        servo(bbox) # Servo motor kontrolü için gerekli talimatların döndürüldüğü fonksiyon 

        
#Cascade         
        # gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        # #detection parameters
        # scaleVal = 1 + (cv2.getTrackbarPos("Scale","Sonuc")/1000)
        # neighbor = (cv2.getTrackbarPos("Neighbor","Sonuc"))
        # #detection
        # rects = cascade.detectMultiScale(gray,scaleVal,neighbor)
        
        # for(x,y,w,h) in rects:
        #     cv2.rectangle(img,(x,y),(x+w,y+h),color,3)
        #     cv2.putText(img,objectName,(x,y-5),cv2.FONT_HERSHEY_COMPLEX_SMALL,1,color,2)
        
    else:
        cv2.putText(img,"Nesne Secmek icin : 't'",(10,15),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
        cv2.putText(img,"Cikis Yapmak icin : 'q'",(10,45),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
    
    cv2.imshow("Tracking",img) # Frame görselleştirme
    
#Cascade
    # cv2.imshow("Sonuc",img)
    
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord("t"): # "t" tuşuna basıldığında seçme işlemi talimatlarını izle
        bbox = cv2.selectROI("Tracking", img, False)
        tracker.init(img,bbox) # Seçilen kısım img ve bbox değerini döndürecek
        

    
    if cv2.waitKey(1) & 0xFF == ord("q"): break

        
    
    elif key == ord("q"): # "q" tuşuna basıldığında döngüyü kır
        break
# %% Döngü bittiyse tüm pencereleri kapa
cap.release()
cv2.destroyAllWindows()
