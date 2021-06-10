#!/bin/sh

if [ -d "AppDir" ] 
then
    rm -r AppDir
fi
if [ ! -d "out" ] 
then
    mkdir out
fi

## Download linuxdeploy
wget https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage
chmod +x linuxdeploy-x86_64.AppImage

./linuxdeploy-x86_64.AppImage --appdir AppDir -e /usr/bin/python3

## Create all needed extra folders in the AppDir (not created by linuxdeploy)
mkdir -p AppDir/opt/novelWriter
mkdir -p AppDir/usr/lib/python3/dist-packages

## Download SMath Release from SMath website and place the files in AppDir
wget https://github.com/vkbo/novelWriter/releases/download/v1.3.2/novelWriter-1.3.2-minimal-linux.zip
VERSION=$(ls novelWriter-* | head -1 | awk -F"-" '{print $2}')
echo $VERSION > AppDir/VERSION
unzip novelWriter*.zip -d AppDir/opt/novelWriter

## Create
sed -i 's/%%exec%%/novelwriter/g' AppDir/opt/novelWriter/setup/novelwriter.desktop

## Copy files from git-repo/Resources to AppDir
cp AppDir/opt/novelWriter/setup/icons/scaled/icon-novelwriter-16.png AppDir/usr/share/icons/hicolor/16x16/novelwriter.png
cp AppDir/opt/novelWriter/setup/icons/scaled/icon-novelwriter-32.png AppDir/usr/share/icons/hicolor/32x32/novelwriter.png
cp AppDir/opt/novelWriter/setup/icons/scaled/icon-novelwriter-64.png AppDir/usr/share/icons/hicolor/64x64/novelwriter.png
cp AppDir/opt/novelWriter/setup/icons/scaled/icon-novelwriter-128.png AppDir/usr/share/icons/hicolor/128x128/novelwriter.png
cp AppDir/opt/novelWriter/setup/icons/scaled/icon-novelwriter-256.png AppDir/usr/share/icons/hicolor/256x256/novelwriter.png
cp AppDir/opt/novelWriter/setup/icons/icon-novelwriter.svg AppDir/usr/share/icons/hicolor/scalable/novelwriter.svg
cp AppDir/opt/novelWriter/setup/icons/scaled/icon-novelwriter-256.png AppDir/novelwriter.png

echo "#!/bin/sh" > AppDir/usr/bin/novelwriter
echo 'LAUNCHER="$(readlink -f "${0}")"' >> AppDir/usr/bin/novelwriter
echo 'HERE="$(dirname "${LAUNCHER}")"' >> AppDir/usr/bin/novelwriter
echo "echo \${LAUNCHER}" >> AppDir/usr/bin/novelwriter
echo "echo \${HERE}" >> AppDir/usr/bin/novelwriter
echo "exec (PYTHONPATH=\${HERE}/../lib/python3/dist-packages/ \${HERE}/python3 \${HERE}/../../opt/novelWriter/novelWriter.py)" >> AppDir/usr/bin/novelwriter
chmod +x AppDir/usr/bin/novelwriter

## Copy libraries from host system (Github Actions Runner or local system) to AppDir
cp -r /usr/lib/python3.6 AppDir/usr/lib/
cp -r /usr/lib/python3/dist-packages/PyQt5 AppDir/usr/lib/python3/dist-packages
cp -r /usr/lib/python3/dist-packages/enchant AppDir/usr/lib/python3/dist-packages
cp -r /usr/lib/python3/dist-packages/lxml AppDir/usr/lib/python3/dist-packages

GLIBC=$(ldd --version | head -1 | awk '{print $5}')
ARCH=x86_64 VERSION=${VERSION}-glibc${GLIBC} ./linuxdeploy-x86_64.AppImage --appdir AppDir -d AppDir/opt/novelWriter/setup/novelwriter.desktop --output appimage 

mv novelWriter*.AppImage out/
rm -f *.zip
rm -f *.AppImage
