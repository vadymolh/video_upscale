Технологія трекінгу та масштабування рухомих об'єктів на полі бою


Для початку необхідно запустити командну строку.
У командній строці необхідно перейти до встановленої папки

Для роботи програми необхідно встановити наступні бібліотеки:
    - OpenCV, команда для встановлення pip install opencv-contrib-python
    - NumPy, команда для встановлення pip install numpy
    - Matplotlib, команда для встановлення pip install matplotlib

Для наступної бібліотеки dlib необхідно визначити, яка версія Python встановлена. В командній строці ввести python --version

Після цього необхідно встановити файл під відповідну версію Python, скориставшись одним з посилань:
    - Python 3.7 https://github.com/datamagic2020/Install-dlib/blob/main/dlib-19.19.0-cp37-cp37m-win_amd64.whl 
    - Python 3.8 https://github.com/datamagic2020/Install-dlib/blob/main/dlib-19.19.0-cp38-cp38-win_amd64.whl 
    - Python 3.9 https://github.com/datamagic2020/Install-dlib/blob/main/dlib-19.22.99-cp39-cp39-win_amd64.whl 
    - Python 3.10 https://github.com/datamagic2020/Install-dlib/blob/main/dlib-19.22.99-cp310-cp310-win_amd64.whl 

Програма точно працює при такій комбінації версій бібліотек із Python 3.10.6 :
    - OpenCV 4.5.4.58
    - NumPy 1.23.2
    - Matplotlib 3.6.2

Тепер необхідно в командній строці ввести pip install "шлях до встановленого файлу з розширенням .whl"


Запуск програми відбувається через командну строку.
Потрібно знаходитись в корінній папці і написати команду: python zone.py

Після обрання файлу, у відкритому вікні відео-програвача можемо лівою кнопкою миші виділяти зону зацікавлення

Для виходу з програми спочатку на вікні Upscaled натискаємо Esc, потім на основному вікні натискаємо Esc

Демонстрація роботи програми - https://youtu.be/CpMbI3NtLQI 
