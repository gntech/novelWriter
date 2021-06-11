#!/bin/sh

## This file builds an novelWriter AppImage from the current source.
## It is run automatically by Github actions workflow.
## The generated AppImage is uploaded as a Dist artifact.

if [ -d "squashfs-root" ] 
then
    rm -r squashfs-root
fi

rm -f *.AppImage

# Download an AppImage of Python 3. built for manylinux
wget https://github.com/niess/python-appimage/releases/download/python3.8/python3.8.10-cp38-cp38-manylinux1_x86_64.AppImage

# Extract this AppImage
chmod +x python*-manylinux1_x86_64.AppImage
./python*-manylinux1_x86_64.AppImage --appimage-extract

# Remove Python 3.8 desktop file
rm squashfs-root/python3.8.10.desktop
rm squashfs-root/usr/share/applications/python3.8.10.desktop
rm squashfs-root/python.png
rm squashfs-root/usr/share/metainfo/python3.8.10.appdata.xml

# Copy source files
mkdir -p squashfs-root/opt/novelWriter
cp -r nw squashfs-root/opt/novelWriter/
cp -r setup squashfs-root/opt/novelWriter/
cp CHANGELOG.md squashfs-root/opt/novelWriter/
cp LICENSE.md squashfs-root/opt/novelWriter/
cp README.md squashfs-root/opt/novelWriter/
cp novelWriter.py squashfs-root/opt/novelWriter/
cp setup.py squashfs-root/opt/novelWriter/
cp requirements.txt squashfs-root/opt/novelWriter/

# Install novelWriter into the extracted AppDir
./squashfs-root/AppRun -m pip install -r squashfs-root/opt/novelWriter/requirements.txt

# Copy and Edit the desktop file
cp setup/novelwriter.desktop squashfs-root/
sed -i 's/%%exec%%/novelwriter/g' squashfs-root/novelwriter.desktop
cp squashfs-root/novelwriter.desktop squashfs-root/usr/share/applications/novelwriter.desktop

# Copy MIME type
cp setup/mime/x-novelwriter-project.xml squashfs-root/usr/share/mime/packages/

# Change AppRun so that it launches novelWriter
sed -i -e 's|/opt/python3.8/bin/python3.8|/usr/bin/novelWriter|g' ./squashfs-root/AppRun

## Download linuxdeploy
wget https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage
chmod +x linuxdeploy-x86_64.AppImage
./linuxdeploy-x86_64.AppImage --appdir squashfs-root

# Copy icons to squashfs-root
cp setup/icons/scaled/icon-novelwriter-16.png squashfs-root/usr/share/icons/hicolor/16x16/apps/novelwriter.png
cp setup/icons/scaled/icon-novelwriter-32.png squashfs-root/usr/share/icons/hicolor/32x32/apps/novelwriter.png
cp setup/icons/scaled/icon-novelwriter-64.png squashfs-root/usr/share/icons/hicolor/64x64/apps/novelwriter.png
cp setup/icons/scaled/icon-novelwriter-128.png squashfs-root/usr/share/icons/hicolor/128x128/apps/novelwriter.png
cp setup/icons/scaled/icon-novelwriter-256.png squashfs-root/usr/share/icons/hicolor/256x256/apps/novelwriter.png
cp setup/icons/novelwriter.svg squashfs-root/usr/share/icons/hicolor/scalable/apps/novelwriter.svg
cp setup/icons/scaled/icon-novelwriter-256.png squashfs-root/novelwriter.png

