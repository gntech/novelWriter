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

# Install novelWriter into the extracted AppDir
./squashfs-root/AppRun -m pip install --use-feature=in-tree-build .

# Copy icons to squashfs-root
cp setup/icons/scaled/icon-novelwriter-16.png squashfs-root/usr/share/icons/hicolor/16x16/apps/novelwriter.png
cp setup/icons/scaled/icon-novelwriter-32.png squashfs-root/usr/share/icons/hicolor/32x32/apps/novelwriter.png
cp setup/icons/scaled/icon-novelwriter-64.png squashfs-root/usr/share/icons/hicolor/64x64/apps/novelwriter.png
cp setup/icons/scaled/icon-novelwriter-128.png squashfs-root/usr/share/icons/hicolor/128x128/apps/novelwriter.png
cp setup/icons/scaled/icon-novelwriter-256.png squashfs-root/usr/share/icons/hicolor/256x256/apps/novelwriter.png
cp setup/icons/icon-novelwriter.svg squashfs-root/usr/share/icons/hicolor/scalable/apps/novelwriter.svg
cp setup/icons/scaled/icon-novelwriter-256.png squashfs-root/novelwriter.png

# Copy MIME type
cp setup/mime/x-novelwriter-project.xml squashfs-root/usr/share/mime/packages/

# Copy and Edit the desktop file
cp setup/novelwriter.desktop squashfs-root/
sed -i 's/%%exec%%/novelwriter/g' squashfs-root/novelwriter.desktop
cp squashfs-root/novelwriter.desktop squashfs-root/usr/share/applications/novelwriter.desktop

# Change AppRun so that it launches novelWriter
sed -i -e 's|/opt/python3.8/bin/python3.8|/usr/bin/novelWriter|g' ./squashfs-root/AppRun

# Remove Python 3.8 desktop file
rm squashfs-root/python3.8.10.desktop
rm squashfs-root/usr/share/applications/python3.8.10.desktop
rm squashfs-root/python.png
rm squashfs-root/usr/share/metainfo/python3.8.10.appdata.xml

# Remove unneeded parts. TODO: This may need to be fine-tuned.
find squashfs-root/opt/python3.8/lib/python3.8/site-packages/PyQt5/Qt/plugins/platforms/ -type f -not -name libqxcb.so -delete
rm -rf squashfs-root/opt/python3.8/lib/python3.8/site-packages/PyQt5/Qt/plugins/egldeviceintegrations
rm -rf squashfs-root/opt/python3.8/lib/python3.8/site-packages/PyQt5/Qt/plugins/{audio,gamepads,geometryloaders,geoservices,mediaservice,playlistformats,position,renderplugins,sceneparsers,sensorgestures,sensors,sqldrivers,texttospeech,wayland*,webview,xcbglintegrations}
rm -rf squashfs-root/opt/python3.8/lib/python3.8/site-packages/PyQt5/Qt/qml
rm squashfs-root/opt/python3.8/lib/python3.8/site-packages/PyQt5/Qt/lib/libQt5{Bluetooth,Concurrent,Designer,Help,Location,Multimedia,Network,Nfc,OpenGL,Positioning,Qml,Quick,RemoteObjects,Sensors,SerialPort,Sql,Test,WaylandClient,WebChannel,WebSockets,Xml}*

## Download linuxdeploy Convert back into an AppImage
wget https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage
chmod +x linuxdeploy-x86_64.AppImage
GLIBC=$(ldd --version | head -1 | awk '{print $5}')
ARCH=x86_64 VERSION=${VERSION}-glibc${GLIBC} ./linuxdeploy-x86_64.AppImage --appdir squashfs-root --output appimage 
