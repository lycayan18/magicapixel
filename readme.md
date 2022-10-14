# Magica Pixel
## Pixel-art редактор
#### Проект для Лицея Академии Яндекса

# Сборка и запуск проекта
### magicautils
Для начала убедитесь, что у вас установлены инструменты сборки ```cpython```.
Перейдите в директорию ```magicautils```, откройте файл ```setup.py``` и модифицируйте строчку:
```python
ext_modules=[Extension("magicautils", sources=["src/clamp.cpp", "src/pixelutils.cpp", "src/canvas.cpp", "src/rendercanvases.cpp", "src/main.cpp"], extra_compile_args=["/std:c++20"])])
```
За место ```/std:c++20``` вам нужно подставить флаг, включающий C++20 на вашем компиляторе.
Для GCC 9.x и выше:
```python
ext_modules=[Extension("magicautils", sources=["src/clamp.cpp", "src/pixelutils.cpp", "src/canvas.cpp", "src/rendercanvases.cpp", "src/main.cpp"], extra_compile_args=["--std=c++2a"])])
```
Для GCC 8.x:
```python
ext_modules=[Extension("magicautils", sources=["src/clamp.cpp", "src/pixelutils.cpp", "src/canvas.cpp", "src/rendercanvases.cpp", "src/main.cpp"], extra_compile_args=["--std=c++20"])])
```
Для MSVC:
```python
ext_modules=[Extension("magicautils", sources=["src/clamp.cpp", "src/pixelutils.cpp", "src/canvas.cpp", "src/rendercanvases.cpp", "src/main.cpp"], extra_compile_args=["/std:c++20"])])
```
Далее выполните следующую команду:
```bash
python3 setup.py install
```
По окончанию сборки появится папка ```build```, а в ней папка ```lib.[система]-[платформа]-[версия python]```. В этой папке будет лежать файл ```magicautils.cp[версия python]-[система]_[платформа].[pyd|so]```. Его нужно перенести в корневую папку программы ( где распологается ```main.py``` ).

#### Исправление проблем
На компиляторах **GCC** ( под *linux* ) может возникать следующая проблема:
```
fatal error: Python.h: No such file or directory
```
Это означает, что у вас не установлены инструменты разработчика под ```cpython```.
Для ```apt``` ( *Ubuntu*, *Debian* ):
```bash
sudo apt-get install python3-dev  # первый вариант
sudo apt-get install python[версия Python]-dev  # или с указанием версии
# Пример: sudo apt-get install python3.10-dev
```
Для ```yum``` ( *CentOS*, *RHEL* ):
```bash
sudo yum install python3-devel  # первый вариант
sudo yum install python[версия Python]-devel  # или с указанием версии
# Пример: sudo yum install python3.10-devel
```
Для ```dnf``` ( *Fedora* ):
```bash
sudo dnf install python3-devel  # первый вариант
sudo dnf install python[версия Python]-devel  # или с указанием версии
# Пример: sudo dnf install python3.10-devel
```
Для ```zypper``` ( *OpenSUSE* ):
```bash
sudo zypper in python3-devel
```
## Запуск проекта
Для запуска проекта достаточно просто запустить ```main.py```:
```bash
python3 main.py
# или с указанием версии, если вдруг собирали под другую версию Python
python3.10 main.py  # за место 3.10 подставьте версию Python, под которую собирали
```
##### Важно: проект нужно запускать той же версией Python, под которую вы собирали *magicautils*.