# Remove unneeded parts. TODO: This may need to be fine-tuned.
find squashfs-root/opt/python3.8/lib/python3.8/site-packages/PyQt5/Qt/plugins/platforms/ -type f -not -name libqxcb.so -delete
rm -rf squashfs-root/opt/python3.8/lib/python3.8/site-packages/PyQt5/Qt/plugins/egldeviceintegrations
rm -rf squashfs-root/opt/python3.8/lib/python3.8/site-packages/PyQt5/Qt/plugins/{audio,gamepads,geometryloaders,geoservices,mediaservice,playlistformats,position,renderplugins,sceneparsers,sensorgestures,sensors,sqldrivers,texttospeech,wayland*,webview,xcbglintegrations}
rm -rf squashfs-root/opt/python3.8/lib/python3.8/site-packages/PyQt5/Qt/qml
rm squashfs-root/opt/python3.8/lib/python3.8/site-packages/PyQt5/Qt/lib/libQt5{Bluetooth,Concurrent,Designer,Help,Location,Multimedia,Network,Nfc,OpenGL,Positioning,Qml,Quick,RemoteObjects,Sensors,SerialPort,Sql,Test,WaylandClient,WebChannel,WebSockets,Xml}*
#rm squashfs-root/opt/python3.8/lib/python3.8/site-packages/PyQt5/Qt5/lib/opengl32sw.dll
rm squashfs-root/opt/python3.8/lib/python3.8/site-packages/PyQt5/Qt5/lib/*Qt*DBus*
rm squashfs-root/opt/python3.8/lib/python3.8/site-packages/PyQt5/Qt5/lib/*Qt*Designer*
rm squashfs-root/opt/python3.8/lib/python3.8/site-packages/PyQt5/Qt5/lib/*Qt*Network*
rm squashfs-root/opt/python3.8/lib/python3.8/site-packages/PyQt5/Qt5/lib/*Qt*OpenGL*
rm squashfs-root/opt/python3.8/lib/python3.8/site-packages/PyQt5/Qt5/lib/*Qt*Qml*
rm squashfs-root/opt/python3.8/lib/python3.8/site-packages/PyQt5/Qt5/lib/*Qt*QmlModels*
rm squashfs-root/opt/python3.8/lib/python3.8/site-packages/PyQt5/Qt5/lib/*Qt*QmlWorkerScript*
rm squashfs-root/opt/python3.8/lib/python3.8/site-packages/PyQt5/Qt5/lib/*Qt*Quick*
rm squashfs-root/opt/python3.8/lib/python3.8/site-packages/PyQt5/Qt5/lib/*Qt*Quick3D*
rm squashfs-root/opt/python3.8/lib/python3.8/site-packages/PyQt5/Qt5/lib/*Qt*Quick3DAssetImport*
rm squashfs-root/opt/python3.8/lib/python3.8/site-packages/PyQt5/Qt5/lib/*Qt*Quick3DRender*
rm squashfs-root/opt/python3.8/lib/python3.8/site-packages/PyQt5/Qt5/lib/*Qt*Quick3DRuntimeRender*
rm squashfs-root/opt/python3.8/lib/python3.8/site-packages/PyQt5/Qt5/lib/*Qt*Quick3DUtils*
rm squashfs-root/opt/python3.8/lib/python3.8/site-packages/PyQt5/Qt5/lib/*Qt*QuickControls2*
rm squashfs-root/opt/python3.8/lib/python3.8/site-packages/PyQt5/Qt5/lib/*Qt*QuickParticles*
rm squashfs-root/opt/python3.8/lib/python3.8/site-packages/PyQt5/Qt5/lib/*Qt*QuickShapes*
rm squashfs-root/opt/python3.8/lib/python3.8/site-packages/PyQt5/Qt5/lib/*Qt*QuickTemplates2*
rm squashfs-root/opt/python3.8/lib/python3.8/site-packages/PyQt5/Qt5/lib/*Qt*QuickTest*
rm squashfs-root/opt/python3.8/lib/python3.8/site-packages/PyQt5/Qt5/lib/*Qt*QuickWidgets*
rm squashfs-root/opt/python3.8/lib/python3.8/site-packages/PyQt5/Qt5/lib/*Qt*Sql*

## Convert back into an AppImage
GLIBC=$(ldd --version | head -1 | awk '{print $5}')
ARCH=x86_64 VERSION=${VERSION}-glibc${GLIBC} ./linuxdeploy-x86_64.AppImage --appdir squashfs-root --output appimage 
